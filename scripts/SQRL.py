import sys
from pymysql import connect, Error as psqlErr
        
class SQLHandler:
    
    def __init__(self):
        self.cnct = connect(
            host="bioed",
            port=4253, 
            user="Group_P",
            password="Group_P",
            database="Group_P")
            
        self.crs = self.cnct.cursor()
    
    
    def add_isolate(self, labid, sid, gnrs, qrbl):
        """
        Retrieves the iid of the isolate under the given labid from the database.
        If it's not there, it inserts it and returns it's iid.
        """
        
        if (iid := self.get_isolate(labid)):
            return iid
        
        if not self.safely("insert into Isolate (labid, sid, generations, queryable) values (%s, %s, %s, %s)", labid, sid, gnrs, qrbl):
            print(f"Failed to insert {labid} into Isolate table.")
            return None
        
        self.safely("select last_insert_id()")
        return self.crs.fetchall()[0][0]
    
    def get_isolate(self, labid):
        if not self.safely("select iid from Isolate where labid = %s", labid):
            print("Could not query Isolate table!")
            return None
        
        if (tab := self.crs.fetchall()):
            return tab[0][0]
        return None
    
    
    def add_gen_mut(self, parent, child, typ):
        if (gmid := self.get_gen_mut(parent, child)):
            return gmid
        
        if not self.safely("insert into GenotypeMutation (old_allele, new_allele, type) values (%s, %s, %s)", parent, child, typ):
            print(f"Failed to insert {parent}→{child} into GenotypeMutation table.")
            return None
        
        self.safely("select last_insert_id()")
        return self.crs.fetchall()[0][0]
    
    def get_gen_mut(self, parent, child):
        if not self.safely("""
            select gmid
            from GenotypeMutation
            where old_allele = %s and new_allele = %s""", parent, child):
            print("Could not query GenotypeMutation table!")
            return None
        
        if (tab := self.crs.fetchall()):
            return tab[0][0]
        return None
    
    
    def add_background(self, name):
        """
        Retrieves the bsid of the background stain under the given name from the database.
        If it's not there, it inserts it and returns it's bsid.
        """
        
        if (bsid := self.get_background(name)):
            return bsid
        
        if not self.safely("insert into BackgroundStrain (name) values (%s);", name):
            print(f"Failed to insert {name} into BackgroundStrain table.")
            return None
        
        self.safely("select last_insert_id()")
        return self.crs.fetchall()[0][0]
    
    def get_background(self, name):
        if not self.safely("select bsid from BackgroundStrain where name = %s;", name):
            print("Could not query BackgroundStrain table!")
            return None
        
        if (tab := self.crs.fetchall()):
            return tab[0][0]
        return None
    
    
    def add_variant(self, iid, gmid, chrom, pos, flag, f5, f3, extra):
        if not self.safely("""
            insert into Variant (iid, gmid, chromosome, position, flag, flank5, flank3, extra)
            values (%s, %s, %s, %s, %s, %s, %s, %s)""",
            iid, gmid, chrom, pos, flag, f5, f3, extra):
            print(f"Failed to insert {iid}, {gmid}, {chrom}, {pos} into Variant table.")
    
    
    def add_eng_mut(self, name):
        """
        Retrieves the emid of the engineered mutation under the given name from the database.
        If it's not there, it inserts it and returns it's emid.
        """
        
        if not self.safely("select emid from EngineeredMutation where name = %s;", name):
            print("Could not query EngineeredMutation table!")
            return None
        
        if (tab := self.crs.fetchall()):
            return tab[0][0]
        
        if not self.safely("insert into EngineeredMutation (name) values (%s);", name):
            print(f"Failed to insert {name} into EngineeredMutation table.")
            return None
        
        self.safely("select last_insert_id()")
        return self.crs.fetchall()[0][0]
    
    
    def add_component(self, sid, emid):
        if not self.safely("""
            insert into Components (sid, emid)
            values (%s, %s)""",
            sid, emid):
            print(f"Failed to insert {sid}, {emid} into Components table.") 
    
    
    def new_strain(self, bsid):
        if not self.safely("""
            insert into Strain (bsid)
            values (%s)""",
            bsid):
            print(f"Failed to insert {bsid}, into Strain table.")
            return None
        
        self.safely("select last_insert_id()")
        return self.crs.fetchall()[0][0]
        
    
    
    def add_feature(self, name, typ, chromosome, start, end, comp, bsid, dbxref):
         if not self.safely("""
            insert into Feature (name, type, chromosome, start, end, complement, bsid, xrefs)
            values (%s, %s, %s, %s, %s, %s, %s, %s)""",
            name, typ, chromosome, start, end, comp, bsid, dbxref):
            print(f"Failed to insert {name} into Feature table.") 
    
    
    def safely(self, query, *args):
        try:
            self.crs.execute(query, args)
            return True
        except psqlErr as e:
            print(e)
            return False
        
    
    def __del__(self):
        self.crs.close()
        self.cnct.close()
        
    def commit(self):
        self.safely("commit;")