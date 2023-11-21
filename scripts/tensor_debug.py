from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import script_callbacks, shared
import matplotlib.pyplot as plt
import numpy as np
import datetime
import shutil
import os

original_callback = KDiffusionSampler.callback_state

CH = []
Steps = []

Debug_Folders = []

LABEL = ['dimgrey', 'lime', 'cyan', 'gold']

def debug_callback(self, d):
    if not hasattr(shared.opts, 'tensor_debug') or shared.opts.tensor_debug is not True:
        return original_callback(self, d)

    output_folder = os.path.join(self.p.outpath_samples, 'debug')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    global Debug_Folders
    if output_folder not in Debug_Folders:
        Debug_Folders.append(output_folder)

    global CH
    global Steps
    if d['i'] == 0:
        CH = []
        Steps = []
        for i in range(4):
            CH.append({'min':[], 'max':[], 'mean':[], 'std':[]})

    Steps.append(d['i'] + 1)

    for i in range(4):
        CH[i]['min'].append(round(float(d['x'][0][i].min()), 4))
        CH[i]['max'].append(round(float(d['x'][0][i].max()), 4))
        CH[i]['mean'].append(round(float(d['x'][0][i].mean()), 4))
        CH[i]['std'].append(round(float(d['x'][0][i].std()), 4))

    if (d['i'] + 1) == self.p.steps:
        x = np.array(Steps)
        t = datetime.datetime.now().strftime("%m.%d-%H.%M.%S")

        for mode in ['mean', 'min', 'max']: # 'min', 'max', 'std'
            for i in range(4):
                y = np.array(CH[i][mode])
                plt.plot(x, y, label=f'{i}', color=LABEL[i])

            plt.legend()
            plt.title(f'channel-{mode} Graph')
            plt.xlabel("Steps")
            plt.savefig(os.path.join(output_folder, f'{t}-{mode}.png'), dpi=300)
            plt.clf()

    return original_callback(self, d)

KDiffusionSampler.callback_state = debug_callback

def restore_callback():
    KDiffusionSampler.callback_state = original_callback
    for d in Debug_Folders:
        shutil.rmtree(d)

script_callbacks.on_script_unloaded(restore_callback)

def on_ui_settings():
    shared.opts.add_option("tensor_debug", shared.OptionInfo(False, "[For Development Only] Log Tensor Statistics Each Step", section=("system", "System")))

script_callbacks.on_ui_settings(on_ui_settings)
