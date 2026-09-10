# Installation And Startup / 安装与启动

[English](#english) · [中文](#中文)

## English

### Start In One Environment

Run commands from the FunClip repository root. Use Python 3.12 for the example below, and keep FunClip separate from existing ASR services. Install a matching PyTorch/torchaudio pair for your platform using the [official PyTorch instructions](https://pytorch.org/get-started/locally/), then install this repository's requirements.

Linux x86-64 CPU example, in a new environment:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --index-url https://download.pytorch.org/whl/cpu \
  "torch==2.10.0" "torchaudio==2.10.0"
python -m pip install -r requirements.txt
python -m pip check
python funclip/launch.py --help
```

This is a CPU setup, not a CUDA recipe. For a GPU or another platform, select the appropriate matching pair before installing the remaining requirements; do not replace packages in a running production environment. Windows/macOS hardware and driver combinations need separate validation.

On Windows, you can use the environment's Python directly without changing PowerShell's execution policy:

```powershell
py -3.12 -m venv .venv
# Install the platform-appropriate torch/torchaudio pair into this environment first.
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe funclip\launch.py --help
```

`--help` checks imports and argument parsing without downloading a model or starting a public service. It does not verify transcription or video export. A successful `pip check` only checks declared dependency compatibility, not native-library loading, model downloads or inference.

### If Installation Or Startup Fails

**`CERTIFICATE_VERIFY_FAILED` during pip install:** fix the HTTPS trust failure first. It means the package download did not complete, so a later `No module named 'funasr'` is not evidence that requirements omitted the package. Check the failing hostname, system clock, proxy and configured package indexes. Use certificates supplied by your OS/Python distribution or an approved corporate CA; never disable certificate verification or make arbitrary hosts trusted to get an install through. Pip supports an approved CA bundle through `--cert`/`PIP_CERT`; see its [certificate documentation](https://pip.pypa.io/en/stable/topics/https-certificates/).

**The package was installed, but this Python cannot find it:** compare the interpreter and pip paths before reinstalling anything:

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
python -m pip --version
python -m pip show funasr torch torchaudio gradio moviepy transformers
python -m pip check
```

Use that same `python` to launch FunClip. An IDE, notebook or shell may otherwise use another interpreter even if a bare `pip` command succeeded.

**The traceback already enters `site-packages/funasr`:** the package was found. Capture the complete exception, especially its final line; do not keep installing packages based only on intermediate `pkgutil` or import-stack frames. Check the import separately, then the application:

```bash
python -c "from funasr import AutoModel; print('FunASR import OK')"
python funclip/launch.py --help
```

For index/proxy diagnostics, inspect `python -m pip config debug` locally. Before posting output, redact credentials, tokens, proxy passwords and private index URLs. Include the FunClip commit, OS, interpreter/package versions, the failing command and the full traceback. A screenshot cut off before the final exception cannot establish the cause. These distinctions come from the two different failure paths reported in [#147](https://github.com/modelscope/FunClip/issues/147); that issue remains open for the original environments to be retested.

### Keep The Two Transformers Routes Separate

FunClip currently requires **Transformers 4.x** (`transformers<5.0`) and `huggingface_hub<1.0`. Its toolkit model, clipping and Gradio paths are not the same environment as the native Nano **Transformers 5.x** example. Installing the native example's requirements into FunClip can violate these constraints.

For standalone native transcription, use a different virtual environment and the [native Transformers guide](https://www.funasr.com/en/docs/native-transformers.html). Native transcription alone does not provide FunClip's timestamp-based video clipping workflow.

## 中文

### 先固定一个环境

在 FunClip 仓库根目录执行命令。上面的 Linux x86-64 CPU 示例使用 Python 3.12 和独立虚拟环境，先安装匹配的 PyTorch/torchaudio，再安装 `requirements.txt`。GPU、Windows 或 macOS 请按 [PyTorch 官方安装说明](https://pytorch.org/get-started/locally/)选择适合平台的匹配版本，不要直接替换正在运行的生产服务环境。

Windows 可以使用上面的完整 `.venv\Scripts\python.exe` 路径，不必修改 PowerShell 执行策略。后续安装、检查和启动都应使用同一个解释器。

`python funclip/launch.py --help` 只检查导入与参数解析，不下载模型、不启动公网服务，也不证明识别或视频导出成功。`pip check` 只检查依赖声明是否兼容，不能代替动态库加载、模型下载或真实推理测试。

### 按报错阶段处理

**安装时出现 `CERTIFICATE_VERIFY_FAILED`：** 先处理 HTTPS 证书信任问题。下载未完成，后续出现 `No module named 'funasr'` 并不说明依赖清单漏了这个包。检查失败域名、系统时间、代理和 pip 源；使用操作系统/Python 发行版提供的证书，企业代理则使用经管理员认可的 CA。不要通过关闭校验或随意信任主机绕过错误。受信任 CA 的 `--cert`/`PIP_CERT` 配置见 [pip 官方证书说明](https://pip.pypa.io/en/stable/topics/https-certificates/)。

**安装成功却找不到模块：** 运行英文部分的解释器和版本检查命令。确认 `sys.executable`、`python -m pip --version` 指向同一个虚拟环境，再用相同的 `python` 启动。不要把另一个 shell、IDE 或 notebook 的安装结果当成当前环境已经装好。

**调用栈已经进入 `site-packages/funasr`：** 包已经被找到，不能仅凭中间的 `pkgutil`/导入堆栈判断缺少哪个依赖。先运行上面的独立 `AutoModel` 导入检查，再执行 `--help`，保留包含最后一行异常的完整 traceback。[#147](https://github.com/modelscope/FunClip/issues/147) 的两张截图分别属于证书失败和已进入 FunASR 的导入失败，不能当作同一个问题。

需要检查代理或源配置时，在本机查看 `python -m pip config debug`。公开日志前，删除账号密码、token、代理凭据和私有源地址；提供 FunClip commit、操作系统、解释器与包版本、完整命令和 traceback。报告者尚未完成原环境复测时，诊断或文档更新不等于问题已经解决。

### 不混用 Transformers 环境

FunClip 当前依赖 **Transformers 4.x** 和 `huggingface_hub<1.0`，Nano 原生 **Transformers 5.x** 是另一条路径。不要在 FunClip 环境里直接执行原生示例的升级命令。

如果只需原生语音转写，请在另一个虚拟环境使用[原生 Transformers 指南](https://www.funasr.com/docs/native-transformers.html)。原生转写本身不提供 FunClip 所需的完整时间戳视频裁剪流程。
