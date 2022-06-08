import pandas as pd

from SQRL import SQLHandler

import re

variant_reader = re.compile("([ACGT-]*)([|LUpm])([ACGT-]+)@(\w+(?: \w+)*)@@(\d+)\[\[([ACGTN]+)\{\{([ACGTN]+)::.*;;(.*)")

sqrl = SQLHandler()

# load data_list
data_sets = pd.read_excel("mutation_database_info.xlsx", "data_sets")

def get_type(p, c):
    if not p:
        return "Allelic Fraction Shift"
    
    if "-" in p:
        if len(p) > 1:
            return ">1 bp Insertion"
        else: return "1 bp Insertion"
    
    if "-" in c:
        if len(p) > 1:
            return ">1 bp Deletion"
        else: return "1 bp Deletion"
    
    if len(p) > 1: return ">1 bp Substitution"
    if (p in "GA" and c in "GA") or\
       (p in "CT" and c in "CT"):
        return "Transition"
    return "Transversion"


flag_map = {
    "|": "Point Mutation",
    "L": "Loss of Heterozygosity",
    "U": "Ambiguous Change",
    "p": "Plus CNV",
    "m": "Minus CNV"
}

i = 0;

for name in data_sets.columns:
    iso_name = name.split()[0]
    IID = sqrl.get_isolate(iso_name)
    if not IID: continue
    
    for variant in data_sets[name]:
        if (type(variant) != str): continue
        if not variant: continue
        if not (match := variant_reader.match(variant)):
            continue
        
        parent = match[1]
        flag = match[2]
        child = match[3]
        chromosome = match[4]
        chromosome = int(chromosome.split("_")[0][3:])
        position = match[5]
        F5 = match[6]
        F3 = match[7]
        extra = match[8]

        typ = get_type(parent, child)
        gmid = sqrl.add_gen_mut(parent, child, typ)
        sqrl.add_variant(IID, gmid, chromosome, position, flag_map[flag], F5[-10:], F3[:10], extra)
        
        i += 1
        print("\rProcessed:", i, end="")
        
print(f"\rDone! {i} Variants     ")
sqrl.commit()