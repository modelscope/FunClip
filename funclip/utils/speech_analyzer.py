#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import sys
import librosa
import numpy as np
import datetime
import argparse
from moviepy.editor import VideoFileClip, AudioFileClip


class SpeechAnalyzer:
    def __init__(self):
        self.frame_length = 2048
        self.silence_threshold = 20
        self._cached_audio = None
        self._cached_file = None
        self._cached_sr = None

    def _parse_timestamp(self, time_str: str) -> float:
        """将 00:00:13,580 格式的时间戳转换为秒数"""
        try:
            # 将逗号替换为点，以便解析毫秒
            time_str = time_str.replace(',', '.')
            time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S.%f')
            total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6
            return total_seconds
        except ValueError as e:
            raise ValueError(
                f"Invalid timestamp format: {time_str}. Expected format: HH:MM:SS,mmm") from e

    def _load_audio_file(self, file_path: str):
        """加载并缓存音频文件"""
        if self._cached_file != file_path:
            print(f"Loading audio file: {file_path}")
            try:
                # 首先尝试使用 librosa
                y, sr = librosa.load(file_path)
                self._cached_audio = y
                self._cached_sr = sr
            except Exception as e:
                print(f"Librosa loading failed: {str(e)}, trying moviepy...")
                # 如果失败，使用 moviepy
                is_video = file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
                if is_video:
                    with VideoFileClip(file_path) as video:
                        if video.audio is None:
                            raise ValueError("Video file has no audio track")
                        audio_data = video.audio.to_soundarray(fps=44100)
                else:
                    with AudioFileClip(file_path) as audio:
                        audio_data = audio.to_soundarray(fps=44100)

                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                self._cached_audio = audio_data
                self._cached_sr = 44100

            self._cached_file = file_path
            print(f"Audio loaded: shape={self._cached_audio.shape}, sr={self._cached_sr}")

    def analyze_segment(self, audio_data: np.ndarray, sr: int) -> dict:
        """分析单个音频片段的特征"""
        try:
            # 确保音频数据是正确的格式
            if audio_data is None or len(audio_data) == 0:
                raise ValueError("Empty audio data")

            # 转换为单声道
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # 确保数据是连续的 numpy 数组
            audio_data = np.ascontiguousarray(audio_data)

            # 语调分析
            try:
                f0, voiced_flag, _ = librosa.pyin(audio_data,
                                                  fmin=librosa.note_to_hz('C2'),
                                                  fmax=librosa.note_to_hz('C7'),
                                                  sr=sr)
                f0_mean = np.nanmean(f0[voiced_flag]) if any(voiced_flag) else 0
                f0_std = np.nanstd(f0[voiced_flag]) if any(voiced_flag) else 0
            except Exception as e:
                print(f"Warning: Pitch analysis failed: {str(e)}", file=sys.stderr)
                f0_mean = 0
                f0_std = 0

            # 音量分析
            try:
                # 确保数据是浮点型
                audio_data = audio_data.astype(np.float32)

                # RMS值计算
                rms = librosa.feature.rms(y=audio_data, frame_length=self.frame_length)[0]
                rms_db = librosa.amplitude_to_db(rms, ref=np.max)
                rms_mean = np.mean(rms)
                rms_db_mean = np.mean(rms_db)

                # 简单平均值
                abs_mean = np.mean(np.abs(audio_data))
                abs_mean_db = librosa.amplitude_to_db(abs_mean, ref=np.max)
            except Exception as e:
                print(f"Warning: Volume analysis failed: {str(e)}", file=sys.stderr)
                rms_mean = 0
                rms_db_mean = float('-inf')
                abs_mean = 0
                abs_mean_db = float('-inf')

            return {
                "pitch": {
                    "mean": round(f0_mean, 1),
                    "std": round(f0_std, 1)
                },
                "volume": {
                    "rms_linear": round(rms_mean, 4),
                    "rms_db": round(rms_db_mean, 1),
                    "mean_linear": round(abs_mean, 4),
                    "mean_db": round(abs_mean_db, 1)
                }
            }
        except Exception as e:
            print(f"Error in analyze_segment: {str(e)}", file=sys.stderr)
            return {
                "error": f"Analysis failed: {str(e)}",
                "pitch": {"mean": 0, "std": 0},
                "volume": {
                    "rms_linear": 0,
                    "rms_db": float('-inf'),
                    "mean_linear": 0,
                    "mean_db": float('-inf')
                }
            }

    def analyze_file_segments(self, file_path: str, time_ranges: list) -> list:
        """分析文件的多个时间段"""
        try:
            print(f"Starting analysis for file: {file_path}")
            print(f"Time ranges to analyze: {time_ranges}")

            # 加载音频文件（如果未缓存）
            self._load_audio_file(file_path)

            results = []
            for start_time, end_time in time_ranges:
                print(f"\nAnalyzing segment: {start_time} - {end_time}")
                try:
                    # 转换时间戳为秒
                    start_sec = self._parse_timestamp(start_time)
                    end_sec = self._parse_timestamp(end_time)
                    print(f"Converted to seconds: {start_sec}s - {end_sec}s")

                    # 提取时间段
                    start_idx = int(start_sec * self._cached_sr)
                    end_idx = int(end_sec * self._cached_sr)
                    print(f"Audio indices: {start_idx} - {end_idx}")
                    print(f"Total audio length: {len(self._cached_audio)}")

                    segment = self._cached_audio[start_idx:end_idx]
                    print(f"Extracted segment length: {len(segment)}")

                    # 分析片段
                    result = self.analyze_segment(segment, self._cached_sr)
                    result["time_range"] = {"start": start_time, "end": end_time}
                    results.append(result)
                    print(f"Analysis complete for this segment")

                except Exception as e:
                    print(f"Error analyzing segment: {str(e)}")
                    results.append({
                        "error": f"Failed to analyze segment {start_time}-{end_time}: {str(e)}",
                        "time_range": {"start": start_time, "end": end_time}
                    })

            print(f"\nAll segments analyzed. Results: {results}")
            return results

        except Exception as e:
            print(f"Fatal error in analyze_file_segments: {str(e)}")
            return [{
                "error": f"Analysis failed: {str(e)}",
                "time_ranges": time_ranges
            }]


def format_analysis_results(results: list) -> str:
    """格式化多个分析结果为易读的字符串"""
    output = []
    for i, result in enumerate(results, 1):
        if "error" in result:
            output.append(
                f"\n片段 {i} ({result.get('time_range', {}).get('start', '')} - {result.get('time_range', {}).get('end', '')}):")
            output.append(f"错误: {result['error']}")
            continue

        output.append(
            f"\n片段 {i} ({result['time_range']['start']} - {result['time_range']['end']}):")
        output.append("语调:")
        output.append(f"  均值: {result['pitch']['mean']}Hz")
        output.append(f"  波动: {result['pitch']['std']}Hz (标准差)")
        output.append("\n音量:")
        output.append(
            f"  RMS: {result['volume']['rms_db']}dB (线性值: {result['volume']['rms_linear']})")
        output.append(
            f"  平均: {result['volume']['mean_db']}dB (线性值: {result['volume']['mean_linear']})")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='音频特征分析工具')
    parser.add_argument('file_path', help='视频或音频文件路径')
    parser.add_argument('-t', '--times', nargs='+', required=True,
                        help='时间点列表，格式: "00:00:13,580-00:00:15,900" "00:01:20,000-00:01:25,000" ...')
    parser.add_argument('--json', action='store_true', help='以JSON格式输出')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')

    args = parser.parse_args()

    try:
        print(f"Input file: {args.file_path}")
        print(f"Time ranges: {args.times}")

        # 解析时间范围
        time_ranges = []
        for time_str in args.times:
            start, end = time_str.split('-')
            time_ranges.append((start.strip(), end.strip()))

        print(f"Parsed time ranges: {time_ranges}")

        analyzer = SpeechAnalyzer()
        results = analyzer.analyze_file_segments(args.file_path, time_ranges)

        if args.json:
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(format_analysis_results(results))

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
