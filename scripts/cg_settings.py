from modules import script_callbacks, shared
import gradio as gr

Section = ('diffusion_cg', "Diffusion CG")

def on_ui_settings():
    shared.opts.add_option("always_center", shared.OptionInfo("None", "Always Perform Recenter on:", gr.Radio, lambda: {"choices": ["None", "txt2img", "img2img", "Both"]}, section=Section).needs_reload_ui())
    shared.opts.add_option("always_normalize", shared.OptionInfo("None", "Always Perform Normalization on:", gr.Radio, lambda: {"choices": ["None", "txt2img", "img2img", "Both"]}, section=Section).needs_reload_ui())
    shared.opts.add_option("default_arch", shared.OptionInfo("1.5", "Default Stable Diffusion Version", gr.Radio, lambda: {"choices": ["1.5", "XL"]}, section=Section).needs_reload_ui())

script_callbacks.on_ui_settings(on_ui_settings)
