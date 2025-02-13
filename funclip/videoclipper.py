#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

import re
import os
import sys
import copy
import librosa
import logging
import argparse
import numpy as np
import soundfile as sf
from moviepy.editor import *
import moviepy.editor as mpy
from moviepy.video.tools.subtitles import SubtitlesClip
from utils.subtitle_utils import generate_srt, generate_srt_clip
from utils.argparse_tools import ArgumentParser, get_commandline_args
from utils.trans_utils import pre_proc, proc, write_state, load_state, proc_spk, convert_pcm_to_float


class VideoClipper():
    def __init__(self, funasr_model):
        logging.warning("Initializing VideoClipper.")
        self.funasr_model = funasr_model
        self.GLOBAL_COUNT = 0

    def recog(self, audio_input, sd_switch='no', state=None, hotwords="", output_dir=None):
        if state is None:
            state = {}
        sr, data = audio_input

        # Convert to float64 consistently (includes data type checking)
        data = convert_pcm_to_float(data)

        # assert sr == 16000, "16kHz sample rate required, {} given.".format(sr)
        if sr != 16000: # resample with librosa
            data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        if len(data.shape) == 2:  # multi-channel wav input
            logging.warning("Input wav shape: {}, only first channel reserved.".format(data.shape))
            data = data[:,0]
        state['audio_input'] = (sr, data)
        if sd_switch == 'Yes':
            rec_result = self.funasr_model.generate(data, return_raw_text=True, is_final=True, hotword=hotwords, cache={})
            res_srt = generate_srt(rec_result[0]['sentence_info'])
            state['sd_sentences'] = rec_result[0]['sentence_info']
        else:
            rec_result = self.funasr_model.generate(data, 
                                                    return_spk_res=False, 
                                                    sentence_timestamp=True, 
                                                    return_raw_text=True, 
                                                    is_final=True, 
                                                    hotword=hotwords,
                                                    output_dir=output_dir,
                                                    cache={})
            res_srt = generate_srt(rec_result[0]['sentence_info'])
        state['recog_res_raw'] = rec_result[0]['raw_text']
        state['timestamp'] = rec_result[0]['timestamp']
        state['sentences'] = rec_result[0]['sentence_info']
        res_text = rec_result[0]['text']
        return res_text, res_srt, state

    def clip(self, dest_text, start_ost, end_ost, state, dest_spk=None, output_dir=None, timestamp_list=None):
        # get from state
        audio_input = state['audio_input']
        recog_res_raw = state['recog_res_raw']
        timestamp = state['timestamp']
        sentences = state['sentences']
        sr, data = audio_input
        data = data.astype(np.float64)

        if timestamp_list is not None:
            all_ts = []
            if dest_spk is None or dest_spk == '' or 'sd_sentences' not in state:
                for _dest_text in dest_text.split('#'):
                    if '[' in _dest_text:
                        match = re.search(r'\[(\d+),\s*(\d+)\]', _dest_text)
                        if match:
                            offset_b, offset_e = map(int, match.groups())
                            log_append = ""
                        else:
                            offset_b, offset_e = 0, 0
                            log_append = "(Bracket detected in dest_text but offset time matching failed)"
                        _dest_text = _dest_text[:_dest_text.find('[')]
                    else:
                        log_append = ""
                        offset_b, offset_e = 0, 0
                    _dest_text = pre_proc(_dest_text)
                    ts = proc(recog_res_raw, timestamp, _dest_text)
                    for _ts in ts: all_ts.append([_ts[0]+offset_b*16, _ts[1]+offset_e*16])
                    if len(ts) > 1 and match:
                        log_append += '(offsets detected but No.{} sub-sentence matched to {} periods in audio, \
                            offsets are applied to all periods)'
            else:
                for _dest_spk in dest_spk.split('#'):
                    ts = proc_spk(_dest_spk, state['sd_sentences'])
                    for _ts in ts: all_ts.append(_ts)
                log_append = ""
        else:
            all_ts = timestamp_list
        ts = all_ts
        # ts.sort()
        srt_index = 0
        clip_srt = ""
        if len(ts):
            start, end = ts[0]
            start = min(max(0, start+start_ost*16), len(data))
            end = min(max(0, end+end_ost*16), len(data))
            res_audio = data[start:end]
            start_end_info = "from {} to {}".format(start/16000, end/16000)
            srt_clip, _, srt_index = generate_srt_clip(sentences, start/16000.0, end/16000.0, begin_index=srt_index)
            clip_srt += srt_clip
            for _ts in ts[1:]:  # multiple sentence input or multiple output matched
                start, end = _ts
                start = min(max(0, start+start_ost*16), len(data))
                end = min(max(0, end+end_ost*16), len(data))
                start_end_info += ", from {} to {}".format(start, end)
                res_audio = np.concatenate([res_audio, data[start+start_ost*16:end+end_ost*16]], -1)
                srt_clip, _, srt_index = generate_srt_clip(sentences, start/16000.0, end/16000.0, begin_index=srt_index-1)
                clip_srt += srt_clip
        if len(ts):
            message = "{} periods found in the speech: ".format(len(ts)) + start_end_info + log_append
        else:
            message = "No period found in the speech, return raw speech. You may check the recognition result and try other destination text."
            res_audio = data
        return (sr, res_audio), message, clip_srt

    def video_recog(self, video_filename, sd_switch='no', hotwords="", output_dir=None):
        video = mpy.VideoFileClip(video_filename)
        # Extract the base name, add '_clip.mp4', and 'wav'
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)
            _, base_name = os.path.split(video_filename)
            base_name, _ = os.path.splitext(base_name)
            clip_video_file = base_name + '_clip.mp4'
            audio_file = base_name + '.wav'
            audio_file = os.path.join(output_dir, audio_file)
        else:
            base_name, _ = os.path.splitext(video_filename)
            clip_video_file = base_name + '_clip.mp4'
            audio_file = base_name + '.wav'
        video.audio.write_audiofile(audio_file)
        wav = librosa.load(audio_file, sr=16000)[0]
        # delete the audio file after processing
        if os.path.exists(audio_file):
            os.remove(audio_file)
        state = {
            'video_filename': video_filename,
            'clip_video_file': clip_video_file,
            'video': video,
        }
        # res_text, res_srt = self.recog((16000, wav), state)
        return self.recog((16000, wav), sd_switch, state, hotwords, output_dir)

    def video_clip(self, 
                   dest_text, 
                   start_ost, 
                   end_ost, 
                   state, 
                   font_size=32, 
                   font_color='white', 
                   add_sub=False, 
                   dest_spk=None, 
                   output_dir=None,
                   timestamp_list=None):
        # get from state
        recog_res_raw = state['recog_res_raw']
        timestamp = state['timestamp']
        sentences = state['sentences']
        video = state['video']
        clip_video_file = state['clip_video_file']


        # 确保输出目录存在
        if output_dir is None or output_dir.strip() == "":
            output_dir = "./output"  # 设置默认输出目录
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # 获取时间戳
        if timestamp_list is not None:
            all_ts = [[i[0]*16.0, i[1]*16.0] for i in timestamp_list]
        else:
            all_ts = []
            if dest_spk is None or dest_spk == '' or 'sd_sentences' not in state:
                for _dest_text in dest_text.split('#'):
                    if '[' in _dest_text:
                        match = re.search(r'\[(\d+),\s*(\d+)\]', _dest_text)
                        if match:
                            offset_b, offset_e = map(int, match.groups())
                            log_append = ""
                        else:
                            offset_b, offset_e = 0, 0
                            log_append = "(Bracket detected in dest_text but offset time matching failed)"
                        _dest_text = _dest_text[:_dest_text.find('[')]
                    else:
                        offset_b, offset_e = 0, 0
                        log_append = ""
                    _dest_text = pre_proc(_dest_text)
                    ts = proc(recog_res_raw, timestamp, _dest_text)
                    for _ts in ts: all_ts.append([_ts[0]+offset_b*16, _ts[1]+offset_e*16])
            else:
                for _dest_spk in dest_spk.split('#'):
                    ts = proc_spk(_dest_spk, state['sd_sentences'])
                    for _ts in ts: all_ts.append(_ts)
        
        ts = all_ts  # 使用处理后的时间戳列表
        
        if len(ts):
            clips = []
            segment_files = []
            clip_srt = ""
            srt_index = 0
            
            message = f"Processing {len(ts)} segments"
            
            for i, _ts in enumerate(ts):
                start, end = _ts[0] / 16000, _ts[1] / 16000
                start, end = start+start_ost/1000.0, end+end_ost/1000.0
                message += f"\nSegment {i+1}: {start:.2f}s - {end:.2f}s"
                
                video_clip = video.subclip(start, end)
                if add_sub:
                    srt_clip, subs, srt_index = generate_srt_clip(sentences, start, end, 
                        begin_index=srt_index-1 if i > 0 else srt_index)
                    generator = lambda txt: TextClip(txt, font='./font/STHeitiMedium.ttc', 
                        fontsize=font_size, color=font_color)
                    subtitles = SubtitlesClip(subs, generator)
                    video_clip = CompositeVideoClip([video_clip, 
                        subtitles.set_pos(('center','bottom'))])
                    clip_srt += srt_clip
                
                # 保存分段视频
                segment_file = os.path.join(output_dir, 
                    f"{os.path.splitext(os.path.basename(clip_video_file))[0]}_seg{i}_no{self.GLOBAL_COUNT}.mp4")
                video_clip.write_videofile(segment_file, audio_codec="aac")
                segment_files.append(segment_file)
                
                clips.append(video_clip)

            # 生成合成视频
            final_clip = concatenate_videoclips(clips)
            combined_file = os.path.join(output_dir, 
                f"{os.path.splitext(os.path.basename(clip_video_file))[0]}_combined_no{self.GLOBAL_COUNT}.mp4")
            final_clip.write_videofile(combined_file, audio_codec="aac")
            
            self.GLOBAL_COUNT += 1
            message += "\nGenerated segment and combined video files"
            
            return segment_files, combined_file, message, clip_srt
        else:
            message = "No period found in the speech, return raw video."
            return [], clip_video_file, message, ""


def get_parser():
    parser = ArgumentParser(
        description="ClipVideo Argument",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=(1, 2),
        help="Stage, 0 for recognizing and 1 for clipping",
        required=True
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Input file path",
        required=True
    )
    parser.add_argument(
        "--sd_switch",
        type=str,
        choices=("no", "yes"),
        default="no",
        help="Turn on the speaker diarization or not",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default='./output',
        help="Output files path",
    )
    parser.add_argument(
        "--dest_text",
        type=str,
        default=None,
        help="Destination text string for clipping",
    )
    parser.add_argument(
        "--dest_spk",
        type=str,
        default=None,
        help="Destination spk id for clipping",
    )
    parser.add_argument(
        "--start_ost",
        type=int,
        default=0,
        help="Offset time in ms at beginning for clipping"
    )
    parser.add_argument(
        "--end_ost",
        type=int,
        default=0,
        help="Offset time in ms at ending for clipping"
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="Output file path"
    )
    return parser


def runner(stage, file, sd_switch, output_dir, dest_text, dest_spk, start_ost, end_ost, output_file, config=None):
    audio_suffixs = ['.wav','.mp3','.aac','.m4a','.flac']
    video_suffixs = ['.mp4','.avi','.mkv','.flv','.mov','.webm','.ts','.mpeg']
    _,ext = os.path.splitext(file)
    if ext.lower() in audio_suffixs:
        mode = 'audio'
    elif ext.lower() in video_suffixs:
        mode = 'video'
    else:
        logging.error("Unsupported file format: {}\n\nplease choise one of the following: {}".format(file),audio_suffixs+video_suffixs)
        sys.exit(1) # exit if the file is not supported
    while output_dir.endswith('/'):
        output_dir = output_dir[:-1]
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if stage == 1:
        from funasr import AutoModel
        # initialize funasr automodel
        logging.warning("Initializing modelscope asr pipeline.")
        funasr_model = AutoModel(model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                  vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                  punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                  spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
                  )
        audio_clipper = VideoClipper(funasr_model)
        if mode == 'audio':
            logging.warning("Recognizing audio file: {}".format(file))
            wav, sr = librosa.load(file, sr=16000)
            res_text, res_srt, state = audio_clipper.recog((sr, wav), sd_switch)
        if mode == 'video':
            logging.warning("Recognizing video file: {}".format(file))
            res_text, res_srt, state = audio_clipper.video_recog(file, sd_switch)
        total_srt_file = output_dir + '/total.srt'
        with open(total_srt_file, 'w') as fout:
            fout.write(res_srt)
            logging.warning("Write total subtitle to {}".format(total_srt_file))
        write_state(output_dir, state)
        logging.warning("Recognition successed. You can copy the text segment from below and use stage 2.")
        print(res_text)
    if stage == 2:
        audio_clipper = VideoClipper(None)
        if mode == 'audio':
            state = load_state(output_dir)
            wav, sr = librosa.load(file, sr=16000)
            state['audio_input'] = (sr, wav)
            (sr, audio), message, srt_clip = audio_clipper.clip(dest_text, start_ost, end_ost, state, dest_spk=dest_spk)
            if output_file is None:
                output_file = output_dir + '/result.wav'
            clip_srt_file = output_file[:-3] + 'srt'
            logging.warning(message)
            sf.write(output_file, audio, 16000)
            assert output_file.endswith('.wav'), "output_file must ends with '.wav'"
            logging.warning("Save clipped wav file to {}".format(output_file))
            with open(clip_srt_file, 'w') as fout:
                fout.write(srt_clip)
                logging.warning("Write clipped subtitle to {}".format(clip_srt_file))
        if mode == 'video':
            state = load_state(output_dir)
            state['video_filename'] = file
            if output_file is None:
                state['clip_video_file'] = file[:-4] + '_clip.mp4'
            else:
                state['clip_video_file'] = output_file
            clip_srt_file = state['clip_video_file'][:-3] + 'srt'
            state['video'] = mpy.VideoFileClip(file)
            segment_files, combined_file, message, srt_clip = audio_clipper.video_clip(dest_text, start_ost, end_ost, state, dest_spk=dest_spk)
            logging.warning("Clipping Log: {}".format(message))
            logging.warning("Save clipped mp4 file to {}".format(combined_file))
            with open(clip_srt_file, 'w') as fout:
                fout.write(srt_clip)
                logging.warning("Write clipped subtitle to {}".format(clip_srt_file))


def main(cmd=None):
    print(get_commandline_args(), file=sys.stderr)
    parser = get_parser()
    args = parser.parse_args(cmd)
    kwargs = vars(args)
    runner(**kwargs)


if __name__ == '__main__':
    main()