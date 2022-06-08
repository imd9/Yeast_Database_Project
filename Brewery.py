#!/usr/bin/python3
# -*- coding: utf8 -*-

# imports
import pymysql
import cgitb
import cgi
import pandas as pd
import decimal
import json

cgitb.enable()

# some constants
#   mysql credentials
mysql_creds = {
    "host": "bioed",
    "port": 4253,
    "user": "Group_P",
    "password": "Group_P",
    "database": "Group_P"
}

#   mutation code map
codemap = {
    "-A": "+A",
    "-G": "+G",
    "-C": "+C",
    "-T": "+T",
    "A-": "-A",
    "T-": "-T",
    "C-": "-C",
    "G-": "-G",
    "AG": "A→G",
    "AC": "A→C",
    "AT": "A→T",
    "CG": "C→G",
    "CA": "C→A",
    "CT": "C→T",
    "GA": "G→A",
    "GC": "G→C",
    "GT": "G→T",
    "TG": "T→G",
    "TC": "T→C",
    "TA": "T→A",
    '>1 bp Insertion': '>1 bp Insertion',
    '>1 bp Deletion':'>1 bp Deletion',
    '>1 bp Substitution': '>1 bp Substitution',
    'Allelic Fraction Shift': 'Allelic Fraction Shift'
}

def fix(d):
    if d % 1 > 0: return float(d)
    return int(d)

def do_query(query, *args):
    with pymysql.connect(**mysql_creds) as cnct,\
        cnct.cursor() as crs:
        crs.execute(query, args)
        data = crs.fetchall()
    return data

# functions
#   get mutations
def get_muts(sid):

    query = """
    select flag, concat(old_allele, new_allele) as code, chromosome, floor(position/10000) as bin, count(*)
    from Isolate straight_join Variant using(iid) straight_join GenotypeMutation using(gmid)
    where sid= %s and type not in (">1 bp Deletion", ">1 bp Insertion", ">1 bp Substitution", "Allelic Fraction Shift")
    group by flag, code, chromosome, bin
    union
    select flag, type as code, chromosome, floor(position/10000) as bin, count(*)
    from Isolate straight_join Variant using(iid) straight_join GenotypeMutation using(gmid)
    where sid= %s and type in (">1 bp Deletion", ">1 bp Insertion", ">1 bp Substitution", "Allelic Fraction Shift")
    group by flag, code, chromosome, bin
    """

    data = do_query(query, sid, sid)
    df = pd.DataFrame(data)
    
    data_map = {}
    
    if not data: return data_map
    
    for flag in df[0].unique():
        flag_set = df[df[0]==flag]
        if flag_set.empty: continue

        data_map[flag] = {}
        for code in df[1].unique():
            mut = codemap[code]
            mut_set = flag_set[df[1]==code]
            if mut_set.empty: continue

            data_map[flag][mut] = []
            for xrmi in range(1,17):
                xrm_set = mut_set[df[2]==xrmi]
                data_map[flag][mut].append(xrm_set[[3,4]].values.tolist())
    
    return data_map

#   get strains
def get_strains():

    query = """select sid, bs.name, group_concat(em.name separator " ") as name
    from Strain join Components using(sid)
	join EngineeredMutation em using(emid)
	join BackgroundStrain bs using (bsid)
    group by sid
    order by sid"""

    data = do_query(query)
    output = [[i, f"{n} {m}"] for (i, n, m) in data]

    return output
    
def get_strain_summary(sid):

    query = """
    select sid, COUNT(iid), sum(generations), sum(queryable), sum(va), sum(pnt), sum(los) 
    from (
    select sid ,iid, generations, queryable, count(flag) as va, sum(flag='Point Mutation') as pnt, 
    sum(flag = 'Loss of Heterozygosity') as los, 
    sum(flag = 'Ambigous Change') as ac  
    from Isolate i join Variant v using(iid)
    where sid = %s
    group by iid
    ) as T ;
    """

    out = do_query(query, sid)

    if not out : return out
    return [[int(o) if o is not None else None for o in row] for row in out]

def get_strain_summaries():

    query = """
    select bg, comps, COUNT(iid), sum(generations), sum(queryable),
        sum(va), sum(pnt), sum(los), sum(ac)
    from 
    (   select sid, iid, generations, queryable, count(flag) as va,
            sum(flag='Point Mutation') as pnt,
            sum(flag = 'Loss of Heterozygosity') as los,
            sum(flag = 'Ambiguous Change') as ac  
        from Isolate i left join Variant v using(iid)
        group by iid
    ) as T right join
    (   select sid, bs.name as bg, group_concat(em.name separator " ") as comps
        from Strain join Components using(sid)
            join EngineeredMutation em using(emid)
            join BackgroundStrain bs using (bsid)
        group by sid
    ) as P using(sid)
    group by sid
    order by sid;"""

    out = do_query(query)

    if not out : return out
    return [[fix(o) if type(o) == decimal.Decimal else o for o in row] for row in out]

#   get features in range
def get_feat_inrange():

    input = fields.getvalue("")

    query = """"""

    data = do_query(query)
    
    df = pd.DataFrame(data)

    return [[fix(o) if type(o) == decimal.Decimal else o for o in row] for row in out]

# get festures summary
def get_feat_summaries():

    query = """select *, total_length/12055736 as genome_fraction
        from (select type, count(*) as count,sum(complement) as on_comp_strand, sum(end-start+1) as total_length
		from Feature
		group by type) as H""" 

    data = do_query(query)
    return [[fix(o) if type(o) == decimal.Decimal else o for o in row] for row in data]

def get_feature_list(typ):
    
    query = """
    select name, chromosome, start, end, complement, xrefs
    from Feature
    where type = %s
    """
    
    data = do_query(query, typ)
    return data

def get_isolate_list(sid):
    query = """
    select labid, generations, queryable
    from Isolate
    where sid = %s
    """
    
    data = do_query(query, sid)
    return data


functionmap = {
    "mutations": get_muts,
    "strains": get_strains,
    "strain_summ" : get_strain_summary,
    "strain_summs": get_strain_summaries,
    "feat_summ" : get_feat_summaries,
    "feat_list" : get_feature_list,
    "iso_list" : get_isolate_list
}

argmap = {
    "mutations": ["sid"],
    "strains": [],
    "strain_summ" : ["sid"],
    "strain_summs": [],
    "feat_summ" : [],
    "feat_list" : ["feature"],
    "iso_list" : ["strain"]
}

if __name__ == "__main__":
    print("Content-type: text/html\n")
    fields = cgi.FieldStorage()
    if (fields):
        selector = fields.getvalue("selector")
        function = functionmap[selector]
        args = [fields.getvalue(a) for a in argmap[selector]]
        out = function(*args)
        print(json.dumps(out))