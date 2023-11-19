from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import script_callbacks
import modules.scripts as scripts
from modules import shared
import gradio as gr


VERSION = 'v0.1.1'


# luminance = 0.2126 * R + 0.7152 * G + 0.0722 * B
# LUTS: [-K, -M, C, Y]

LUTS = [0.0, -0.5152, 0.0126, -0.1278]


# https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/configs/v1-inference.yaml#L17
# (1.0 / 0.18215) / 2 = 2.74499039253

DYNAMIC_RANGE = [2.74, 2.74, 2.74, 2.74]


def normalize_tensor(x, r):
    x_min = float(x.min())
    x_max = float(x.max())

    ratio = r / max(abs(x_min), abs(x_max))

    if ratio < 1.0:
        return x
    else:
        return x * ratio


original_callback = KDiffusionSampler.callback_state

def center_callback(self, d):
    if not self.diffcg_enable:
        return original_callback(self, d)

    batchSize = d['x'].size(0)
    for b in range(batchSize):
        for i in range(4):

            if self.diffcg_recenter:
                d['x'][b][i] += (LUTS[i] - d['x'][b][i].mean())

            if self.diffcg_normalize and (d['i'] + 1) == self.diffcg_last_step:
                d['x'][b][i] = normalize_tensor(d['x'][b][i], DYNAMIC_RANGE[i])

    return original_callback(self, d)

KDiffusionSampler.callback_state = center_callback


class DiffusionCG(scripts.Script):

    def title(self):
        return "DiffusionCG"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(f'Diffusion CG {VERSION}', open=False):
            enableG = gr.Checkbox(label="Enable (Global)")

            with gr.Row():
                with gr.Group():
                    gr.Markdown('<h3 align="center">Recenter</h3>')
                    enableC = gr.Checkbox(label="Enable")

                with gr.Group():
                    gr.Markdown('<h3 align="center">Normalization</h3>')
                    enableN = gr.Checkbox(label="Enable")

        return [enableG, enableC, enableN]

    def before_hr(self, p, *args):
        KDiffusionSampler.diffcg_enable = False

    def process(self, p, enableG:bool, enableC:bool, enableN:bool):
        KDiffusionSampler.diffcg_enable = enableG
        KDiffusionSampler.diffcg_recenter = enableC
        KDiffusionSampler.diffcg_normalize = enableN

        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps:
            KDiffusionSampler.diffcg_last_step = int(p.steps * p.denoising_strength) + 1
        else:
            KDiffusionSampler.diffcg_last_step = p.steps


def restore_callback():
    KDiffusionSampler.callback_state = original_callback

script_callbacks.on_script_unloaded(restore_callback)
