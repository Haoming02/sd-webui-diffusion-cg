from modules import shared
from .settings import *

SCALE_FACTOR: dict = {
    "1.5": 0.18215,  # https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/configs/v1-inference.yaml#L17
    "XL": 0.13025,  # https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/configs/sd_xl_inpaint.yaml#L4
}

# ["None", "txt2img", "img2img", "Both"]
ac: str = getattr(shared.opts, "always_center", "None")
an: str = getattr(shared.opts, "always_normalize", "None")

c_t2i: bool = ac in ("txt2img", "Both")
c_i2i: bool = ac in ("img2img", "Both")
n_t2i: bool = an in ("txt2img", "Both")
n_i2i: bool = an in ("img2img", "Both")

default_sd: str = getattr(shared.opts, "default_arch", "1.5")
