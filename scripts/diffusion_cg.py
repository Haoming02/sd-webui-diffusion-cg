from math import sin, pi
from modules.script_callbacks import on_cfg_after_cfg, AfterCFGCallbackParams
from modules.ui_components import InputAccordion
from modules import scripts
import gradio as gr
import torch

VERSION = "2.0.0"


class DiffusionCG(scripts.Script):
    enable: bool = False
    recenter: float = 0.0
    normalization: float = 0.0

    def title(self):
        return "Diffusion CG"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with InputAccordion(False, label=f"{self.title()} v{VERSION}") as enable:
            with gr.Row():
                recenter = gr.Slider(
                    label="Recenter Strength",
                    info="higher = balanced colors",
                    minimum=0.0,
                    maximum=1.0,
                    step=0.05,
                    value=0.0,
                )
                normalization = gr.Slider(
                    label="Normalization Strength",
                    info="higher = more contrast",
                    minimum=0.0,
                    maximum=1.0,
                    step=0.05,
                    value=0.0,
                )

        self.paste_field_names = []
        self.infotext_fields = [
            (recenter, "CG Recenter"),
            (normalization, "CG Normalization"),
        ]

        for _, name in self.infotext_fields:
            self.paste_field_names.append(name)

        return [enable, recenter, normalization]

    def before_hr(self, p, *args):
        DiffusionCG.recenter *= 0.1
        DiffusionCG.normalization *= 0.1

    def process(self, p, enable: bool, recenter: float, normalization: float):
        if getattr(p, "_ad_inner", False):
            enable = False

        DiffusionCG.enable = enable
        if not enable:
            return

        DiffusionCG.recenter = recenter
        DiffusionCG.normalization = normalization

        p.extra_generation_params.update(
            {
                "CG Recenter": recenter,
                "CG Normalization": normalization,
            }
        )

    @classmethod
    @torch.inference_mode()
    def cfg_preprocess(cls, params: AfterCFGCallbackParams):
        if not cls.enable:
            return
        if params.sampling_step + 1 >= params.total_sampling_steps - 1:
            return

        ratio: float = params.sampling_step / params.total_sampling_steps
        strength: float = 1.0 - sin(ratio * pi / 2.0)
        latent: torch.Tensor = params.x.detach().clone()

        batches: int = latent.shape[0]
        channels: int = latent.shape[1]

        for b in range(batches):
            _std: float = latent[b].std()

            for c in range(channels):
                bias: float = latent[b][c].std() / _std * strength
                latent[b][c] += (0.0 - latent[b][c].mean()) * bias * cls.recenter

                magnitude = float(latent[b][c].max() - latent[b][c].min())
                factor = 1.0 / 0.13025
                scale = max(factor / magnitude - 1.0, 0.0)
                latent[b][c] *= scale * cls.normalization * strength + 1.0

        params.x = latent


on_cfg_after_cfg(DiffusionCG.cfg_preprocess)
