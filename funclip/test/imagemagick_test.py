from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.compositing import CompositeVideoClip

generator = lambda txt: TextClip(txt, font='./font/STHeitiMedium.ttc', fontsize=48, color='white')
subs = [((0, 2), 'sub1中文字幕'),
        ((2, 4), 'subs2'),
        ((4, 6), 'subs3'),
        ((6, 8), 'subs4')]

subtitles = SubtitlesClip(subs, generator)

video = VideoFileClip("examples/2022云栖大会_片段.mp4.mp4")
video = video.subclip(0, 8)
video = CompositeVideoClip([video, subtitles.set_pos(('center','bottom'))])

video.write_videofile("test_output.mp4")