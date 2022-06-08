import pandas as pd

from SQRL import SQLHandler


sqrl = SQLHandler()

# load feature_list
feature_list = pd.read_excel("mutation_database_info.xlsx", "features")

# Replace column names for ref

feature_list.columns = ['A', 'B', 'C', 'D', 'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

bsid = sqrl.get_background("L03 (ref v2)")

for index, row in feature_list.iterrows():
    chromosome = row['I']
    name = row['D']
    typ = row['E']
    comp = row['J']
    qualifiers = row['G']
    start = row['K'] % 10000000
    end = row['L'] % 10000000

    dbxref = []

    if (type(qualifiers) == str):
        for piece in qualifiers.split(";"):
            if not "=" in piece: continue
            bits = piece.strip().split("=")
            if (len(bits) > 2): continue
            what, content = bits
            if (what != "/db_xref"): continue
            dbxref.append(content[1:-1])
    
    dbxref = ";".join(dbxref)

    print("\rOn feature_list: ", index, end="")
    
    sqrl.add_feature(name, typ, chromosome, start, end, comp, bsid, dbxref)
print(f"\rDone! {index} Features      ")

sqrl.commit()