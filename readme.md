# ImageJ/Jython Automation for Tight Junction Analysis

This repository contains a set of Jython and Python scripts designed to automate the analysis of fluorescence microscopy images in ImageJ/Fiji. The primary goal is to segment individual cells and quantify the intensity of a protein of interest (like ZO-1) specifically at the tight junctions between cells.

The pipeline involves four main stages:
1.  **Preprocessing:** Correcting for spectral bleed-through between fluorescence channels and isolating the tight junction signal.
2.  **Segmentation & Measurement:** Identifying individual cells to create Regions of Interest (ROIs) and using these ROIs to measure the tight junction signal for each cell.
3.  **Data Summarization:** Aggregating the measurement results from multiple images into a single summary table.
4.  **Visualization:** Creating composite color images and assembling them into a final montage figure.

## Prerequisites

- **[Fiji](https://fiji.sc/)**: An ImageJ distribution with bundled plugins.
  - The scripts rely on the Jython interpreter, which is included with Fiji.
  - **Required Plugin**: `Rigid Registration`. This is often part of larger plugin suites like `bUnwarpJ` or `TurboReg`. Please ensure it is installed in Fiji.
- **Python 3**: For data summarization and image combination steps.
  - **Required Libraries**: `pandas`, `matplotlib`, and `Pillow`. Install them via pip:
    ```bash
    pip install pandas matplotlib Pillow
    ```
- **Raw Data**: Your microscopy images in `.tif` format, with separate files for each channel.

## File Naming Convention

The scripts are designed to work with a specific, underscore-delimited file naming structure. This allows them to automatically identify the channel/staining for each file.

**Structure:** `ProjectName_TJ_Staining_Initials(optional)_Well#_Image#_ch##.tif`

**Examples:**
- `marijn1_TJ_ACTIN_MDL_well1_1_ch00.tif`
- `marijn1_TJ_DAPI_MDL_well1_1_ch00.tif`
- `Project_TJ_ZO1_well1_2_ch00.tif`
- `Project_TJ_ACTIN_well1_2_ch00.tif`

## Workflow & How to Run

### Step 0: Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Organize Data:**
    - Create an **input directory** for your raw `.tif` images.
    - Create an **output directory** where all processed images and results will be saved.

3.  **Configure Scripts:**
    - Open the relevant scripts (`ZO_preprocess.py`, `cell_segment_and_analysis.py`, `create_image.py`, etc.) in a text editor.
    - Update the `data_folder` and `output_folder` (or similar) variables in each script to point to your input and output directories.

### Step 1: Preprocess ZO-1 Channel (`ZO_preprocess.py`)

This script corrects for fluorescence bleed-through from the Actin channel into the ZO-1 channel and creates a mask of the tight junctions.

1.  **Determine Correction Factor:** The `correction_factor` variable compensates for Actin signal that has bled into the ZO-1 channel. This value is dataset-specific. You can determine it using the **Coloc 2** plugin in Fiji on a representative image pair (Actin and ZO-1). Update this value in the script.
    - `ZO_preprocess.py`: `correction_factor = 0.185`
    - `ZO_preprocess_rick.py`: `correction_factor = 0.115`

2.  **Run the Script in Fiji:**
    - Open Fiji.
    - Go to `File > Open...` and select `ZO_preprocess.py` or `ZO_preprocess_rick.py`.
    - Click **Run** in the Script Editor window.
    - The script will iterate through all Actin/ZO-1 image pairs in your `data_folder`, perform the corrections, and save the results.

3.  **Outputs:** For each input pair `i`, this script generates two files in your `output_folder`:
    - `processed_zo1_[i+1].tif`: The ZO-1 image after registration and subtraction of the bleed-through signal.
    - `TJ_[i+1].tif`: A binary mask highlighting the tight junctions, created by thresholding the `processed_zo1` image.

### Step 2: Segment Cells and Measure Signal (`cell_segment_and_analysis.py`)

This script uses the Actin and DAPI channels to identify individual cells (segmentation). It then uses these cell ROIs to measure the ZO-1 signal from the files generated in Step 1.

1.  **Review Parameters:** This script contains several parameters that may need tuning for your specific images to achieve accurate cell segmentation.
    - `prominence=14`: In `Find Maxima...`, controls the sensitivity of nucleus detection. Adjust based on DAPI signal.
    - `IJ.setThreshold(imp_for_mask2, 5, 65535)`: The threshold values for creating the initial cell body mask from the Actin channel.
    - `size=600-Infinity`: In `Analyze Particles...`, filters out small objects that are not cells. Adjust based on your cell size in pixels.

2.  **Run the Script in Fiji:**
    - Ensure Step 1 is complete and its output files are in the `output_folder`.
    - In Fiji, open `cell_segment_and_analysis.py`.
    - Click **Run** in the Script Editor window.

3.  **Process Overview:**
    - The script segments cells using a combination of nucleus detection (`Find Maxima`) and cell body thresholding.
    - The resulting cell outlines are added to the ROI Manager.
    - It then loads the corresponding `processed_zo1` image and `TJ` mask from Step 1.
    - It **redirects measurements** to measure the signal only from the tight junction pixels that fall within each cell's ROI.
    - It saves the measurements for each image to a separate `Results_[i+1].csv` file.

4.  **Outputs:**
    - `Results_[i+1].csv`: A CSV file with measurements for each cell found in the image.
    - Intermediate mask files (`Mask1_...`, `Mask2_...`, `Mask3_...`) are also saved for quality control.

### Step 3: Summarize All Results (`summarize csv's.py`)

This Python script aggregates the data from all the individual `Results_*.csv` files into a single, easy-to-read summary table. This should be run outside of Fiji.

1.  **Configure Path:** Make sure the `folder_path` variable in `summarize csv's.py` points to your `output_folder`.

2.  **Run the Script from your Terminal:**
    - Open a terminal or command prompt and navigate to the repository directory.
    - Run the script:
      ```bash
      python "summarize csv's.py"
      ```

3.  **Output:** The script will print a tab-separated table to the console. Each row represents one of the original images, showing statistics like the number of cells analyzed and the average value for each measurement column.

### Step 4: Create Visualization Montages (Optional)

This two-part process first creates merged color images for each well and then assembles them into a final montage.

#### Part A: Generate Individual Merged Images (`create_image.py`)

This ImageJ/Jython macro creates a composite color image (ZO-1, Actin, DAPI) for each well.

1.  **Prerequisites:** Ensure Step 1 (`ZO_preprocess.py`) has been completed, as this script requires its output files (`processed_zo1_*.tif` and `TJ_*.tif`).
2.  **Run in Fiji:**
    - Open `create_image.py` in Fiji's Script Editor.
    - Ensure the `data_folder` and `output_folder` variables are correct.
    - Click **Run**.
3.  **Output:** The script will save one `Well_[i+1].jpg` file for each image set in your output folder.

#### Part B: Assemble Montages (`combine_images.py` & `combine_images_row.py`)

These Python scripts use the JPEGs from the previous step to create a final, publication-ready montage.

1.  **Configure Scripts:**
    - Open `combine_images.py` and/or `combine_images_row.py` in a text editor.
    - Update the `image_dir` variable to your output folder.
    - If necessary, update the `cell_lines` list to match your experimental setup.
2.  **Run from Terminal:**
    - `combine_images.py`: Creates a 4x2 montage that includes negative controls.
      ```bash
      python combine_images.py
      ```
    - `combine_images_row.py`: Creates a 2x2 montage without negative controls.
       ```bash
      python combine_images_row.py
       ```
3.  **Output:**
    - `Final_Montage.jpg`: The full montage with negative controls.
    - `Final_Montage_no_neg_ctrl.jpg`: The montage without negative controls.

## Script Details

#### `ZO_preprocess.py` / `ZO_preprocess_rick.py`
- **Purpose:** To isolate the ZO-1 signal from channel bleed-through.
- **Key Steps:**
    1.  Opens an Actin and a ZO-1 image.
    2.  Aligns the ZO-1 image to the Actin image using `Rigid Registration` to correct for any minor shifts.
    3.  Multiplies the Actin image by a `correction_factor`.
    4.  Subtracts the scaled Actin image from the registered ZO-1 image.
    5.  Thresholds the resulting image to create a binary mask of the tight junctions (`TJ_...tif`).
    6.  Saves both the corrected ZO-1 image (`processed_zo1_...tif`) and the junction mask.
- **Note:** The `_rick.py` version includes a condition to skip registration for specific images, which may be necessary if registration fails or is not needed for certain wells.

#### `cell_segment_and_analysis.py`
- **Purpose:** To segment cells and perform measurements on the preprocessed ZO-1 signal.
- **Key Steps:**
    1.  **Cell Segmentation:**
        - Uses `Find Maxima` on a DAPI/Actin average projection to find cell centers (`Mask1`).
        - Uses thresholding on the Actin channel to find cell bodies (`Mask2`).
        - Combines `Mask1` and `Mask2` (`AND`) to ensure each segmented object has a nucleus.
        - Filters the result by size and fills holes to create the final cell mask (`Mask3`).
        - The ROIs from `Mask3` are added to the ROI Manager.
    2.  **Measurement:**
        - Loads the preprocessed ZO-1 image and the tight junction mask (`TJ_...tif`).
        - Multiplies them to create an image where only the tight junction pixels have intensity values.
        - Sets the measurement redirection to this final masked image (`redirect=ZO1_masked...`).
        - Measures all ROIs in the ROI Manager, capturing statistics only from the junctional pixels within each cell's boundary.
        - Saves the results table to a `.csv` file.

#### `summarize csv's.py`
- **Purpose:** To aggregate results for easy comparison.
- **Key Steps:**
    1.  Finds all `Results_*.csv` files in the output folder.
    2.  For each file, it reads the data using the `pandas` library.
    3.  It calculates the mean for all measurement columns.
    4.  It counts the total number of cells (`Total Count`) and the number of cells with an area of zero (`Zero Area Count`), which are cells without ZO-1 signal.
    5.  Prints a formatted summary to the console.

#### `create_image.py`
- **Purpose:** To create a composite, multi-channel image for visualization.
- **Key Steps:**
    1.  Opens the original Actin and DAPI images, along with the preprocessed ZO-1 image and its tight junction mask from Step 1.
    2.  Applies the junction mask to the ZO-1 image, isolating the signal of interest.
    3.  Merges the masked ZO-1 (red channel), Actin (green channel), and DAPI (blue channel) into a single color image.
    4.  Adds a scale bar and saves the result as a high-quality JPEG (`Well_*.jpg`).

#### `combine_images.py` & `combine_images_row.py`
- **Purpose:** To assemble the individual `Well_*.jpg` images into a single montage figure.
- **Key Steps:**
    1.  Loads a specific set of `Well_*.jpg` files from the output directory.
    2.  Uses `matplotlib` to arrange the images in a grid (4x2 for `combine_images.py`, 2x2 for `combine_images_row.py`).
    3.  Adds titles to each subplot based on a hardcoded list of cell line names.
    4.  Saves the final figure as a high-resolution JPEG, removing extra whitespace.