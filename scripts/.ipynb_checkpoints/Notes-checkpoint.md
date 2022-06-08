## Info

Thomas Kunkel's Page at NIEHS

https://www.niehs.nih.gov/research/atniehs/labs/gisbl/pi/dnarf/index.cfm

### Setting up database

Run `from_clean.sh`


## Pending
- html/css

- javascript
  - widgets for style options?
  - do mutation panel call in chart_script
  - clean up nomenclature
  - a script for holding constants 
  - separate out DataController from HeatmapController
  - more links in the library for other databases

- features
  - search bar-like text filtering for strains
  - More heatmaps?
  - homopolymer run graphs ???
  - indel graphs

- sql queries:
  - ~select all features (type, start, end) in a particular range on a given chromosome~

## Code Snippets

### SQL
```SQL
select type, start, end, chromosome
from Feature f
where start >= 1000 and end < 100000 and chromosome regexp "chr4_ref v2"
```
```SQL
select start, end, chromosome,type
from Feature
where type = "CDE"
```

```SQL
#Feature_summary
select *, total_length/12055736 as genome_fraction
from (select type, count(*) as count,sum(complement) as on_comp_strand, sum(end-start+1) as total_length
		from Feature
		group by type) as H

```
#strain_summary
select sid, COUNT(iid), sum(generations), sum(queryable), count(flag), sum(flag='Point Mutation') , sum(flag = 'Loss of Heterozygosity'), sum(flag = 'Ambigous Change')  
  from Isolate i join Variant v using(iid)
  group by sid;

## Questions For Scott
- Homopolymer run data in sheet static?