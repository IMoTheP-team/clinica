# coding: utf8

def freesurfer2ply_full(overlay_lh_file, overlay_rh_file, surface_lh_file, surface_rh_file):
    ply_file_lh = freesurfer2ply_side(overlay_lh_file, surface_lh_file)
    ply_file_rh = freesurfer2ply_side(overlay_rh_file, surface_rh_file)

    return ply_file_lh, ply_file_rh


def freesurfer2ply_side(overlay_file, surface_file):
    import nibabel as nib
    import os
    import pandas as pd
    import matplotlib as mpl
    import matplotlib.cm as cm
    import numpy as np
    from nibabel.freesurfer.mghformat import load

    overlay = load(overlay_file).get_fdata().flatten()
    coords, faces = nib.freesurfer.io.read_geometry(surface_file)

    num_verts = coords.shape[0]
    num_faces = faces.shape[0]

    # TODO : check.verts.faces

    # HEADER SETTINGS

    basedir = os.getcwd()
    array = ["ply", "format ascii 1.0"]

    array.append(f"element vertex {num_verts}")

    array.append("property float x")
    array.append("property float y")
    array.append("property float z")

    array.append("property uchar red")
    array.append("property uchar green")
    array.append("property uchar blue")
    array.append("property uchar alpha")

    array.append(f"element face {num_faces}")
    array.append("property list uchar int vertex_indices")

    array.append("end_header")

    with open(os.path.join(basedir, str(overlay_file).replace(".mgh", "") + ".ply"), 'w') as file:
        file.writelines("%s\n" % line for line in array)

    # COORDS VERTEX + COLORS

    df_coords = pd.DataFrame(coords)
    df_coords = df_coords - df_coords.mean()

    norm = mpl.colors.Normalize(vmin=overlay.min(), vmax=overlay.max())
    cmap = cm.hot

    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    overlay_color = m.to_rgba(overlay, bytes=True)

    df_color = pd.DataFrame(overlay_color)

    df = pd.concat([df_coords, df_color], axis=1)
    df.to_csv(os.path.join(basedir, str(overlay_file).replace(".mgh", "") + ".ply"), sep=" ", mode="a", header=False, index=False)
    print(len(df.index))

    # FACES
    faces = np.insert(faces, 0, np.repeat(3, faces.shape[0]), axis=1)
    df_faces = pd.DataFrame(faces)
    df_faces.to_csv(os.path.join(basedir, str(overlay_file).replace(".mgh", ".ply")), sep=" ", mode="a", header=False, index=False)
    print(len(df_faces.index))


    return os.path.join(basedir, str(overlay_file).replace(".mgh", ".ply"))


def ply2gltf_full(ply_file_lh, ply_file_rh):
    output_file_gltf_lh = ply2gltf_side(ply_file_lh)
    output_file_gltf_rh = ply2gltf_side(ply_file_rh)

    return output_file_gltf_lh, output_file_gltf_rh


def ply2gltf_side(ply_file):
    import vtk
    import os

    basedir = os.getcwd()

    reader = vtk.vtkPLYReader()
    reader.SetFileName(ply_file)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    # Assign actor to the renderer
    ren.AddActor(actor)

    # Export the GLTF
    writer = vtk.vtkGLTFExporter()
    writer.SetFileName(os.path.join(basedir, str(ply_file.replace(".ply", ".gltf"))))
    writer.InlineDataOn()
    writer.SetRenderWindow(renWin)
    writer.Write()

    return os.path.join(basedir, str(ply_file.replace(".ply", ".gltf")))
