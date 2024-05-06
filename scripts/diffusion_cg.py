from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import shared, scripts, script_callbacks
import gradio as gr

VERSION = "v1.0.1"

DYNAMIC_RANGE = [3.25, 2.5, 2.5, 2.5]

Default_LUTs = {"C": 0.01, "M": 0.5, "Y": -0.13, "K": 0}


def normalize_tensor(x, r):
    X = x.detach().clone()

    ratio = r / max(abs(float(X.min())), abs(float(X.max())))
    X *= max(ratio, 0.99)

    return X


original_callback = KDiffusionSampler.callback_state


def center_callback(self, d):
    if not self.diffcg_enable or getattr(self.p, "_ad_inner", False):
        return original_callback(self, d)

    X = d["denoised"].detach().clone()
    batchSize = X.size(0)
    channels = len(self.LUTs)

    for b in range(batchSize):
        for c in range(channels):

            if self.diffcg_recenter_strength > 0.0:
                d["denoised"][b][c] += (
                    self.LUTs[c] - X[b][c].mean()
                ) * self.diffcg_recenter_strength

            print(d["denoised"][b][c].min(), d["denoised"][b][c].max())

            if self.diffcg_normalize and (d["i"] + 1) == self.diffcg_last_step:
                d["denoised"][b][c] = normalize_tensor(X[b][c], DYNAMIC_RANGE[c])

    return original_callback(self, d)


KDiffusionSampler.callback_state = center_callback


# ["None", "txt2img", "img2img", "Both"]
ac = getattr(shared.opts, "always_center", "None")
an = getattr(shared.opts, "always_normalize", "None")
def_sd = getattr(shared.opts, "default_arch", "1.5")
adv_opt = getattr(shared.opts, "show_center_opt", False)

c_t2i = ac in ("txt2img", "Both")
c_i2i = ac in ("img2img", "Both")
n_t2i = an in ("txt2img", "Both")
n_i2i = an in ("img2img", "Both")


class DiffusionCG(scripts.Script):

    def title(self):
        return "DiffusionCG"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(f"Diffusion CG {VERSION}", open=False):
            with gr.Row():
                enableG = gr.Checkbox(
                    label="Enable (Global)",
                    value=(
                        ((not is_img2img) and (c_t2i or n_t2i))
                        or (is_img2img and (c_i2i or n_i2i))
                    ),
                )
                sd_ver = gr.Radio(
                    ["1.5", "XL"], value=def_sd, label="Stable Diffusion Version"
                )

            with gr.Row():
                with gr.Group():
                    gr.Markdown('<h3 align="center">Recenter</h3>')

                    if not is_img2img:
                        v = 1.0 if c_t2i else 0.0
                    else:
                        v = 1.0 if c_i2i else 0.0

                    rc_str = gr.Slider(
                        label="Effect Strength",
                        minimum=0.0,
                        maximum=1.0,
                        step=0.2,
                        value=v,
                    )

                with gr.Group():
                    gr.Markdown('<h3 align="center">Normalization</h3>')
                    enableN = gr.Checkbox(
                        label="Activate",
                        value=(((not is_img2img) and n_t2i) or (is_img2img and n_i2i)),
                    )

            with gr.Accordion("Recenter Settings", visible=adv_opt, open=False):
                with gr.Group(visible=(def_sd == "1.5")) as setting15:
                    C = gr.Slider(
                        label="C",
                        minimum=-1.00,
                        maximum=1.00,
                        step=0.01,
                        value=Default_LUTs["C"],
                    )
                    M = gr.Slider(
                        label="M",
                        minimum=-1.00,
                        maximum=1.00,
                        step=0.01,
                        value=Default_LUTs["M"],
                    )
                    Y = gr.Slider(
                        label="Y",
                        minimum=-1.00,
                        maximum=1.00,
                        step=0.01,
                        value=Default_LUTs["Y"],
                    )
                    K = gr.Slider(
                        label="K",
                        minimum=-1.00,
                        maximum=1.00,
                        step=0.01,
                        value=Default_LUTs["K"],
                    )

                with gr.Group(visible=(def_sd == "XL")) as settingXL:
                    L = gr.Slider(
                        label="L", minimum=-1.00, maximum=1.00, step=0.01, value=0.0
                    )
                    a = gr.Slider(
                        label="a", minimum=-1.00, maximum=1.00, step=0.01, value=0.0
                    )
                    b = gr.Slider(
                        label="b", minimum=-1.00, maximum=1.00, step=0.01, value=0.0
                    )

            def on_radio_change(choice):
                if choice == "1.5":
                    return [
                        gr.Group.update(visible=True),
                        gr.Group.update(visible=False),
                    ]
                else:
                    return [
                        gr.Group.update(visible=False),
                        gr.Group.update(visible=True),
                    ]

            sd_ver.change(on_radio_change, sd_ver, [setting15, settingXL])

        self.paste_field_names = [
            (rc_str, "ReCenter Str"),
            (enableN, "Normalization"),
            (sd_ver, "SD_ver"),
        ]
        self.infotext_fields = [
            (rc_str, "ReCenter Str"),
            (enableN, "Normalization"),
            (sd_ver, "SD_ver"),
        ]

        if adv_opt:
            self.paste_field_names += [
                (
                    C,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[0])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    M,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[1])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    Y,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[2])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    K,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[3])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    L,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[0])
                        if len(d.get("LUTs", "").split(",")) == 3
                        else gr.update()
                    ),
                ),
                (
                    a,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[1])
                        if len(d.get("LUTs", "").split(",")) == 3
                        else gr.update()
                    ),
                ),
                (
                    b,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[2])
                        if len(d.get("LUTs", "").split(",")) == 3
                        else gr.update()
                    ),
                ),
            ]
            self.infotext_fields += [
                (
                    C,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[0])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    M,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[1])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    Y,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[2])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    K,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[3])
                        if len(d.get("LUTs", "").split(",")) == 4
                        else gr.update()
                    ),
                ),
                (
                    L,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[0])
                        if len(d.get("LUTs", "").split(",")) == 3
                        else gr.update()
                    ),
                ),
                (
                    a,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[1])
                        if len(d.get("LUTs", "").split(",")) == 3
                        else gr.update()
                    ),
                ),
                (
                    b,
                    lambda d: (
                        float(d["LUTs"].strip("[]").split(",")[2])
                        if len(d.get("LUTs", "").split(",")) == 3
                        else gr.update()
                    ),
                ),
            ]

        for comp in [enableG, sd_ver, rc_str, enableN, C, M, Y, K, L, a, b]:
            comp.do_not_save_to_config = True

        return [enableG, sd_ver, rc_str, enableN, C, M, Y, K, L, a, b]

    def before_hr(self, p, *args):
        KDiffusionSampler.diffcg_normalize = False

    def process(
        self,
        p,
        enableG: bool,
        sd_ver: str,
        rc_str: float,
        enableN: bool,
        C: float,
        M: float,
        Y: float,
        K: float,
        L: float,
        a: float,
        b: float,
    ):

        KDiffusionSampler.diffcg_enable = enableG
        if not enableG:
            return p

        if sd_ver == "1.5":
            KDiffusionSampler.LUTs = [-K, -M, C, Y]
        else:
            KDiffusionSampler.LUTs = [L, -a, b]

        KDiffusionSampler.diffcg_recenter_strength = rc_str
        KDiffusionSampler.diffcg_normalize = enableN

        if (
            not hasattr(p, "enable_hr")
            and not shared.opts.img2img_fix_steps
            and getattr(p, "denoising_strength", 1.0) < 1.0
        ):
            KDiffusionSampler.diffcg_last_step = int(p.steps * p.denoising_strength) + 1
        else:
            KDiffusionSampler.diffcg_last_step = p.steps

        p.extra_generation_params.update(
            {
                "ReCenter Str": rc_str,
                "Normalization": enableN,
                "SD_ver": sd_ver,
            }
        )

        if adv_opt:
            if def_sd == "1.5":
                p.extra_generation_params["LUTs"] = f"[{C}, {M}, {Y}, {K}]"
            else:
                p.extra_generation_params["LUTs"] = f"[{L}, {a}, {b}]"


def restore_callback():
    KDiffusionSampler.callback_state = original_callback


script_callbacks.on_script_unloaded(restore_callback)
