# <p align="center"> FunClip🎥</p>

**<p align="center"> ⚡ Open-source, accurate and easy-to-use video clipping tool ⚡ </p>**

<p align="center"> <img src="docs/images/interface.jpg" width=444/></p>

### <p align="center">「[简体中文](./README.md) | English」</p>

<div align="center">  
<h4>
<a href="#What's New"> What's New </a>
｜<a href="#On Going"> On Going </a>
｜<a href="#Install"> Install </a>
｜<a href="#Usage"> Usage </a>
｜<a href="#Community"> Community </a>
</h4>
</div>

**FunClip** is a fully open-source, locally deployed automated video clipping tool. It leverages Alibaba TONGYI speech lab's open-source [FunASR](https://github.com/alibaba-damo-academy/FunASR) Paraformer series models to perform speech recognition on videos. Then, users can freely choose text segments or speakers from the recognition results and click the clip button to obtain the video corresponding to the selected segments ([Quick Experience](https://modelscope.cn/studios/iic/funasr_app_clipvideo/summary)).

On top of the basic features mentioned above, FunClip has following highlights:

- Try AI clipping using LLM in FunClip now.
- FunClip integrates Alibaba's open-source industrial-grade model [Paraformer-Large](https://modelscope.cn/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/summary), which is one of the best-performing open-source Chinese ASR models available, with over 13 million downloads on Modelscope. It can also accurately predict timestamps in an integrated manner.
- FunClip incorporates the hotword customization feature of [SeACo-Paraformer](https://modelscope.cn/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/summary), allowing users to specify certain entity words, names, etc., as hotwords during the ASR process to enhance recognition results.
- FunClip integrates the [CAM++](https://modelscope.cn/models/iic/speech_campplus_sv_zh-cn_16k-common/summary) speaker recognition model, enabling users to use the auto-recognized speaker ID as the target for trimming, to clip segments from a specific speaker.
- The functionalities are realized through Gradio interaction, offering simple installation and ease of use. It can also be deployed on a server and accessed via a browser.
- FunClip supports multi-segment free clipping and automatically returns full video SRT subtitles and target segment SRT subtitles, offering a simple and convenient user experience.

You're welcome to try it out, and we look forward to any requests and valuable suggestions you may have about subtitle generation or speech recognition~

<a name="What's New"></a>
## What's New🚀
- 🔥2024/05/13 FunClip updates its clipping feature based on large language models, and the usage is as follows:
  1. After the recognition, select the name of the large model and configure your own apikey;
  2. Click on the 'LLM Smart Paragraph Selection' button, and FunClip will automatically combine two prompts with the video's srt subtitles;
  3. Click on the 'LLM Smart Clipping' button, and based on the output results of the large language model from the previous step, FunClip will extract the timestamps for clipping;
  4. You can try changing the prompt to leverage the capabilities of the large language models to get the results you want;
- 🔥FunClip adds smart clipping functionality with large language models, integrating models from the qwen series, gpt series, etc., providing default prompts. You can also explore and share tips for setting prompts.
- 2024/05/09 FunClip updated to v1.1.0, including the following updates and fixes:
  - Support configuration of output file directory, saving ASR intermediate results and video clipping intermediate files;
  - UI upgrade (see guide picture below), video and audio cropping function on the same page, button position adjustment;
  - Fixed a bug introduced due to FunASR interface upgrade, which has caused some serious editing errors;
  - Support configuring different start and end time offsets for each paragraph;
  - Code update, etc;
- 2024/03/06 Fix bugs in using FunClip with command line.
- 2024/02/28 [FunASR](https://github.com/alibaba-damo-academy/FunASR) is updated to 1.0 version, use FunASR1.0 and SeACo-Paraformer to conduct ASR with hotword customization.
- 2023/10/17 Fix bugs in multiple periods chosen, used to return video with wrong length.
- 2023/10/10 FunClipper now supports recognizing with speaker diarization ability, choose 'yes' button in 'Recognize Speakers' and you will get recognition results with speaker id for each sentence. And then you can clip out the periods of one or some speakers (e.g. 'spk0' or 'spk0#spk3') using FunClipper.

<a name="On Going"></a>
## On Going🌵

- FunClip will support Whisper model for English users, coming soon.
- FunClip will intergrat the abilities of large langage model, coming soon.

<a name="Install"></a>
## Install🔨

### Python env install

```shell
# clone funclip repo
git clone https://github.com/alibaba-damo-academy/FunClip.git
cd FunClip
# install Python requirments
pip install -r ./requirements.txt
```

### imagemagick install (Optional)

If you want to clip video file with embedded subtitles

1. ffmpeg and imagemagick is required

- On Ubuntu
```shell
apt-get -y update && apt-get -y install ffmpeg imagemagick
sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml
```
- On MacOS
```shell
brew install imagemagick
sed -i 's/none/read,write/g' /usr/local/Cellar/imagemagick/7.1.1-8_1/etc/ImageMagick-7/policy.xml 
```
2. Download font file to funclip/font

```shell
wget https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/STHeitiMedium.ttc -O font/STHeitiMedium.ttc
```
<a name="Usage"></a>
## Use FunClip

### A. Use FunClip as local Gradio Service
You can establish your own FunClip service which is same as [Modelscope Space](https://modelscope.cn/studios/iic/funasr_app_clipvideo/summary) as follow:
```shell
python funclip/launch.py
```
then visit ```localhost:7860``` you will get a Gradio service like below and you can use FunClip following the steps:
<img src="docs/images/guide.jpg"/>

- Step1: Upload your video file (or try the example videos below)
- Step2: Copy the text segments you need to 'Text to Clip'
- Step3: Adjust subtitle settings (if needed)
- Step4: Click 'Clip' or 'Clip and Generate Subtitles'

### B. Experience FunClip in Modelscope
You can try FunClip in modelscope space: [link](https://modelscope.cn/studios/iic/funasr_app_clipvideo/summary).

### C. Use FunClip in command line

FunClip supports you to recognize and clip with commands:
```shell
# step1: Recognize
python funclip/videoclipper.py --stage 1 \
                       --file examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output
# now you can find recognition results and entire SRT file in ./output/
# step2: Clip
python funclip/videoclipper.py --stage 2 \
                       --file examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output \
                       --dest_text '我们把它跟乡村振兴去结合起来，利用我们的设计的能力' \
                       --start_ost 0 \
                       --end_ost 100 \
                       --output_file './output/res.mp4'
```

<a name="Community"></a>
## Community Communication🍟

FunClip is firstly open-sourced bu FunASR team, any useful PR is welcomed.

You can also scan the following DingTalk group or WeChat group QR code to join the community group for communication.

|                           DingTalk group                            |                     WeChat group                      |
|:-------------------------------------------------------------------:|:-----------------------------------------------------:|
| <div align="left"><img src="docs/images/dingding.png" width="250"/> | <img src="docs/images/wechat.png" width="215"/></div> |

## Support Us🌟

[![Star History Chart](https://api.star-history.com/svg?repos=alibaba-damo-academy/FunClip&type=Date)](https://star-history.com/#alibaba-damo-academy/FunClip&Date)

## Find Speech Models in FunASR

[FunASR](https://github.com/alibaba-damo-academy/FunASR) hopes to build a bridge between academic research and industrial applications on speech recognition. By supporting the training & finetuning of the industrial-grade speech recognition model released on ModelScope, researchers and developers can conduct research and production of speech recognition models more conveniently, and promote the development of speech recognition ecology. ASR for Fun！

📚FunASR Paper: <a href="https://arxiv.org/abs/2305.11013"><img src="https://img.shields.io/badge/Arxiv-2305.11013-orange"></a> 

📚SeACo-Paraformer Paper: <a href="https://arxiv.org/abs/2308.03266"><img src="https://img.shields.io/badge/Arxiv-2308.03266-orange"></a>

🌟Support FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR/stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunASR.svg?style=social'></a>
