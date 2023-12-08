from modules.sd_samplers_kdiffusion import KDiffusionSampler
from scripts.cg_version import VERSION
from modules import script_callbacks
import modules.scripts as scripts
from modules import shared
import gradio as gr


DYNAMIC_RANGE = [3.25, 2.5, 2.5, 2.5]

Default_LUTs = {
    'C': 0.01,
    'M': 0.5,
    'Y': -0.13,
    'K': 0
}


def normalize_tensor(x, r):
    delta = x.mean()
    x -= delta

    x_min = abs(float(x.min()))
    x_max = abs(float(x.max()))

    ratio = r / max(x_min, x_max)
    x *= max(ratio, 0.95)

    return x + delta


original_callback = KDiffusionSampler.callback_state

def center_callback(self, d):
    if not self.diffcg_enable or getattr(self.p, 'image_mask', None) is not None:
        return original_callback(self, d)

    batchSize = d['x'].size(0)
    channels = len(self.LUTs)

    for b in range(batchSize):
        for c in range(channels):

            if self.diffcg_recenter:
                d['x'][b][c] += (self.LUTs[c] - d['x'][b][c].mean()) * self.diffcg_recenter_strength

            if self.diffcg_normalize and (d['i'] + 1) >= self.diffcg_last_step - 1:
                d[self.diffcg_tensor][b][c] = normalize_tensor(d[self.diffcg_tensor][b][c], DYNAMIC_RANGE[c])

    return original_callback(self, d)

KDiffusionSampler.callback_state = center_callback


# ["None", "txt2img", "img2img", "Both"]
ac = getattr(shared.opts, 'always_center', 'None')
an = getattr(shared.opts, 'always_normalize', 'None')
def_sd = getattr(shared.opts, 'default_arch', '1.5')

c_t2i = (ac == "txt2img" or ac == "Both")
c_i2i = (ac == "img2img" or ac == "Both")
n_t2i = (an == "txt2img" or an == "Both")
n_i2i = (an == "img2img" or an == "Both")


class DiffusionCG(scripts.Script):

    def title(self):
        return "DiffusionCG"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(f'Diffusion CG {VERSION}', open=False):
            with gr.Row():
                enableG = gr.Checkbox(label="Enable (Global)", value=(((not is_img2img) and (c_t2i or n_t2i)) or (is_img2img and (c_i2i or n_i2i))))
                sd_ver = gr.Radio(['1.5', 'XL'], value=def_sd, label="Stable Diffusion Version")

            with gr.Row():
                with gr.Group():
                    gr.Markdown('<h3 align="center">Recenter</h3>')

                    if not is_img2img:
                        v = 1.0 if c_t2i else 0.0
                    else:
                        v = 1.0 if c_i2i else 0.0

                    rc_str = gr.Slider(label="Effect Strength", minimum=0.0, maximum=1.0, step=0.2, value=v)

                with gr.Group():
                    gr.Markdown('<h3 align="center">Normalization</h3>')
                    enableN = gr.Checkbox(label="Activate", value=(((not is_img2img) and n_t2i) or (is_img2img and n_i2i)))

            with gr.Accordion('Recenter Settings', open=False):
                with gr.Group(visible=(def_sd=='1.5')) as setting15:
                    C = gr.Slider(label="C", minimum=-1.00, maximum=1.00, step=0.01, value=Default_LUTs['C'])
                    M = gr.Slider(label="M", minimum=-1.00, maximum=1.00, step=0.01, value=Default_LUTs['M'])
                    Y = gr.Slider(label="Y", minimum=-1.00, maximum=1.00, step=0.01, value=Default_LUTs['Y'])
                    K = gr.Slider(label="K", minimum=-1.00, maximum=1.00, step=0.01, value=Default_LUTs['K'])

                with gr.Group(visible=(def_sd=='XL')) as settingXL:
                    L = gr.Slider(label="L", minimum=-1.00, maximum=1.00, step=0.01, value=0.0)
                    a = gr.Slider(label="a", minimum=-1.00, maximum=1.00, step=0.01, value=0.0)
                    b = gr.Slider(label="b", minimum=-1.00, maximum=1.00, step=0.01, value=0.0)

            def on_radio_change(choice):
                if choice != "1.5":
                    return [gr.Group.update(visible=True), gr.Group.update(visible=False)]
                else:
                    return [gr.Group.update(visible=False), gr.Group.update(visible=True)]

            sd_ver.select(on_radio_change, sd_ver, [setting15, settingXL])

        return [enableG, sd_ver, rc_str, enableN, C, M, Y, K, L, a, b]

    def before_hr(self, p, *args):
        KDiffusionSampler.diffcg_normalize = False

    def process(self, p, enableG:bool, sd_ver:str, rc_str:float, enableN:bool, C, M, Y, K, L, a, b):
        KDiffusionSampler.diffcg_enable = enableG

        if sd_ver == '1.5':
            KDiffusionSampler.LUTs = [-K, -M, C, Y]
        else:
            KDiffusionSampler.LUTs = [L, -a, b]

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
