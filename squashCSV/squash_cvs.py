import pandas as pd
import os
import random

# Define file paths
folder_path = "data"
facilities_file = os.path.join(folder_path, "Health_facilities.csv")
services_file = os.path.join(folder_path, "health_services.csv")
insurance_file = os.path.join(folder_path, "insuarance.csv")

# Load the datasets
facilities_df = pd.read_csv(facilities_file)
services_df = pd.read_csv(services_file)
insurance_df = pd.read_csv(insurance_file)

# Assign random services and insurances to facilities
facilities_df["Assigned Service"] = facilities_df.apply(lambda x: random.choice(services_df["Service"]), axis=1)
facilities_df["Assigned Insurance"] = facilities_df.apply(lambda x: random.choice(insurance_df["name of insurance"]), axis=1)

# Save the updated dataset
output_file = os.path.join(folder_path, "Updated_Health_Facilities.csv")
facilities_df.to_csv(output_file, index=False)

print(f"Updated file saved as: {output_file}")
