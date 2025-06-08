from ij import IJ, WindowManager
from ij.plugin import ImageCalculator
from ij import Prefs
from java.awt import Window
from javax.swing import JFrame
import os

def process_pair(folder, actin_name, zo1_name, i, correction_factor):
	# Open both images from disk
	imp1 = IJ.openImage(folder + "\\" + actin_name)
	imp1.show()
	IJ.run(imp1, "16-bit", "")
	
	imp2 = IJ.openImage(folder + "\\" + zo1_name)
	imp2.show()
	IJ.run(imp2, "16-bit", "")
	
	if i not in [3,5]:
		# Run rigid registration on imp2 using imp1 as template
		IJ.run(imp2, "Rigid Registration", "initialtransform=[] n=3 tolerance=0.01 level=7 stoplevel=2 materialcenterandbbox=[] showtransformed template=" + actin_name + " measure=MutualInfo")
	
	# Multiply imp1 by 0.185
	IJ.run(imp1, "Multiply...", "value=" + str(correction_factor))
	
	# Get transformed result and subtract imp1 from it
	if i in [3, 5]:
		imp2_transformed = imp2
	else:
		imp2_transformed = WindowManager.getImage("transformed")
	calc = ImageCalculator()
	imp3 = calc.run("Subtract create", imp2_transformed, imp1)
	IJ.saveAs(imp3, "Tiff", output_folder + "processed_zo1_" + str(i + 1) + ".tif")
	imp3.show()
	
	# Threshold and convert to mask
	imp3.setAutoThreshold("Default dark no-reset")
	IJ.setRawThreshold(imp3, 13, 65535)
	Prefs.blackBackground = True
	IJ.run(imp3, "Convert to Mask", "")
	
	# Save result
	IJ.saveAs(imp3, "Tiff", output_folder + "TJ_" + str(i + 1) + ".tif")
	
	# --- Clean up: close all image and result windows but keep Fiji + script editor open ---
	
	# Close all image windows without save prompts
	for i in reversed(range(WindowManager.getImageCount())):
	    img = WindowManager.getImage(i + 1)
	    if img is not None:
	        img.changes = False
	        img.close()
	
	# Close Log and Matrix windows if they exist
	for title in ["Log", "Matrix"]:
	    win = WindowManager.getWindow(title)
	    if win is not None:
	        win.dispose()
	        
	print("Finished " + actin_name)
	

########### Main Script ###########

# Paths to input images
data_folder = "D:\\micro_data\\Rick1"
output_folder = "C:/Users/20203226/OneDrive - TU Eindhoven/8NM20 optical microscopy/paper review/pipelines/data_rick_1/"
correction_factor = 0.115

file_names = [f for f in os.listdir(data_folder) if f.endswith(".tif")]
actin_names = [x for x in file_names if x.split("_")[2] == u"ACTIN"]
zo1_names = [x for x in file_names if x.split("_")[2] == u"ZO1"]

#for i in range(len(actin_names)):
for i in range(len(actin_names)):
	if i != 4:
		process_pair(data_folder, actin_names[i], zo1_names[i], i, correction_factor)
	


