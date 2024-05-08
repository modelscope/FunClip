import os
import gradio as gr
from funasr import AutoModel
from videoclipper import VideoClipper
from introduction import top_md_1, top_md_2, top_md_3


if __name__ == "__main__":
    funasr_model = AutoModel(model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                             vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                             punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                             spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
                            )
    audio_clipper = VideoClipper(funasr_model)

    def audio_recog(audio_input, sd_switch, hotwords, output_dir):
        return audio_clipper.recog(audio_input, sd_switch, hotwords, output_dir=output_dir)

    def video_recog(video_input, sd_switch, hotwords, output_dir):
        return audio_clipper.video_recog(video_input, sd_switch, hotwords, output_dir=output_dir)

    def video_clip(dest_text, video_spk_input, start_ost, end_ost, state, output_dir):
        return audio_clipper.video_clip(
            dest_text, start_ost, end_ost, state, dest_spk=video_spk_input, output_dir=output_dir
            )

    def mix_recog(video_input, audio_input, sd_switch, hotwords, output_dir):
        # output_dir here is for funasr model generate
        # both relative and absolute paths are OK
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        audio_state, video_state = None, None
        if video_input is not None:
            res_text, res_srt, video_state = video_recog(
                video_input, sd_switch, hotwords, output_dir=output_dir)
            return res_text, res_srt, video_state, None
        if audio_input is not None:
            res_text, res_srt, audio_state = audio_recog(
                audio_input, sd_switch, hotwords, output_dir=output_dir)
            return res_text, res_srt, None, audio_state
    
    def mix_clip(dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        # output_dir here is for moviepy, vedio saving
        # supposed to be absolute path only
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, dest_spk=video_spk_input, output_dir=output_dir)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, dest_spk=video_spk_input, output_dir=output_dir)
            return None, (sr, res_audio), message, clip_srt
    
    def video_clip_addsub(dest_text, video_spk_input, start_ost, end_ost, state, output_dir, font_size, font_color):
        return audio_clipper.video_clip(
            dest_text, start_ost, end_ost, state, 
            font_size=font_size, font_color=font_color, 
            add_sub=True, dest_spk=video_spk_input, output_dir=output_dir
            )

    # gradio interface
    with gr.Blocks() as funclip_service:
        gr.Markdown(top_md_1)
        gr.Markdown(top_md_2)
        gr.Markdown(top_md_3)
        video_state, audio_state = gr.State(), gr.State()
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    video_input = gr.Video(label="🎥视频输入 Video Input")
                    audio_input = gr.Audio(label="🔊音频输入 Audio Input")
                with gr.Column():
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81%E5%A4%9A%E8%AF%BB%E4%B9%A6%EF%BC%9F%E8%BF%99%E6%98%AF%E6%88%91%E5%90%AC%E8%BF%87%E6%9C%80%E5%A5%BD%E7%9A%84%E7%AD%94%E6%A1%88-%E7%89%87%E6%AE%B5.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/2022%E4%BA%91%E6%A0%96%E5%A4%A7%E4%BC%9A_%E7%89%87%E6%AE%B52.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E4%BD%BF%E7%94%A8chatgpt_%E7%89%87%E6%AE%B5.mp4'],
                                [video_input],
                                label='示例视频 Demo Video')
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E8%AE%BF%E8%B0%88.mp4'],
                                [video_input],
                                label='多说话人示例视频 Multi-speaker Demo Video')
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E9%B2%81%E8%82%83%E9%87%87%E8%AE%BF%E7%89%87%E6%AE%B51.wav'],
                                [audio_input],
                                label="示例音频 Demo Audio")
                    with gr.Column():
                        with gr.Row():
                            video_sd_switch = gr.Radio(["No", "Yes"], label="👥是否区分说话人 Recognize Speakers", value='No')
                            hotwords_input = gr.Textbox(label="🚒热词 Hotwords")
                        output_dir = gr.Textbox(label="文件输出路径 File Output Dir", value=" ")
                        recog_button = gr.Button("👂识别 Recognize")
                video_text_output = gr.Textbox(label="✏️识别结果 Recognition Result")
                video_srt_output = gr.Textbox(label="📖SRT字幕内容 RST Subtitles")
            with gr.Column():
                video_text_input = gr.Textbox(label="✏️待裁剪文本 Text to Clip (多段文本使用'#'连接)")
                video_spk_input = gr.Textbox(label="✏️待裁剪说话人 Speaker to Clip (多个说话人使用'#'连接)")
                with gr.Row():
                    video_start_ost = gr.Slider(minimum=-500, maximum=1000, value=0, step=50, label="⏪开始位置偏移 Start Offset (ms)")
                    video_end_ost = gr.Slider(minimum=-500, maximum=1000, value=100, step=50, label="⏩结束位置偏移 End Offset (ms)")
                with gr.Row():
                    font_size = gr.Slider(minimum=10, maximum=100, value=32, step=2, label="🔠字幕字体大小 Subtitle Font Size")
                    font_color = gr.Radio(["black", "white", "green", "red"], label="🌈字幕颜色 Subtitle Color", value='white')
                    # font = gr.Radio(["黑体", "Alibaba Sans"], label="字体 Font")
                with gr.Row():
                    clip_button = gr.Button("✂️裁剪\nClip")
                    clip_subti_button = gr.Button("✂️裁剪+字幕\nClip+Subtitles")
                video_output = gr.Video(label="🎥裁剪结果 Video Clipped")
                audio_output = gr.Audio(label="🔊裁剪结果 Audio Clipped")
                clip_message = gr.Textbox(label="ℹ️裁剪信息 Clipping Log")
                srt_clipped = gr.Textbox(label="📖裁剪部分SRT字幕内容 Clipped RST Subtitles")
                
        recog_button.click(mix_recog, 
                            inputs=[video_input, 
                                    audio_input, 
                                    video_sd_switch, 
                                    hotwords_input, 
                                    output_dir,
                                    ], 
                            outputs=[video_text_output, video_srt_output, video_state, audio_state])
        clip_button.click(mix_clip, 
                           inputs=[video_text_input, 
                                   video_spk_input, 
                                   video_start_ost, 
                                   video_end_ost, 
                                   video_state, 
                                   audio_state, 
                                   output_dir
                                   ],
                           outputs=[video_output, audio_output, clip_message, srt_clipped])
        clip_subti_button.click(video_clip_addsub, 
                           inputs=[video_text_input, 
                                   video_spk_input, 
                                   video_start_ost, 
                                   video_end_ost, 
                                   video_state, 
                                   output_dir, 
                                   font_size, 
                                   font_color,
                                   ], 
                           outputs=[video_output, clip_message, srt_clipped])
    
    # start gradio service in local
    funclip_service.launch()
