from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules.script_callbacks import on_script_unloaded
from modules.ui_components import InputAccordion
from modules import scripts

from functools import wraps
import gradio as gr
import torch

from lib_cg import SCALE_FACTOR, c_t2i, c_i2i, n_t2i, n_i2i, default_sd
from lib_cg.params import DiffusionCGParams
from lib_cg.adv import advanced_settings
from lib_cg.xyz import xyz_support

VERSION = "1.2.0"


@torch.inference_mode()
def normalize_tensor(x: torch.Tensor, r: float) -> torch.Tensor:
    ratio: float = r / max(abs(float(x.min())), abs(float(x.max())))
    x *= max(ratio, 1.0)
    return x


original_callback = KDiffusionSampler.callback_state


@torch.inference_mode()
@wraps(original_callback)
def center_callback(self, d):
    if getattr(self.p, "_ad_inner", False):
        return original_callback(self, d)

    params: DiffusionCGParams = getattr(self, "diffcg_params", None)
    if not params:
        return original_callback(self, d)

    X: torch.Tensor = d["denoised"].detach().clone()
    batchSize: int = X.size(0)
    channels: int = len(params.LUTs)

    for b in range(batchSize):
        for c in range(channels):

            if params.rc_str > 0.0:
                d["denoised"][b][c] += (params.LUTs[c] - X[b][c].mean()) * params.rc_str

            if params.normalization and (d["i"] + 1) >= (params.total_step - 1):
                d["denoised"][b][c] = normalize_tensor(X[b][c], params.dynamic_range)

    return original_callback(self, d)


KDiffusionSampler.callback_state = center_callback


class DiffusionCG(scripts.Script):

    def __init__(self):
        self.xyzCache = {}
        xyz_support(self.xyzCache)

    def title(self):
        return "Diffusion CG"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):

        with InputAccordion(
            label=f"{self.title()} v{VERSION}",
            open=False,
            value=(
                ((not is_img2img) and (c_t2i or n_t2i))
                or (is_img2img and (c_i2i or n_i2i))
            ),
        ) as enable:

            with gr.Row():

                sd_ver = gr.Radio(
                    ["1.5", "XL"], value=default_sd, label="Stable Diffusion Version"
                )

                with gr.Column():

                    rc_str = gr.Slider(
                        label="[Recenter]",
                        info="Effect Strength",
                        minimum=0.0,
                        maximum=1.0,
                        step=0.2,
                        value=(
                            1.0
                            if (((not is_img2img) and c_t2i) or (is_img2img and c_i2i))
                            else 0.0
                        ),
                    )

                    normalization = gr.Checkbox(
                        label="[Normalization]",
                        value=(((not is_img2img) and n_t2i) or (is_img2img and n_i2i)),
                    )

            with gr.Accordion("Recenter Settings", open=False):
                C, M, Y, K, L, a, b = advanced_settings(default_sd, sd_ver)

        comps: list = []

        self.paste_field_names = []
        self.infotext_fields = [
            (enable, "Diffusion CG Enable"),
            (sd_ver, "Diffusion CG SD-Ver"),
            (rc_str, "Diffusion CG Recenter"),
            (normalization, "[Diff. CG] Normalization"),
            (C, "Diffusion CG C"),
            (M, "Diffusion CG M"),
            (Y, "Diffusion CG Y"),
            (K, "Diffusion CG K"),
            (L, "Diffusion CG Y'"),
            (a, "Diffusion CG Cb"),
            (b, "Diffusion CG Cr"),
        ]

        for comp, name in self.infotext_fields:
            comp.do_not_save_to_config = True
            self.paste_field_names.append(name)
            comps.append(comp)

        return comps

    def before_hr(self, p, *args):
        KDiffusionSampler.diffcg_last_step = (
            getattr(p, "hr_second_pass_steps", None) or p.steps
        )

    def process(
        self,
        p,
        enable: bool,
        sd_ver: str,
        rc_str: float,
        normalization: bool,
        C: float,
        M: float,
        Y: float,
        K: float,
        Lu: float,
        Cb: float,
        Cr: float,
    ):

        if "enable" in self.xyzCache.keys():
            enable = self.xyzCache["enable"].lower().strip() == "true"

        if not enable:
            if len(self.xyzCache) > 0:
                if "enable" not in self.xyzCache.keys():
                    print("\n[Vec.CC] x [X/Y/Z Plot] Extension is not Enabled!\n")
                self.xyzCache.clear()

            setattr(KDiffusionSampler, "diffcg_params", None)
            return p

        rc_str = float(self.xyzCache.get("rc_str", rc_str))

        if "normalization" in self.xyzCache.keys():
            normalization = self.xyzCache["normalization"].lower().strip() == "true"

        C = float(self.xyzCache.get("C", C))
        M = float(self.xyzCache.get("M", M))
        Y = float(self.xyzCache.get("Y", Y))
        K = float(self.xyzCache.get("K", K))
        Lu = float(self.xyzCache.get("Lu", Lu))
        Cb = float(self.xyzCache.get("Cb", Cb))
        Cr = float(self.xyzCache.get("Cr", Cr))

        params = DiffusionCGParams(
            getattr(p, "firstpass_steps", None) or p.steps,
            enable,
            sd_ver,
            rc_str,
            [-K, -M, C, Y] if (sd_ver == "1.5") else [Lu, -Cr, -Cb],
            normalization,
            (1.0 / SCALE_FACTOR["1.5"]) / 2.0,  # XL causes Noises...
        )

        setattr(KDiffusionSampler, "diffcg_params", params)

        p.extra_generation_params.update(
            {
                "Diffusion CG Enable": enable,
                "Diffusion CG SD-Ver": sd_ver,
                "Diffusion CG Recenter": rc_str,
                "Diffusion CG Normalization": normalization,
            }
        )

        if sd_ver == "1.5":
            p.extra_generation_params.update(
                {
                    "Diffusion CG C": C,
                    "Diffusion CG M": M,
                    "Diffusion CG Y": Y,
                    "Diffusion CG K": K,
                }
            )
        else:
            p.extra_generation_params.update(
                {
                    "Diffusion CG Y'": Lu,
                    "Diffusion CG Cb": Cb,
                    "Diffusion CG Cr": Cr,
                }
            )

        self.xyzCache.clear()


def restore_callback():
    KDiffusionSampler.callback_state = original_callback


on_script_unloaded(restore_callback)
