import os

from ij import IJ, WindowManager
from ij.plugin import ImageCalculator

def process_pair(folder, actin_name, dapi_name, i, output_folder):
    # Open ACTIN and DAPI images
    im_actin = IJ.openImage(folder + "\\" + actin_name)
    IJ.run(im_actin, "16-bit", "")
    im_actin.show()

    im_dapi = IJ.openImage(folder + "\\" + dapi_name)
    IJ.run(im_dapi, "16-bit", "")
    im_dapi.show()

    # Open processed ZO1 image and corresponding mask
    imp_zo1 = IJ.openImage(output_folder + "/processed_zo1_" + str(i + 1) + ".tif")
    imp_zo1.show()

    imp_zo1_mask = IJ.openImage(output_folder + "/TJ_" + str(i + 1) + ".tif")
    imp_zo1_mask.show()
    IJ.run(imp_zo1_mask, "Divide...", "value=255.000")

    # Apply mask to ZO1 image
    ic = ImageCalculator()
    zo1_masked = ic.run("Multiply create", imp_zo1, imp_zo1_mask)
    title_zo1_masked = "ZO1_masked_" + str(i + 1)
    zo1_masked.setTitle(title_zo1_masked)
    zo1_masked.show()
    IJ.run(zo1_masked, "Multiply...", "value=10.000")

    # Merge channels using image titles dynamically
    merge_command = "c1=" + title_zo1_masked + " c2=" + im_actin.getTitle() + " c3=" + im_dapi.getTitle() + " create keep"
    IJ.run("Merge Channels...", merge_command)

    im_merged = WindowManager.getImage("Composite")
    IJ.run(im_merged, "Scale Bar...", "width=100 height=20 font=60 horizontal bold overlay")

    # Save the merged image
    IJ.saveAs(im_merged, "Jpeg", output_folder + "Well_" + str(i + 1) + ".jpg")

    # Close all images
    for j in reversed(range(WindowManager.getImageCount())):
        img = WindowManager.getImage(j + 1)
        if img is not None:
            img.changes = False
            img.close()

    print("Processed Well_" + str(i + 1) + ".jpg")

########### Main Script ###########

data_folder = "D:\\micro_data\\Marijn1"
output_folder = "C:/Users/20203226/OneDrive - TU Eindhoven/8NM20 optical microscopy/paper review/pipelines/data_marijn_1/"

file_names = [f for f in os.listdir(data_folder) if f.endswith(".tif")]
actin_names = sorted([x for x in file_names if "ACTIN" in x])
dapi_names = sorted([x for x in file_names if "DAPI" in x])

for i in range(len(actin_names)):
    process_pair(data_folder, actin_names[i], dapi_names[i], i, output_folder)

