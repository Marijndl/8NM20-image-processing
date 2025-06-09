import os
from PIL import Image
import matplotlib.pyplot as plt

# Configuration
image_dir = "C:/Users/20203226/OneDrive - TU Eindhoven/8NM20 optical microscopy/paper review/pipelines/data_marijn_1/"
output_file = os.path.join(image_dir, "Final_Montage_no_neg_ctrl.jpg")

# Define cell line names
cell_lines = ["EMT", "MDA-231", "MDA-468", "MCF7"]
# Only use images from first column (no negative control), so indexes: 0,1,2,3
image_filenames = ["Well_" + str(i + 1) + ".jpg" for i in range(4)]

# Load images
images = [Image.open(os.path.join(image_dir, fname)) for fname in image_filenames]

# Setup figure: 2 rows, 2 columns
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

for row in range(2):
    for col in range(2):
        index = row * 2 + col
        ax = axes[row, col]
        ax.imshow(images[index])
        ax.axis('off')

        label = cell_lines[index]
        ax.set_title(label, fontsize=14, fontweight='bold')

# Adjust spacing
plt.subplots_adjust(wspace=0.01, hspace=-0.3)

# Save figure
plt.savefig(output_file, dpi=600, bbox_inches='tight', pad_inches=0)
plt.close()

print("Saved no negative control montage to:", output_file)
