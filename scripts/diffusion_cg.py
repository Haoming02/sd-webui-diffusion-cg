from modules.sd_samplers_kdiffusion import KDiffusionSampler
from scripts.cg_version import VERSION
from modules import script_callbacks
import modules.scripts as scripts
from modules import shared
import gradio as gr

# LUTS
# 1.5: [-K, -M, C, Y]
# XL:  [L, -a, b]

LUTS = {
    '1.5': [0.0, -0.5152, 0.0126, -0.1278],
    'XL': [0.0, 0.0, 0.0, None]
}


DYNAMIC_RANGE = [3.25, 2.5, 2.5, 2.5]


def normalize_tensor(x, r):
    x_min = abs(float(x.min()))
    x_max = abs(float(x.max()))

    delta = (x_max - x_min) / 2.0
    x -= delta

    ratio = r / float(x.max())

    x *= max(ratio, 0.95)

    return x + delta


original_callback = KDiffusionSampler.callback_state

def center_callback(self, d):
    if not self.diffcg_enable or getattr(self.p, 'image_mask', None) is not None:
        return original_callback(self, d)

    batchSize = d['x'].size(0)
    channels = 4 if self.diffcg_arch == '1.5' else 3

    for b in range(batchSize):
        for i in range(channels):

            if self.diffcg_recenter:
                d['x'][b][i] += (LUTS[self.diffcg_arch][i] - d['x'][b][i].mean()) * self.diffcg_recenter_strength

            if self.diffcg_normalize and (d['i'] + 1) >= self.diffcg_last_step - 1:
                d[self.diffcg_tensor][b][i] = normalize_tensor(d[self.diffcg_tensor][b][i], DYNAMIC_RANGE[i])

    return original_callback(self, d)

KDiffusionSampler.callback_state = center_callback


class DiffusionCG(scripts.Script):

    def title(self):
        return "DiffusionCG"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(f'Diffusion CG {VERSION}', open=False):
            with gr.Row():
                enableG = gr.Checkbox(label="Enable (Global)")
                sd_ver = gr.Radio(['1.5', 'XL'], value='1.5', label="Stable Diffusion Version")

            with gr.Row():
                with gr.Group():
                    gr.Markdown('<h3 align="center">Recenter</h3>')
                    rc_str = gr.Slider(label="Effect Strength", minimum=0.0, maximum=1.0, step=0.2, value=0.0)

                with gr.Group():
                    gr.Markdown('<h3 align="center">Normalization</h3>')
                    enableN = gr.Checkbox(label="Activate")

        return [enableG, sd_ver, rc_str, enableN]

    def before_hr(self, p, *args):
        KDiffusionSampler.diffcg_normalize = False

    def process(self, p, enableG:bool, sd_ver:str, rc_str:float, enableN:bool):
        KDiffusionSampler.diffcg_enable = enableG
        KDiffusionSampler.diffcg_arch = sd_ver

        KDiffusionSampler.diffcg_recenter = rc_str > 0.0
        KDiffusionSampler.diffcg_normalize = enableN
        KDiffusionSampler.diffcg_recenter_strength = rc_str

        KDiffusionSampler.diffcg_tensor = 'x' if p.sampler_name.strip() == 'Euler' else 'denoised'

        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps and p.denoising_strength < 1.0:
            KDiffusionSampler.diffcg_last_step = int(p.steps * p.denoising_strength) + 1
        else:
            KDiffusionSampler.diffcg_last_step = p.steps


def restore_callback():
    KDiffusionSampler.callback_state = original_callback

script_callbacks.on_script_unloaded(restore_callback)
