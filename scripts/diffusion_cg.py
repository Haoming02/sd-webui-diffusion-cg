from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import script_callbacks
import modules.scripts as scripts
from modules import shared
import gradio as gr


VERSION = 'v0.2.0'


# luminance = 0.2126 * R + 0.7152 * G + 0.0722 * B
# LUTS: [-K, -M, C, Y]

LUTS = {
    '1.5': [0.0, -0.5152, 0.0126, -0.1278],
    'XL': [-0.01, -0.01, 0.01, None]
}


# https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/configs/v1-inference.yaml#L17
# (1.0 / 0.18215) / 2 = 2.74499039253
# (1.0 / 0.13025) / 2 = 3.83877159309

DYNAMIC_RANGE = {
    'Default': [3.2, 2.5, 2.5, 2.5],
    'Maximize': [3.839, 2.745, 2.745, 2.745]
}


def normalize_tensor(x, r):
    x_min = abs(float(x.min()))
    x_max = abs(float(x.max()))

    delta = (x_max - x_min) / 2.0
    x -= delta

    ratio = r / float(x.max())

    if ratio > 0.95:
        x *= ratio

    return x + delta


original_callback = KDiffusionSampler.callback_state

def center_callback(self, d):
    if not self.diffcg_enable:
        return original_callback(self, d)

    batchSize = d['x'].size(0)
    channels = 4 if self.diffcg_arch == '1.5' else 3

    for b in range(batchSize):
        for i in range(channels):

            if self.diffcg_recenter:
                d['x'][b][i] += (LUTS[self.diffcg_arch][i] - d['x'][b][i].mean())

            if self.diffcg_normalize and (d['i'] + 1) >= self.diffcg_last_step - 1:
                d[self.diffcg_tensor][b][i] = normalize_tensor(d[self.diffcg_tensor][b][i], DYNAMIC_RANGE[self.diffcg_normalize_strength][i])

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

            gr.Markdown('<hr>')

            with gr.Row():
                with gr.Group():
                    gr.Markdown('<h3 align="center">Recenter</h3>')
                    enableC = gr.Checkbox(label="Enable")

                with gr.Group():
                    gr.Markdown('<h3 align="center">Normalization</h3>')
                    enableN = gr.Checkbox(label="Enable")
                    n_str = gr.Radio(['Default', 'Maximize'], value='Default', label="Effect Strength")

        return [enableG, sd_ver, enableC, enableN, n_str]

    def before_hr(self, p, *args):
        KDiffusionSampler.diffcg_normalize = False

    def process(self, p, enableG:bool, sd_ver:str, enableC:bool, enableN:bool, n_str:str):
        KDiffusionSampler.diffcg_enable = enableG
        KDiffusionSampler.diffcg_arch = sd_ver
        KDiffusionSampler.diffcg_recenter = enableC
        KDiffusionSampler.diffcg_normalize = enableN
        KDiffusionSampler.diffcg_normalize_strength = n_str
        KDiffusionSampler.diffcg_tensor = 'x' if p.sampler_name.strip() == 'Euler' else 'denoised'

        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps and p.denoising_strength < 1.0:
            KDiffusionSampler.diffcg_last_step = int(p.steps * p.denoising_strength) + 1
        else:
            KDiffusionSampler.diffcg_last_step = p.steps


def restore_callback():
    KDiffusionSampler.callback_state = original_callback

script_callbacks.on_script_unloaded(restore_callback)
