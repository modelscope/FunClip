import argparse
import subprocess
import re
from datetime import datetime

def srt_time_to_ffmpeg(srt_time):
    """ 将 SRT 格式的时间 (00:00:13,580) 转换为 FFmpeg 格式 (00:00:13.580) """
    return srt_time.replace(',', '.')

def calculate_duration(start_time, end_time):
    """ 计算持续时间（秒） """
    time_format = "%H:%M:%S.%f"
    start_dt = datetime.strptime(srt_time_to_ffmpeg(start_time), time_format)
    end_dt = datetime.strptime(srt_time_to_ffmpeg(end_time), time_format)
    duration = (end_dt - start_dt).total_seconds()
    return str(max(duration, 1))  # 确保 duration 至少 1 秒

def get_mean_volume(input_file, start_time, end_time):
    """ 计算指定时间段的 RMS 音量 """
    ffmpeg_start_time = srt_time_to_ffmpeg(start_time)
    duration = calculate_duration(start_time, end_time)

    cmd = [
        "ffmpeg", "-i", input_file, "-ss", ffmpeg_start_time, "-t", duration,
        "-af", "volumedetect", "-f", "null", "/dev/null"
    ]

    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

    # 使用正则提取 mean_volume 数值
    match = re.search(r"mean_volume:\s(-?\d+\.\d+)", result.stderr)
    if match:
        print(match.group(1))  # 只输出数值
    else:
        print("未找到均方根音量，请检查音频是否为空或 FFmpeg 版本是否兼容。")

# 解析命令行参数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="计算音频特定时间段的均方根音量 (RMS Volume)")
    parser.add_argument("input_file", help="输入音频文件路径")
    parser.add_argument("start_time", help="起始时间（格式：00:00:13,580）")
    parser.add_argument("end_time", help="结束时间（格式：00:00:14,100）")

    args = parser.parse_args()
    get_mean_volume(args.input_file, args.start_time, args.end_time)