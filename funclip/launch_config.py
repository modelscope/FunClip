"""Launch policy for the FunClip Gradio service."""


def build_launch_kwargs(*, share, port, listen):
    kwargs = {
        "share": share,
        "server_port": port,
        "server_name": "127.0.0.1",
    }
    if listen:
        kwargs.update(
            server_name="0.0.0.0",
            inbrowser=False,
            _frontend=False,
        )
    return kwargs
