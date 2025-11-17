# SD Webui Diffusion Color Grading
This is an Extension for the WebUIs, which performs "Color Grading" during the generation, producing a more **neutral** and **balanced**, but also **vibrant** and **contrasty** color.

> **Support:** [A1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui), [Classic](https://github.com/Haoming02/sd-webui-forge-classic/tree/classic), [Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo), [Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge), [reForge](https://github.com/Panchovix/stable-diffusion-webui-reForge)

> [!Note]
> This Extension is disabled during [ADetailer](https://github.com/Bing-su/adetailer) pass to prevent inconsistent colors

## Features

This Extension comes with two main effects, **Recenter** and **Normalization**:

#### Recenter

<ins>TimothyAlexisVass</ins> discovered that, the value of the latent noise Tensor often starts off-centered, and the mean of each channel tends to drift away from `0`.

When this feature is enabled, the output images will not have a color bias, and all colors will distribute more evenly. Additionally, the brightness will be adjusted so that bright areas are not overblown and dark areas are not clipped, producing an effect similar to HDR phone photos.

> [!Important]
> If the original image should have bias, this may cause the opposite effect instead<br>
> **e.g.** a photo of orange will have a blue tint...

#### Normalization

<ins>TimothyAlexisVass</ins> discovered that the images decoded with VAE usually fall within a certain value range, and thus theorized that if the final latent noise has a narrower value range than intended, then some precision is essentially wasted.

When this feature is enabled, the latent noise will attempt to span across a large value range, before getting decoded by the VAE.

> [!Tip]
> You can enable both features at the same time to generate some stunning images

> [!Warning]
> This Extension officially supports `SD 1` and `SDXL` checkpoints; may not work properly with other models

## Examples

<p align="center">
<img src="examples\off.webp" width=384>
<img src="examples\on.webp" width=384>
<br><code>Off | On</code><br>
</p>

```
1girl, solo, hatsune miku, vocaloid, white dress, cowboy shot, wind, floating hair, looking at viewer, smile, beach, sunset, sky, cloud, (safe)
Negative prompt: old, oldest, text, glitch, deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, very displeasing, (worst quality, bad quality:1.2), jpeg artifacts, signature, watermark, username, conjoined, ai-generated, explicit
Steps: 20, Sampler: Euler a, Schedule type: Automatic, CFG scale: 4.5, Seed: 1234, Size: 896x1152, Model hash: 4a87df67ba, Model: evenlyMix_v11, VAE hash: 235745af8d, VAE: sdxl-vae.safetensors, Denoising strength: 0.48, Clip skip: 2, eps_scaling_factor: 1.02, RNG: CPU, SkipEarly: 0.1, NGMS: 0.5, CG Recenter: 0.6, CG Normalization: 0.4, Hires resize: 1344x1792, Hires steps: 12, Hires upscaler: Lanczos, MaHiRo: True, Emphasis: No norm, Version: classic
```

<hr>

<details>
<summary>Details</summary>

This Extension is the fruition of the joint research between [TimothyAlexisVass](https://github.com/TimothyAlexisVass) with their findings, and me with my experience in developing [Vectorscope CC](https://github.com/Haoming02/sd-webui-vectorscope-cc)

The `Tensor` of the latent noise has a dimension of `[batch, channel, height / 8, width / 8]`

- For **SD1**: Latent has **4** channels, representing the `-K`, `-M`, `C`, `Y` color for the **CMYK** color model

- For **SDXL**: Latent has **4** channels; the first 3 channels represent the `Y'`, `-Cr`, `-Cb` color for the **Y'CbCr** color model, while the 4th channel is probably the pattern/structure

> See Also [Latent Playground](https://github.com/Haoming02/sd-webui-latent-playground)

</details>
