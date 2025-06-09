import os
from PIL import Image
import matplotlib.pyplot as plt

# Configuration
image_dir = "C:/Users/20203226/OneDrive - TU Eindhoven/8NM20 optical microscopy/paper review/pipelines/data_marijn_1/"
output_file = os.path.join(image_dir, "Final_Montage.jpg")

# Define cell line names
cell_lines = ["EMT", "MDA-231", "MDA-468", "MCF7"]
image_filenames = ["Well_" + str(i + 1) + ".jpg" for i in range(8)]

# Load images
images = [Image.open(os.path.join(image_dir, fname)) for fname in image_filenames]

# Setup figure
fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(8, 16))  # Adjust this if needed

for row in range(4):
    for col in range(2):
        idx = row + col * 4
        ax = axes[row, col]
        ax.imshow(images[idx])
        ax.axis('off')

        label = cell_lines[row]
        if col == 1:
            label += " (neg ctrl)"
        ax.set_title(label, fontsize=14, fontweight='bold')  # Slightly smaller font

# Remove spacing between plots
plt.subplots_adjust(wspace=0.01, hspace=-0.01)

# Optional: Also remove padding when saving
plt.savefig(output_file, dpi=450, bbox_inches='tight', pad_inches=0)
plt.close()

print("Saved final montage to:", output_file)
