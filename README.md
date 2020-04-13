# OMOP schema network graph


Launch ap with : 
```shell script
python -m http.server 8000
```


and then open browser localhost:8000

Reproducing OMOP structural mapping of the SNDS by adapting this original [repo](https://github.com/austin-taylor/austin-taylor.github.io/tree/master/static/examples/force_directed)
Working on the basis of individual mappings of each table to illustrate structural
mapping.
 
Data is taken from individual structural mappings [here](https://framagit.org/interchu/snds-structural-mapping), 
with some harmonization of concepts. The file `snds_to_omop.json` can be rebuilt using code
`clean_json.py`. 