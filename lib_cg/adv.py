import gradio as gr

COLOR_DESC: dict[str, str] = {
    "C": "Red | Cyan",
    "M": "Green | Magenta",
    "Y": "Blue | Yellow",
    "K": "Bright | Dark",
    "Y'": "Dark | Bright",
    "Cb": None,
    "Cr": None,
}


def advanced_settings(default_sd: str, sd_ver: gr.Radio) -> list[gr.Slider]:

    color_channels: list[gr.Slider] = []

    with gr.Group(visible=(default_sd == "1.5")) as setting15:

        for ch in ("C", "M", "Y", "K"):
            color_channels.append(
                gr.Slider(
                    label=ch,
                    info=COLOR_DESC[ch],
                    minimum=-1.00,
                    maximum=1.00,
                    step=0.05,
                    value=0.0,
                )
            )

    with gr.Group(visible=(default_sd == "XL")) as settingXL:

        for ch in ("Y'", "Cb", "Cr"):
            color_channels.append(
                gr.Slider(
                    label=ch,
                    info=COLOR_DESC[ch],
                    minimum=-1.00,
                    maximum=1.00,
                    step=0.05,
                    value=0.0,
                )
            )

    def on_arch_change(choice: str):
        return [
            gr.update(visible=(choice == "1.5")),
            gr.update(visible=(choice == "XL")),
        ]

    sd_ver.change(on_arch_change, inputs=[sd_ver], outputs=[setting15, settingXL])

    return color_channels
