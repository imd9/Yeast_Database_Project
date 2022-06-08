import pandas as pd

from SQRL import SQLHandler


sqrl = SQLHandler()

# load reference_list
ref_list = pd.read_excel("mutation_database_info.xlsx", "reference_list")
ref_list = ref_list[pd.notna(ref_list['reference'])]

strain_map = {}

# loop over rows of reference_list
for index, row in ref_list.iterrows():
    complete_strain = row['Data set']
    if "*" in complete_strain: continue;
    
    background_strain = row['reference']
    #print(background_strain, " -- " , complete_strain)
    
    back_id = sqrl.add_background(background_strain)
    strain_id = sqrl.new_strain(back_id)
    
    strain_map[complete_strain] = strain_id

    engineered_muts = complete_strain.split()
    for i, mut in enumerate(engineered_muts):
        if mut in ["W303", "S288C", "(het)"]: continue
        if mut == "WT": mut = "wt"
        if mut[-1] in ['.', ',']: mut = mut[:-1]
        ##print(mut, end=' ')
        if (i < len(engineered_muts) - 1) and engineered_muts[i+1] == "(het)":
            mut += " (het)"
        
        mut_id = sqrl.add_eng_mut(mut)
        sqrl.add_component(strain_id, mut_id)
        
    print("\rOn ref_list: ", index, end="")

print(f"\rDone! {index} Strains")
    
# load iso_list
iso_list = pd.read_excel("mutation_database_info.xlsx", "iso_list")
iso_list.columns = ['A', 'B', 'C', 'D', 'E','F','G','H','I','J','K','L','M','N','O','P']
iso_list = iso_list[pd.notna(iso_list['H'])]

# loop over rows of iso_list
for index, row in iso_list.iterrows():
    complete_strain = row['D']
    if pd.isna(complete_strain): continue
    lab_id = row['C']
    generations = row['E']
    queryable = row['F']
    
    strain_id = strain_map[complete_strain]
    iso_id = sqrl.add_isolate(lab_id, strain_id, generations, queryable)
        
    print('\rOn iso_list: ', index, end='')

print(f"\rDone! {index} Isolates")

sqrl.commit()