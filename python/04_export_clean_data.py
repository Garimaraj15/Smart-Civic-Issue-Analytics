import pandas as pd

# Feature engineered dataset load karo
df = pd.read_csv("../data/feature_engineered/feature_engineered_civic_complaints.csv")

# Export final cleaned dataset
output_path = "../data/feature_engineered/feature_engineered_civic_complaints.csv"
df.to_csv(output_path, index=False)

print("Final cleaned dataset exported successfully!")