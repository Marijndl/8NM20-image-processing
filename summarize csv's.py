import pandas as pd
import glob
import os

# Define the folder path
folder_path = r"C:\Users\20203226\OneDrive - TU Eindhoven\8NM20 optical microscopy\paper review\pipelines\data_marijn_1"

# Find all matching CSV files
csv_files = sorted(glob.glob(os.path.join(folder_path, "Results_*.csv")))

# Store results for all files
all_means = []

for file in csv_files:
    df = pd.read_csv(file, sep=None, engine='python')  # auto-detect separator
    row_count = len(df)

    zero_area_count = 0
    if "Area" in df.columns:
        # Convert "Area" to numeric, coerce errors to NaN
        df["Area"] = pd.to_numeric(df["Area"], errors='coerce')
        # Count rows where Area == 0 (ignoring NaNs)
        zero_area_count = (df["Area"] == 0).sum()

    df_numeric = df.apply(pd.to_numeric, errors='coerce')  # convert non-numeric to NaN
    means = df_numeric.mean(skipna=True)  # calculate means
    all_means.append((row_count, zero_area_count, os.path.basename(file), means))

# Print header
header = ["Total Count", "Zero Area Count", "Filename"] + list(all_means[0][3].index)
print("\t".join(header))

# Print each row
for total_count, zero_area_count, filename, means in all_means:
    row = [str(total_count), str(zero_area_count), filename] + [f"{v:.4f}" if pd.notna(v) else "NaN" for v in means.values]
    print("\t".join(row))