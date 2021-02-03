# coding: utf8

def freesurfer2mollweid_full(overlay_lh_file, overlay_rh_file):
    png_file_lh = freesurfer2mollweid_side(overlay_lh_file)
    png_file_rh = freesurfer2mollweid_side(overlay_rh_file)

    return png_file_lh, png_file_rh


def freesurfer2mollweid_side(overlay_file):
    import nibabel as nib
    from matplotlib import pyplot as plt
    import os
    import pandas as pd

    overlay = nib.freesurfer.io.read_geometry(overlay_file)
    basedir = os.getcwd()
    tmp = pd.read_csv(os.path.abspath("./projected.csv"))
    plt.scatter(tmp['x'], tmp['y'], overlay)
    plt.axis('off')
    plt.savefig(os.path.join(basedir, str(overlay_file).replace(".mgh", "") + ".png"))
