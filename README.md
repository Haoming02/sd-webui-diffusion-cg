# SD Webui Diffusion Color Grading
This is an Extension for the [Automatic1111 Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui), which performs *Color Grading* during the generation, producing a more **neutral** and **balanced**, but also **vibrant** and **contrasty** color.

> This is the fruition of the joint research between [TimothyAlexisVass](https://github.com/TimothyAlexisVass) with their findings, and me with my experience in developing [Vectorscope CC](https://github.com/Haoming02/sd-webui-vectorscope-cc)

**Note:** This Extension is disabled during [ADetailer](https://github.com/Bing-su/adetailer) phase to prevent inconsistent colors

## Features

This Extension comes with two main effects, **Recenter** and **Normalization**:

#### Recenter

<h5 align="center">Abstract</h5>

<ins>TimothyAlexisVass</ins> discovered that, the value of the latent noise Tensor often starts off-centered, and the mean of each channel tends to drift away from `0`. Therefore, I wrote a function to guide the mean back to `0`.

<h5 align="center">Effects</h5>

When you enable the feature, the output images will not have a biased color tint, and all colors will distribute more evenly; Additionally, the brightness will be adjusted so that bright areas are not overblown and dark areas are not clipped, producing an effect similar to HDR photos.

<h5 align="center">Samples</h5>

<p align="center">
<img src="examples\rc_off.jpg" width=384>
<img src="examples\rc_on.jpg" width=384>
<br><code>Off | On</code><br>
</p>

#### Normalization

<h5 align="center">Abstract</h5>

By encoding images back into latent noise using VAE, <ins>TimothyAlexisVass</ins> discovered that the resulting values usually fall within a certain range, and thus theorized that if the final latent noise has a smaller value range than normal, then some precision is essentailly wasted. This gave me an idea to write a function that make the latent noise utilize the full depth.

<h5 align="center">Effects</h5>

When you enable the feature, the latent noise will attempt to span across the full value range if possible, before getting decoded by the VAE. As a result, bright areas will get brighter and dark areas will get darker, and additional details may also be introduced in these areas.

<p align="center">
<img src="examples\nml_off.jpg" width=384>
<img src="examples\nml_on.jpg" width=384>
<br><code>Off | On</code><br>
</p>

> Both features increase the image file size when enabled, suggesting that they "contain more informations"

#### Misc.

- You can enable both features at the same time to generate some stunning images
- This Extension supports both `SD 1.5` and `SDXL` checkpoints

<p align="center">
<img src="examples\xl_off.jpg" width=384>
<img src="examples\xl_on.jpg" width=384>
<br><code>Off | On</code><br>
</p>

## Settings
In the `Diffusion CG` section under the <ins>Stable Diffusion</ins> category in the **Settings** tab, you can make either feature default to `enable`, as well as setting the Stable Diffusion architecture to start with.

<hr>

<details>
<summary>Structures of Stable Diffusion</summary>

The `Tensor` of the latent noise has a dimention of `[batch, 4, height / 8, width / 8]`.

- For **SD 1.5:** From my trial and error when developing [Vectorscope CC](https://github.com/Haoming02/sd-webui-vectorscope-cc), each of the 4 channels essentially represents the `-K`, `-M`, `C`, `Y` color for the **CMYK** color model.

- For **SDXL:** According to <ins>TimothyAlexisVass</ins>'s [Blogpost](https://huggingface.co/blog/TimothyAlexisVass/explaining-the-sdxl-latent-space), the first 3 channels represent the `Y'`, `-Cr`, `-Cb` color for the **Y'CbCr** color model, while the 4th channel is the pattern/structure.

</details>
