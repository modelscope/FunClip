top_md_1 = ("""
    基于阿里巴巴通义实验室自研SeACo-Paraformer-长音频版的语音识别、端点检测、标点预测、时间戳功能、角色区分、热词定制化功能

    准确识别，自由复制所需段落，或者设置说话人标识，一键裁剪、添加字幕

    * Step1: 上传视频或音频文件（或使用下方的用例体验），点击 **<font color="#f7802b">识别</font>** 按钮
    * Step2: 复制识别结果中所需的文字至右上方，或者右设置说话人标识，设置偏移与字幕配置（可选）
    * Step3: 点击 **<font color="#f7802b">裁剪</font>** 按钮或 **<font color="#f7802b">裁剪并添加字幕</font>** 按钮获得结果
    """)

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

top_md_3 = ("""访问FunASR项目与论文能够帮助您深入了解ParaClipper中所使用的语音处理相关模型：
    <div align="center">
    <div style="display:flex; gap: 0.25rem;" align="center">
        FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR'><img src='https://img.shields.io/badge/Github-Code-blue'></a> 
        FunASR Paper: <a href="https://arxiv.org/abs/2305.11013"><img src="https://img.shields.io/badge/Arxiv-2305.11013-orange"></a> 
        🌟Star FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR/stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunASR.svg?style=social'></a>
    </div>
    </div>
    """)

top_md_4 = ("""我们在「LLM智能裁剪」模块中提供三种LLM调用方式，
            1. 选择阿里云百炼平台通过api调用qwen系列模型，此时需要您准备百炼平台的apikey，请访问[阿里云百炼](https://bailian.console.aliyun.com/#/home)；
            2. 选择GPT开头的模型即为调用openai官方api，此时需要您自备sk与网络环境；
            3. [gpt4free](https://github.com/xtekky/gpt4free?tab=readme-ov-file)项目也被集成进FunClip，可以通过它免费调用gpt模型；
            
            其中方式1与方式2需要在界面中传入相应的apikey
                        
            方式3而可能非常不稳定，返回时间可能很长或者结果获取失败，可以多多尝试或者自己准备sk使用方式1
            """)
