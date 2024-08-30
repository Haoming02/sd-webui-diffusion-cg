from modules.script_callbacks import on_ui_settings
from modules.shared import OptionInfo, opts
import gradio as gr

section = ("diffusion_cg", "Diffusion CG")
tabs = ("None", "txt2img", "img2img", "Both")


def on_settings():
    opts.add_option(
        "always_center",
        OptionInfo(
            "None",
            "Always Perform Recenter on:",
            component=gr.Radio,
            component_args={"choices": tabs},
            section=section,
            category_id="sd",
        ).needs_reload_ui(),
    )

    opts.add_option(
        "always_normalize",
        OptionInfo(
            "None",
            "Always Perform Normalization on:",
            component=gr.Radio,
            component_args={"choices": tabs},
            section=section,
            category_id="sd",
        ).needs_reload_ui(),
    )

    opts.add_option(
        "default_arch",
        OptionInfo(
            "1.5",
            "Default Stable Diffusion Version",
            component=gr.Radio,
            component_args={"choices": ("1.5", "XL")},
            section=section,
            category_id="sd",
        ).needs_reload_ui(),
    )


on_ui_settings(on_settings)
