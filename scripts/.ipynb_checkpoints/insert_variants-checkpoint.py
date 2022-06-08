import pandas as pd

from SQRL import SQLHandler


sqrl = SQLHandler()

# load feture_list
data_sets = pd.read_excel("mutation_database_info.xlsx", "data_sets")

# Replace column names for ref

print(data_sets.columns)