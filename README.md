# ParaClipper

ParaClipper是一款自动化视频剪辑工具，通过调用阿里巴巴通义实验室开源的[FunASR](https://github.com/alibaba-damo-academy/FunASR) Paraformer系列模型进行视频音轨的语音识别。用户可以自由选择识别结果中的片段，点击裁剪按钮即可获取对应片段的视频。

在上述基本功能的基础上，ParaClipper有以下特色功能：
- ParaClipper结合了[SeACo-Paraformer](https://modelscope.cn/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/summary)的热词定制化功能，在ASR过程中可以指定一些实体词、人名等作为热词，提升识别效果。
- ParaClipper结合了[CAM++](https://modelscope.cn/models/iic/speech_campplus_sv_zh-cn_16k-common/summary)说话人识别模型，用户可以将自动识别出的说话人ID作为裁剪目标，将某一说话人的段落裁剪出来。
- 通过Gradio交互实现上述功能，安装简单使用方便。
- ParaClipper支持多段自由剪辑，并且会自动返回全视频SRT字幕，目标段落SRT字幕，方便用户使用。

## 近期更新

- 2024/02/28 ParaClipper升级到FunASR1.0模型调用方式，通过FunASR开源的SeACo-Paraformer模型在视频剪辑中进一步支持热词定制化功能。
- 2024/02/28 原FunASR-APP/ClipVideo更名为ParaClipper。

## 使用ParaClipper进行视频剪辑

### 安装
```shell
# 安装FunASR（必须）
pip install -U funasr
# 安装ParaClipper的Python依赖（必须）
pip install -r ParaClipper/requirments.txt
```

### 安装imagemagick（可选）
如果你希望使用自动生成字幕的视频裁剪功能，需要安装imagemagick
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

并且下载你需要的字体文件，这里我们提供一个默认的黑体字体文件
```shell
wget https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ParaClipper/STHeitiMedium.ttc -O font/STHeitiMedium.ttc
```

### 使用ParaClipper

#### 在本地启动Gradio服务

```shell
python paraclipper/launch.py
```
随后在浏览器中访问```localhost:7860```即可看到如下图所示的界面，按如下步骤即可进行视频剪辑
1. 上传你的视频（或使用下方的视频用例）
2. （可选）设置热词，勾选是否使用说话人识别功能
3. 点击识别按钮获取识别结果
4. 将识别结果中的选段复制到对应位置，或者将说话人ID输入到对应为止
5. （可选）配置剪辑参数，偏移量与字幕设置等
6. 点击“裁剪”或“裁剪并添加字幕”按钮


<img src="docs/images/show2.0.png"/>

#### 通过命令行调用使用ParaClipper的相关功能（更新中）
```shell
# 步骤一：识别
python paraclipper/videoclipper.py --stage 1 \
                       --file examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output
# ./output中生成了识别结果与srt字幕等
# 步骤二：裁剪
python paraclipper/videoclipper.py --stage 2 \
                       --file examples/2022云栖大会_片段.mp4 \
                       --output_dir ./output \
                       --dest_text '我们把它跟乡村振兴去结合起来，利用我们的设计的能力' \
                       --start_ost 0 \
                       --end_ost 100 \
                       --output_file './output/res.mp4'
```

#### 通过Modelscope创空间体验ParaClipper
[ParaClipper创空间](https://modelscope.cn/studios/damo/funasr_app_ParaClipper/summary)（版本较旧，并且受网络影响速度较慢，不推荐）

### 通过FunASR了解语音识别相关技术

[FunASR](https://github.com/alibaba-damo-academy/FunASR)是阿里巴巴通义实验室开源的端到端语音识别工具包，目前已经成为主流ASR工具包之一。其主要包括Python pipeline，SDK部署与海量开源工业ASR模型等。

📚FunASR论文: <a href="https://arxiv.org/abs/2305.11013"><img src="https://img.shields.io/badge/Arxiv-2305.11013-orange"></a> 
📚SeACo-Paraformer论文：<a href="https://arxiv.org/abs/2308.03266"><img src="https://img.shields.io/badge/Arxiv-2308.03266-orange"></a> 
⭐支持FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR/stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunASR.svg?style=social'></a>