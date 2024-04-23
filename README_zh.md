# FunClip🎥

(简体中文|[English](./README.md))

FunClip是一款完全开源、本地部署的自动化视频剪辑工具，通过调用阿里巴巴通义实验室开源的[FunASR](https://github.com/alibaba-damo-academy/FunASR) Paraformer系列模型进行视频的语音识别，随后用户可以自由选择识别结果中的文本片段或说话人，点击裁剪按钮即可获取对应片段的视频（[快速体验](https://modelscope.cn/studios/iic/funasr_app_clipvideo/summary)）。

在上述基本功能的基础上，FunClip有以下特色：
- FunClip集成了阿里巴巴开源的工业级模型[Paraformer-Large](https://modelscope.cn/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/summary)，是当前识别效果最优的开源中文ASR模型之一，Modelscope下载量1300w+次，并且能够一体化的准确预测时间戳。
- FunClip集成了[SeACo-Paraformer](https://modelscope.cn/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/summary)的热词定制化功能，在ASR过程中可以指定一些实体词、人名等作为热词，提升识别效果。
- FunClip集成了[CAM++](https://modelscope.cn/models/iic/speech_campplus_sv_zh-cn_16k-common/summary)说话人识别模型，用户可以将自动识别出的说话人ID作为裁剪目标，将某一说话人的段落裁剪出来。
- 通过Gradio交互实现上述功能，安装简单使用方便，并且可以在服务端搭建服务通过浏览器使用。
- FunClip支持多段自由剪辑，并且会自动返回全视频SRT字幕、目标段落SRT字幕，使用简单方便。

欢迎体验使用，欢迎提出关于字幕生成或语音识别的需求与宝贵建议~

## 近期更新🚀

- 2024/03/06 命令行调用方式更新与问题修复，相关功能可以正常使用。
- 2024/02/28 FunClip升级到FunASR1.0模型调用方式，通过FunASR开源的SeACo-Paraformer模型在视频剪辑中进一步支持热词定制化功能。
- 2024/02/28 原FunASR-APP/ClipVideo更名为FunClip。

### 安装

#### Python环境安装

```shell
# 安装FunASR
pip install -U funasr
# 可以通过源码安装funasr
git clone https://github.com/alibaba-damo-academy/FunASR.git
cd FunASR; pip install -e ./
# 安装FunClip的Python依赖
pip install -r ./requirments.txt
# 根据你的环境（CUDA，Python版本等）安装torch和torchaudio
pip install torch==xxx torchaudio==xxx
```

#### 安装imagemagick（可选）

1. 如果你希望使用自动生成字幕的视频裁剪功能，需要安装imagemagick

- Ubuntu
```shell
apt-get -y update && apt-get -y install ffmpeg imagemagick
sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml
```
- MacOS
```shell
brew install imagemagick
sed -i 's/none/read,write/g' /usr/local/Cellar/imagemagick/7.1.1-8_1/etc/ImageMagick-7/policy.xml 
```

2. 下载你需要的字体文件，这里我们提供一个默认的黑体字体文件

```shell
wget https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/STHeitiMedium.ttc -O font/STHeitiMedium.ttc
```

### 使用FunClip

#### A.在本地启动Gradio服务

```shell
python funclip/launch.py
```
随后在浏览器中访问```localhost:7860```即可看到如下图所示的界面，按如下步骤即可进行视频剪辑
1. 上传你的视频（或使用下方的视频用例）
2. （可选）设置热词，勾选是否使用说话人识别功能
3. 点击识别按钮获取识别结果
4. 将识别结果中的选段复制到对应位置，或者将说话人ID输入到对应为止
5. （可选）配置剪辑参数，偏移量与字幕设置等
6. 点击“裁剪”或“裁剪并添加字幕”按钮

<img src="docs/images/demo.png"/>

#### B.通过命令行调用使用FunClip的相关功能（更新中）
```shell
# 步骤一：识别
python funclip/videoclipper.py --stage 1 \
                       --file examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output
# ./output中生成了识别结果与srt字幕等
# 步骤二：裁剪
python funclip/videoclipper.py --stage 2 \
                       --file examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output \
                       --dest_text '我们把它跟乡村振兴去结合起来，利用我们的设计的能力' \
                       --start_ost 0 \
                       --end_ost 100 \
                       --output_file './output/res.mp4'
```

#### C.通过Modelscope创空间体验FunClip
[funclip创空间](https://modelscope.cn/studios/iic/funasr_app_clipvideo/summary)

## 施工中

- FunClip将会集成Whisper模型，以提供英文视频剪辑能力。

## 社区交流

FunClip开源项目由FunASR社区维护，欢迎加入社区，交流与讨论，以及合作开发等。

|                              钉钉群                                |                     微信群                      |
|:-------------------------------------------------------------------:|:-----------------------------------------------------:|
| <div align="left"><img src="docs/images/dingding.png" width="250"/> | <img src="docs/images/wechat.png" width="215"/></div> |


## 通过FunASR了解语音识别相关技术

[FunASR](https://github.com/alibaba-damo-academy/FunASR)是阿里巴巴通义实验室开源的端到端语音识别工具包，目前已经成为主流ASR工具包之一。其主要包括Python pipeline，SDK部署与海量开源工业ASR模型等。

📚FunASR论文: <a href="https://arxiv.org/abs/2305.11013"><img src="https://img.shields.io/badge/Arxiv-2305.11013-orange"></a> 

📚SeACo-Paraformer论文：<a href="https://arxiv.org/abs/2308.03266"><img src="https://img.shields.io/badge/Arxiv-2308.03266-orange"></a> 

⭐支持FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR.stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunASR.svg?style=social'></a>
