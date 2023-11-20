# SD Webui Diffusion Color Grading
<h4 align = "right"><i>Alpha</i></h4>
<p align="right">
<sup><i>Experimental... Expect feature-breaking changes~</i></sup>
</p>

This is an Extension for the [Automatic1111 Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui), which performs *Color Grading* during the generation, 
producing a more **neutral** and **balanced**, but also **vibrant** and **contrasty** color.

> This is the fruition of the joint research between [TimothyAlexisVass](https://github.com/TimothyAlexisVass) with their findings, and me with my experience in developing [Vectorscope CC](https://github.com/Haoming02/sd-webui-vectorscope-cc)

This Extension comes with two main features, **Recenter** and **Normalization**:

### Recenter

<h5 align="center">Abstract</h5>

<ins>TimothyAlexisVass</ins> discovered that, the value of the latent noise Tensor often starts off-centered, and the mean of each channel tends to drift away from `0`. 
Therefore, I tried to write an Extension to guide the mean back to `0`. However after some trial and error, it was found out that pushing the mean of every channel to `0` often produces a green tint,
suggesting that the "center" of each channel might not simply be the same at `0`. After experimenting with hundreds of images, with both Anime and Realistic checkpoints, 
I have located a set of rather suitable values for a **neutral and balanced** tone.

<h5 align="center">Effects</h5>

When you enable the feature, the output images will not have a biased color tint, and all colors will distribute evenly;
Additionally, the brightness will be adjusted so that bright areas are not overblown and dark areas are not clipped, 
producing a similar effect like the HDR photos taken by smartphones.

<h5 align="center">Samples</h5>

<p align="center">
<img src="samples\c_a_off.jpg" width=256>
<img src="samples\c_a_on.jpg" width=256>
<br><code>Off | On</code><br>
</p>

<p align="center">
<img src="samples\c_r_off.jpg" width=256>
<img src="samples\c_r_on.jpg" width=256>
<br><code>Off | On</code><br>
</p>

### Normalization

<h5 align="center">Abstract</h5>

By encoding images into latent noise with VAE, <ins>TimothyAlexisVass</ins> discovered that the values for VAE to decode are usually within a certain range, 
and thus theorized that if the final latent noise has a smaller value range, then some precision is essentailly wasted. 
This gave me an idea to write a function that can make the latent noise utilize the full color depth,
making the final output more **vibrant** and **contrasty**.

<h5 align="center">Effects</h5>

When you enable the feature, the latent noise will attempt to span across the value ranges if possible, before getting decoded by the VAE. 
As a result, bright areas will get brighter and dark areas will get darker; Additional details may also be introduced in these areas.

> Seems to have less effects when not using `Euler` sampler...

> This feature is disabled during Hires. fix pass

<h5 align="center">Samples</h5>

<p align="center">
<img src="samples\n_a_off.jpg" width=256>
<img src="samples\n_a_on.jpg" width=256>
<br><code>Off | On</code><br>
</p>

<p align="center">
<img src="samples\n_r_off.jpg" width=256>
<img src="samples\n_r_on.jpg" width=256>
<br><code>Off | On</code><br>
</p>

<h4 align="center">Combined</h4>
<p align="center">Finally, you can also enable both features at the same time, creating some really stunning results!</p>

<p align="center">
<img src="samples\cn_a_1.jpg" width=512>
<br>
<img src="samples\cn_a_2.jpg" width=512>
</p>

<p align="center">
<b>SDXL</b><br>
<img src="samples\cn_xl_off.jpg" width=384>
<img src="samples\cn_xl_on.jpg" width=384>
<br><code>Off | On</code><br>
</p>

> Some sample images were generated using older versions of the Extension. I will update all of them again when the Extension is finally out of experimental stage.

## To Do
- [ ] Parameter Settings
  - Such as effect strength
  - However, I also want this to be a simple plug-and-use Extension
- [ ] Better SDXL Support
  > The current values may produce a pink tint for SDXL
- [ ] Better Algorithms
  > Currently, for extreme cases *(**eg.** a bowl of oranges)*, the overall colors will be overcompensating
- [ ] Generation InfoText

<hr>

**Checkpoints Used:**
- [UHD-23](https://civitai.com/models/22371/uhd-23)
- [Realistic Vision V5.1](https://civitai.com/models/4201/realistic-vision-v51)
- [SDXL Base 1.0 w/ 0.9 VAE](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main)

<hr>

<details>
<summary>Debug</summary>

1. This also comes with the script `tensor_debug.py`
2. You can enable it in the `System` section of **Settings** tab
3. It will plot out the values of the Tensor during the generation, and save to the `debug` folder in `output`
4. *Perhaps you can make some interesting discoveries too?*
5. The folder will be deleted whenever the UI is reloaded/closed
</details>
