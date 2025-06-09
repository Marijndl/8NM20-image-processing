import os

from ij import IJ, WindowManager
from ij import Prefs
from ij.plugin import ImageCalculator
from java.awt import Window
from javax.swing import JFrame

def process_pair(folder, actin_name, dapi_name, i, output_folder):
    # Open both images from disk
    im_actin = IJ.openImage(folder + "\\" + actin_name)
    IJ.run(im_actin, "16-bit", "")

    im_dapi = IJ.openImage(folder + "\\" + dapi_name)
    IJ.run(im_dapi, "16-bit", "")

    # Process ZO1 iamge
    ic = ImageCalculator()
    imp_zo1 = IJ.openImage(output_folder + "/processed_zo1_" + str(i + 1) + ".tif")
    imp_zo1_mask = IJ.openImage(output_folder + "/TJ_" + str(i + 1) + ".tif")
    IJ.run(imp_zo1_mask, "Divide...", "value=255.000")
    zo1_masked = ic.run("Multiply create", imp_zo1, imp_zo1_mask)
    zo1_masked.setTitle("ZO1_masked" + str(i + 1))
    IJ.run(zo1_masked, "Multiply...", "value=10.000")

    IJ.run("Merge Channels...",
           "c1=[Result of processed_zo1_1.tif] c2=marijn1_TJ_ACTIN_MDL_well1_1_ch00.tif c3=marijn1_TJ_DAPI_MDL_well1_1_ch00.tif create keep")
    im_merged = WindowManager.getImage("Composite")
    IJ.run(im_merged, "Scale Bar...", "width=20 height=20 font=40 horizontal bold overlay")

    # Save image
    IJ.saveAs(im_merged, "Jpeg", output_folder + "Well_" + str(i + 1) + ".jpg")

    # Close all image windows without save prompts
    for i in reversed(range(WindowManager.getImageCount())):
        img = WindowManager.getImage(i + 1)
        if img is not None:
            img.changes = False
            img.close()

    print("Processed Well_" + str(i + 1) + ".jpg")

########### Main Script ###########

# Paths to input images
data_folder = "D:\\micro_data\\Marijn1"
output_folder = "C:/Users/20203226/OneDrive - TU Eindhoven/8NM20 optical microscopy/paper review/pipelines/data_marijn_1/"

file_names = [f for f in os.listdir(data_folder) if f.endswith(".tif")]
actin_names = sorted([x for x in file_names if x.split("_")[2] == u"ACTIN"])
dapi_names = sorted([x for x in file_names if x.split("_")[2] == u"DAPI"])

# for i in range(len(actin_names)):
for i in range(len(actin_names)):
    process_pair(data_folder, actin_names[i], dapi_names[i], i, output_folder)