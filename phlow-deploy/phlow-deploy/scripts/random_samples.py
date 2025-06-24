import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
csv_path = os.getenv("CSV_PATH")
output_csv_path = os.getenv("OUTPUT_CSV_PATH")
output_csv_path_modified = os.getenv("OUTPUT_CSV_PATH_MODIFIED")

# Load the CSV into a DataFrame
df = pd.read_csv(csv_path)

# Sample a percentage of the DataFrame
sample_percentage = 0.9
sample_size = int(len(df) * sample_percentage)
random_sample = df.sample(n=sample_size, random_state=42)

# Save the sampled data to a new CSV file
random_sample.to_csv(output_csv_path, index=False)
print(f"Original data size: {len(df)} entries")
print(f"Randomly sampled data size: {len(random_sample)} entries")
print(f"Saved sampled data to: {output_csv_path}")

# Reload the sampled data from the newly created CSV file
df_sampled = pd.read_csv(output_csv_path)

# Split the 'reactions' column into 'reactant' and 'product' columns
df_sampled[["reactant", "product"]] = df_sampled["reactions"].str.split(
    ">>", expand=True
)

# Drop the original 'reactions' column if needed
df_sampled = df_sampled.drop(columns=["reactions"])

# Save the modified DataFrame to a new CSV file
df_sampled.to_csv(output_csv_path_modified, index=False)
print(f"Modified DataFrame:\n{df_sampled.head()}")
print(f"\nSaved modified data to: {output_csv_path_modified}")
