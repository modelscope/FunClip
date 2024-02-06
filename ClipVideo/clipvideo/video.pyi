import gradio
from pathlib import Path
from ffmpy import FFmpeg
from gradio import utils
from gradio_client.documentation import document, set_documentation_group
set_documentation_group("component")
from gradio.events import Dependency

@document()
class Video(gradio.Video):
    """
    This is adapted from gradio.Video. Only `def preprocess()` is modified for auto recoginzing input x is local data or url
    """
    def preprocess(self, x):
        """
        Parameters:
            x: A tuple of (video file data, subtitle file data) or just video file data.
        Returns:
            A string file path or URL to the preprocessed video. Subtitle file data is ignored.
        """
        if x is None:
            return None
        elif isinstance(x, dict):
            video = x
        else:
            video = x[0]

        file_name, file_data, is_file = (
            video.get("name"),
            video["data"],
            video.get("is_file", False),
        )

        if is_file:
            assert file_name is not None, "Received file data without a file name."
            if utils.validate_url(file_name): # URL path
                file_name = Path(self.download_temp_copy_if_needed(file_name))
            else: # Local path
                file_name = Path(self.make_temp_copy_if_needed(file_name))
        else:
            assert file_data is not None, "Received empty file data."
            file_name = Path(self.base64_to_temp_file_if_needed(file_data, file_name))

        uploaded_format = file_name.suffix.replace(".", "")
        needs_formatting = self.format is not None and uploaded_format != self.format
        flip = self.source == "webcam" and self.mirror_webcam

        if needs_formatting or flip:
            format = f".{self.format if needs_formatting else uploaded_format}"
            output_options = ["-vf", "hflip", "-c:a", "copy"] if flip else []
            output_options += ["-an"] if not self.include_audio else []
            flip_suffix = "_flip" if flip else ""
            output_file_name = str(
                file_name.with_name(f"{file_name.stem}{flip_suffix}{format}")
            )
            if Path(output_file_name).exists():
                return output_file_name
            ff = FFmpeg(
                inputs={str(file_name): None},
                outputs={output_file_name: output_options},
            )
            ff.run()
            return output_file_name
        elif not self.include_audio:
            output_file_name = str(file_name.with_name(f"muted_{file_name.name}"))
            ff = FFmpeg(
                inputs={str(file_name): None},
                outputs={output_file_name: ["-an"]},
            )
            ff.run()
            return output_file_name
        else:
            return str(file_name)