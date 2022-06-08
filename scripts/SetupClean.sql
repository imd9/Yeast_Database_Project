
drop table if exists Components;
drop table if exists EngineeredMutation;

drop table if exists Variant;
drop table if exists GenotypeMutation;
drop table if exists Isolate;

drop table if exists Strain;
drop table if exists Feature;
drop table if exists BackgroundStrain;


create table BackgroundStrain (
  bsid int auto_increment not null,
  name varchar(15) not null,
  primary key (bsid)
) character set 'utf8';

create table EngineeredMutation (
  emid int auto_increment not null,
  name varchar(20) not null,
  primary key (emid)
) character set 'utf8';

create table Strain (
  sid int auto_increment not null,
  bsid int not null,
  primary key (sid),
  foreign key (bsid) references BackgroundStrain (bsid)
);

create table Components (
  sid int not null,
  emid int not null,
  primary key (emid, sid),
  foreign key (emid) references EngineeredMutation (emid),
  foreign key (sid) references Strain (sid)
);

create table Isolate (
  iid int auto_increment not null,
  labid varchar(10) not null,
  generations float,
  queryable int,
  sid int not null,
  t0id int,
  primary key (iid),
  foreign key (sid) references Strain (sid),
  foreign key (t0id) references Isolate (iid)
);

create table GenotypeMutation (
  gmid int auto_increment not null,
  old_allele varchar(100),
  new_allele varchar(100),
  type enum("Transition", "Transversion", ">1 bp Substitution",
            "1 bp Deletion", ">1 bp Deletion",
            "1 bp Insertion", ">1 bp Insertion",
            "Allelic Fraction Shift") not null,
  primary key (gmid),
  index (type)
);

create table Variant (
  iid int not null,
  gmid int not null,
  chromosome int not null,
  position int not null,
  flank5 char(10),
  flank3 char(10),
  flag enum("Point Mutation",
            "Loss of Heterozygosity",
            "Ambiguous Change",
            "Plus CNV",
            "Minus CNV"),
  extra varchar(200),
  foreign key (iid) references Isolate (iid),
  foreign key (gmid) references GenotypeMutation (gmid),
  index (iid),
  index (gmid),
  index (chromosome, position)
);

create table Feature (
  fid int auto_increment not null,
  name varchar(100) not null,
  start int not null,
  end int not null,
  chromosome int not null,
  xrefs varchar(200),
  complement boolean,
  bsid int not null,
  type enum("CDS", "Gene", "LTR", "Misc.", "Misc. feature", "Misc. recombination", "Misc. RNA", "ncRNA", "Repeat region", "Replication origin", "rRNA", "Source", "STS", "tRNA", "CDE", "centromere", "Nucleosome", "mRNA", "Intron", "tRNA+-300", "Replication origin+-500") not null,
  primary key (fid),
  foreign key (bsid) references BackgroundStrain (bsid)
) character set 'utf8';