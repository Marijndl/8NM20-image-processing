from ij import IJ, WindowManager, ImagePlus, ImageStack
from ij.plugin import ImageCalculator, ZProjector, Duplicator
from ij.measure import ResultsTable
from ij.plugin.filter import Analyzer
from ij.plugin.frame import RoiManager
from ij import Prefs
import os
import time


def process_images(data_folder, actin_file_name, dapi_file_name, output_folder, file_index):
    print("Processing: " + actin_file_name + " and " + dapi_file_name)

    # --- Open and process ACTIN image ---
    imp_actin = IJ.openImage(os.path.join(data_folder, actin_file_name))
    imp_actin.setTitle("Actin_Proc_" + str(file_index + 1))
    IJ.run(imp_actin, "16-bit", "")
    IJ.run(imp_actin, "Median...", "radius=2")
    IJ.run(imp_actin, "Subtract Background...", "rolling=150 disable")

    # --- Open and process DAPI image ---
    imp_dapi = IJ.openImage(os.path.join(data_folder, dapi_file_name))
    imp_dapi.setTitle("DAPI_Proc_" + str(file_index + 1))
    IJ.run(imp_dapi, "16-bit", "")
    IJ.run(imp_dapi, "Median...", "radius=8")
    IJ.run(imp_dapi, "Subtract Background...", "rolling=150 disable")

    # --- Combine processed images into a stack ---
    combined_stack = ImageStack(imp_actin.getWidth(), imp_actin.getHeight())
    combined_stack.addSlice(imp_actin.getProcessor().duplicate())
    combined_stack.addSlice(imp_dapi.getProcessor().duplicate())
    imp_combined = ImagePlus("Combined_Stack_" + str(file_index+1), combined_stack)

    # --- Z-Project the combined stack ---
    imp_avg_projection = ZProjector.run(imp_combined, "avg")  # Returns new ImagePlus
    imp_avg_projection.setTitle("Z_Average_" + str(file_index+1))

    # --- Create Mask 1 (from Find Maxima on Z-projection) ---
    dup_for_maxima = Duplicator().run(imp_avg_projection)
    dup_for_maxima.setTitle("Dup_For_Maxima_" + str(file_index+1))
    IJ.run(dup_for_maxima, "Find Maxima...", "prominence=14 strict exclude output=[Segmented Particles]")
    imp_mask1 = WindowManager.getImage("Dup_For_Maxima_" + str(file_index+1) + " Segmented")
    imp_mask1.setTitle("Mask1_Maxima_" + str(file_index + 1))
    IJ.saveAs(imp_mask1, "Tiff", os.path.join(output_folder, "Mask1_" + str(file_index+1) + ".tif"))

    # --- Create Mask 2 (from thresholding the Z-projection) ---
    imp_for_mask2 = Duplicator().run(imp_avg_projection)
    imp_for_mask2.setTitle("Image_For_Mask2_" + str(file_index + 1))
    imp_for_mask2.setAutoThreshold("Default dark no-reset")
    IJ.setThreshold(imp_for_mask2, 5, 65535)
    IJ.run(imp_for_mask2, "Smooth", "")
    IJ.setThreshold(imp_for_mask2, 5, 65535)  # Re-apply threshold
    Prefs.blackBackground = True
    IJ.run(imp_for_mask2, "Convert to Mask", "")  # Modifies imp_for_mask2
    imp_for_mask2.setTitle("Mask2_Thresholded_" + str(file_index + 1))
    IJ.saveAs(imp_for_mask2, "Tiff", os.path.join(output_folder, "Mask2_" + str(file_index + 1) + ".tif"))

    # --- Combine Mask1 and Mask2 using Image Calculator ---
    ic = ImageCalculator()
    imp_mask_combined = ic.run("AND create", imp_mask1, imp_for_mask2)
    imp_mask_combined.setTitle("Combined_AND_Mask_" + str(file_index + 1))

    # --- Process the combined mask (Mask3 logic) ---
    # Analyze Particles with "show=Masks" creates a new image.
    # Assume the new mask image becomes active or has a predictable title.
    IJ.run("Set Measurements...",
           "area mean standard modal min perimeter shape feret's integrated median area_fraction display nan redirect=None decimal=3")
    IJ.run(imp_mask_combined, "Analyze Particles...", "size=600-Infinity pixel show=Masks exclude add")
    # This typically creates an image named "Mask of [original image title]" or simply "Masks" if title is too long,
    # or it becomes the active image. For simplicity, we'll grab the active image.
    # If multiple images are open, this might be risky.
    imp_mask3 = WindowManager.getCurrentImage()  # Get the newly created mask image
    # If the "Mask of ..." image is not the active one, you might need:
    # imp_mask3 = WindowManager.getImage("Mask of " + imp_mask_combined.getTitle())
    imp_mask3.setTitle("Mask3_Particles_" + str(file_index + 1))

    IJ.run(imp_mask3, "Invert LUT", "")
    IJ.run(imp_mask3, "Fill Holes", "")
    IJ.saveAs(imp_mask3, "Tiff", os.path.join(output_folder, "Mask3_" + str(file_index + 1) + ".tif"))
    
    imp_zo1 = IJ.openImage(output_folder + "/processed_zo1_" + str(file_index + 1) + ".tif")
    imp_zo1_mask = IJ.openImage(output_folder + "/TJ_" + str(file_index + 1) + ".tif")
    IJ.run(imp_zo1_mask, "Divide...", "value=255.000")
    zo1_masked = ic.run("Multiply create", imp_zo1, imp_zo1_mask)
    zo1_masked.setTitle("ZO1_masked" + str(file_index + 1))	
    zo1_masked.show()
    
    # Get the ROI Manager instance
    rm = RoiManager.getInstance()
    if rm is None:
    	rm = RoiManager()
	rm.reset()    

    # --- Set Measurements and Analyze Particles (final measurements) ---
    time.sleep(0.5)
    IJ.run("Set Measurements...",
           "area mean standard modal min perimeter shape feret's integrated median area_fraction limit display nan redirect=ZO1_masked" + str(file_index + 1) + " decimal=3")
    rt = ResultsTable.getResultsTable()
    rt.reset()  # Clear previous results from the main table
    
    # Set threshold to only select non-black pixels.
    zo1_masked.setAutoThreshold("Default dark no-reset")
    IJ.setRawThreshold(zo1_masked, 1, 65535)
    Prefs.blackBackground = True
    
    # Use ROI manager to get results
    roi_count = rm.getCount()
    rm.setSelectedIndexes(range(roi_count))
    rm.runCommand("Measure")
   
#    IJ.run(imp_mask3, "Analyze Particles...", "size=600-Infinity pixel show=Outlines display exclude clear summarize")
    rt = ResultsTable.getResultsTable()
    rt.save(os.path.join(output_folder, "Results_" + str(file_index+1) + ".csv"))
    rt.reset()
    # Close the window (if open)
    win = WindowManager.getFrame("Results")
    if win is not None:
    	win.close()
    
    # --- Clean up image windows for this pair ---
    # Close intermediate images explicitly to manage memory and window clutter.
    # Original images are not explicitly closed here but will be handled by general cleanup if desired.
    if imp_actin and imp_actin.isVisible(): imp_actin.close()
    if imp_dapi and imp_dapi.isVisible(): imp_dapi.close()
    if imp_combined and imp_combined.isVisible(): imp_combined.close()
    if imp_avg_projection and imp_avg_projection.isVisible(): imp_avg_projection.close()
    if dup_for_maxima and dup_for_maxima.isVisible(): dup_for_maxima.close()
    if imp_mask1 and imp_mask1.isVisible(): imp_mask1.close()
    if imp_for_mask2 and imp_for_mask2.isVisible(): imp_for_mask2.close()
    if imp_mask_combined and imp_mask_combined.isVisible(): imp_mask_combined.close()

    # imp_mask3 and the "Outlines" image from Analyze Particles might be kept open for review.
    # If you want to close them too:
    # if imp_mask3 and imp_mask3.isVisible(): imp_mask3.close()
    # outlines_title = "Outlines of " + imp_mask3.getTitle() # Or whatever it's named
    # imp_outlines = WindowManager.getImage(outlines_title)
    # if imp_outlines and imp_outlines.isVisible(): imp_outlines.close()
    
	# Close all image windows without save prompts
    print("Finished: " + str(file_index + 1))
    rm.reset()
    for i in reversed(range(WindowManager.getImageCount())):
	    img = WindowManager.getImage(i + 1)
	    if img is not None:
	        img.changes = False
	        img.close()


########### Main Script ###########

data_folder = "D:\\micro_data\\Marijn1"
output_folder = "C:/Users/20203226/OneDrive - TU Eindhoven/8NM20 optical microscopy/paper review/pipelines/data_marijn_1/"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_names = [f for f in os.listdir(data_folder) if f.endswith(".tif")]
actin_names = [x for x in file_names if x.split("_")[2] == u"ACTIN"]
dapi_names = [x for x in file_names if x.split("_")[2] == u"DAPI"]


#for i in range(1):
#i=1 #well number
for i in range(len(actin_names)):
	process_images(data_folder, actin_names[i], dapi_names[i], output_folder, i)

# # Optional: Final cleanup of all remaining image windows and utility windows
# close_all_at_end = False  # Set to True to close everything
# if close_all_at_end:
#     while WindowManager.getImageCount() > 0:
#         img = WindowManager.getCurrentImage()
#         if img:
#             img.changes = False  # Don't ask to save
#             img.close()
#
#     utility_windows_to_close = ["Log", "Results", "Summary", "ROI Manager"]  # Add others if needed
#     for title in utility_windows_to_close:
#         win = WindowManager.getWindow(title)
#         if win is not None:
#             win.dispose()

print("Script finished.")