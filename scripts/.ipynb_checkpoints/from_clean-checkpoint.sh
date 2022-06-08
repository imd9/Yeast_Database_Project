mysql -u Group_P --password='Group_P' -D Group_P -h "bioed" < SetupClean.sql

python insert_isolates.py
python insert_features.py
python insert_variants.py