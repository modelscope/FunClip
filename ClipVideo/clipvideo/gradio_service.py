import gradio as gr
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from videoclipper import VideoClipper


if __name__ == "__main__":
    inference_pipeline = pipeline(
        task=Tasks.auto_speech_recognition,
        model='damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
        vad_model='damo/speech_fsmn_vad_zh-cn-16k-common-pytorch',
        punc_model='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
    )
    audio_clipper = VideoClipper(inference_pipeline)

    def audio_recog(audio_input):
        return audio_clipper.recog(audio_input)

    def audio_clip(dest_text, start_ost, end_ost, state):
        return audio_clipper.clip(dest_text, start_ost, end_ost, state)

    def video_recog(video_input):
        return audio_clipper.video_recog(video_input)

    def video_clip(dest_text, start_ost, end_ost, state):
        return audio_clipper.video_clip(dest_text, start_ost, end_ost, state)

    def video_clip_addsub(dest_text, start_ost, end_ost, state, font_size, font_color):
        return audio_clipper.video_clip(dest_text, start_ost, end_ost, state, font_size, font_color, add_sub=True)

    '''
    top_md_1 = ("""
    基于达摩院自研Paraformer-长音频版的语音识别、端点检测、标点预测、时间戳功能

    准确识别，自由复制所需段落并一键裁剪、添加字幕

    * Step1: 上传视频文件（或使用下方的用例体验），点击 **<font color="#f7802b">识别</font>** 按钮
    * Step2: 复制识别结果中所需的文字至右上方，设置偏移与字幕配置（可选）
    * Step3: 点击 **<font color="#f7802b">裁剪</font>** 按钮或 **<font color="#f7802b">裁剪并添加字幕</font>** 按钮获得结果
    """)
    '''

    top_md_2 = ("""
    受到网络传输与服务资源的限制，用于体验的视频最好大小在40mb以下
    过大的视频可以尝试分离音轨使用音频剪辑，或 **<font color="#1785c4">通过源代码将您的ClipVideo服务部署在本地（推荐）</font>** ：
    <div align="center">
    <div style="display:flex; gap: 0.25rem;" align="center">
    FunASR_APP: <a href='https://github.com/alibaba/funasr-app'><img src='https://img.shields.io/badge/Github-Code-blue'></a> 
    🌟支持我们: <a href='https://github.com/alibaba/funasr-app/stargazers'><img src='https://img.shields.io/github/stars/alibaba/funasr-app.svg?style=social'></a>
    </div>
    </div>
    """)

    top_md_3 = ("""访问FunASR项目与论文能够帮助您深入了解ClipVideo中所使用的语音处理相关模型：
    <div align="center">
    <div style="display:flex; gap: 0.25rem;" align="center">
        FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR'><img src='https://img.shields.io/badge/Github-Code-blue'></a> 
        FunASR Paper: <a href="https://arxiv.org/abs/2305.11013"><img src="https://img.shields.io/badge/Arxiv-2305.11013-orange"></a> 
        🌟Star FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR/stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunASR.svg?style=social'></a>
    </div>
    </div>
    """)

    # gradio interface
    with gr.Blocks() as demo:
        #gr.Image("./examples/guide.png", show_label=False)
        # gr.Markdown(top_md_1)
        #gr.Markdown(top_md_2)
        #gr.Markdown(top_md_3)
        video_state = gr.State()
        audio_state = gr.State()
        with gr.Tab("🎥✂️视频裁剪 Video Clipping"):
            with gr.Row():
                with gr.Column():
                    video_input = gr.Video(label="🎥视频输入 Video Input")
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81%E5%A4%9A%E8%AF%BB%E4%B9%A6%EF%BC%9F%E8%BF%99%E6%98%AF%E6%88%91%E5%90%AC%E8%BF%87%E6%9C%80%E5%A5%BD%E7%9A%84%E7%AD%94%E6%A1%88-%E7%89%87%E6%AE%B5.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/2022%E4%BA%91%E6%A0%96%E5%A4%A7%E4%BC%9A_%E7%89%87%E6%AE%B5.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/2022%E4%BA%91%E6%A0%96%E5%A4%A7%E4%BC%9A_%E7%89%87%E6%AE%B52.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E4%BD%BF%E7%94%A8chatgpt_%E7%89%87%E6%AE%B5.mp4'],
                                [video_input])
                    recog_button2 = gr.Button("👂识别 Recognize")
                    video_text_output = gr.Textbox(label="✏️识别结果 Recognition Result")
                    video_srt_output = gr.Textbox(label="📖SRT字幕内容 RST Subtitles")
                with gr.Column():
                    video_text_input = gr.Textbox(label="✏️待裁剪文本 Text to Clip (多段文本使用'#'连接)")
                    with gr.Row():
                        video_start_ost = gr.Slider(minimum=-500, maximum=1000, value=0, step=50, label="⏪开始位置偏移 Start Offset (ms)")
                        video_end_ost = gr.Slider(minimum=-500, maximum=1000, value=100, step=50, label="⏩结束位置偏移 End Offset (ms)")
                    with gr.Row():
                        font_size = gr.Slider(minimum=10, maximum=100, value=32, step=2, label="🔠字幕字体大小 Subtitle Font Size")
                        font_color = gr.Radio(["black", "white", "green", "red"], label="🌈字幕颜色 Subtitle Color", value='white')
                        # font = gr.Radio(["黑体", "Alibaba Sans"], label="字体 Font")
                    with gr.Row():
                        clip_button2 = gr.Button("✂️裁剪\nClip")
                        clip_button3 = gr.Button("✂️裁剪并添加字幕\nClip and Generate Subtitles")
                    video_output = gr.Video(label="🎥裁剪结果 Audio Clipped")
                    video_mess_output = gr.Textbox(label="ℹ️裁剪信息 Clipping Log")
                    video_srt_clip_output = gr.Textbox(label="📖裁剪部分SRT字幕内容 Clipped RST Subtitles")

        with gr.Tab("🔊✂️音频裁剪 Audio Clipping"):
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(label="🔊音频输入 Audio Input")
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E9%B2%81%E8%82%83%E9%87%87%E8%AE%BF%E7%89%87%E6%AE%B51.wav'], [audio_input])
                    recog_button1 = gr.Button("👂识别 Recognize")
                    audio_text_output = gr.Textbox(label="✏️识别结果 Recognition Result")
                    audio_srt_output = gr.Textbox(label="📖SRT字幕内容 RST Subtitles")
                with gr.Column():
                    audio_text_input = gr.Textbox(label="✏️待裁剪文本 Text to Clip (多段文本使用'#'连接)")
                    with gr.Row():
                        audio_start_ost = gr.Slider(minimum=-500, maximum=1000, value=0, step=50, label="⏪开始位置偏移 Start Offset (ms)")
                        audio_end_ost = gr.Slider(minimum=-500, maximum=1000, value=100, step=50, label="⏩结束位置偏移 End Offset (ms)")
                    with gr.Row():
                        clip_button1 = gr.Button("✂️裁剪 Clip")
                    audio_output = gr.Audio(label="🔊裁剪结果 Audio Clipped")
                    audio_mess_output = gr.Textbox(label="ℹ️裁剪信息 Clipping Log")
                    audio_srt_clip_output = gr.Textbox(label="📖裁剪部分SRT字幕内容 Clipped RST Subtitles")
        
        recog_button1.click(audio_recog, 
                            inputs=audio_input, 
                            outputs=[audio_text_output, audio_srt_output, audio_state])
        clip_button1.click(audio_clip, 
                           inputs=[audio_text_input, audio_start_ost, audio_end_ost, audio_state], 
                           outputs=[audio_output, audio_mess_output, audio_srt_clip_output])

        recog_button2.click(video_recog, 
                            inputs=video_input, 
                            outputs=[video_text_output, video_srt_output, video_state])
        clip_button2.click(video_clip, 
                           inputs=[video_text_input, video_start_ost, video_end_ost, video_state], 
                           outputs=[video_output, video_mess_output, video_srt_clip_output])
        clip_button3.click(video_clip_addsub, 
                           inputs=[video_text_input, video_start_ost, video_end_ost, video_state, font_size, font_color], 
                           outputs=[video_output, video_mess_output, video_srt_clip_output])
    
    # start gradio service in local
    demo.queue(concurrency_count=3).launch()
