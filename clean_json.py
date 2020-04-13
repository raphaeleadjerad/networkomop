# Script to import information from individual mapping and create nodes/links between variables


# Launch ap with : python -m http.server 8000, and then open browser localhost:8000
# see more dets: https://appdividend.com/2019/02/06/python-simplehttpserver-tutorial-with-example-http-request-handler/
# app created with https://github.com/austin-taylor/austin-taylor.github.io/tree/master/static/examples/force_directed)
#  this source code, see license in consequence

# Modules -------------------------------
import pandas as pd
import json
import re
from flatten_json import flatten_json
import glob
import numpy as np

# README
# The nodes are going to be all variables in OMOP model and SNDS that are linked via
# the structural mapping
# We will group nodes by product to distinguish OMOP tables from SNDS, and within each database the
# different products

# Parameters -----------------------------------------------------
ind_mappings = glob.glob("data/*.json")

# Import individual mappings -------------------------------------


def extract_node_link(ind_mapping, num_table):
    table_omop = ind_mapping[5:][:-5].upper()

    with open(ind_mapping) as json_file:
        data = json.load(json_file)

    nb_keys = len(list(data["source_tables"].keys()))
    print(nb_keys)

    def extract_table_snds(table_snds):

        df = flatten_json(data["source_tables"][table_snds]["CDM_columns"])
        df = pd.json_normalize(df)
        df = df.transpose()
        df = df.reset_index()
        df.columns = ["target", "source"]
        # Keep if mapped or if primary key
        df = df.loc[(df["source"].str.contains("^0") == False) | (df["target"].index == 0), :]
        df["target"] = table_omop + "__" + df["target"]
        df["value"] = 1  # for the moment this does not matter in our representation

        # add links between all variables in a table
        primary_key = df["target"][0]
        idx = pd.MultiIndex.from_product([df["target"], df["target"]], names=["target", "source"])
        link_within_table = idx.to_frame().reset_index(drop=True)
        link_within_table = link_within_table.loc[(link_within_table["target"] != link_within_table["source"]) &
                                          (link_within_table["target"] == primary_key), :]
        link_within_table["value"] = 1

        df = pd.concat([df, link_within_table])

        # nodes_list --------------------------------------------------------
        set_tables = set(df["target"])
        set_tables.update(df["source"])
        unique_tables = list(set_tables)
        nodes_list = []

        for tab in unique_tables:
            nodes_list.append({"name": tab, "group": num_table if re.search(table_omop, tab) else 1})
        return df, nodes_list

    temp_df = []
    temp_nodes = []
    for k in list(data["source_tables"].keys()):
        print(k)
        df, nodes_list = extract_table_snds(k)
        temp_df.append(df)
        temp_nodes.append(nodes_list)

    nodes_list = list(np.concatenate(temp_nodes))
    df = pd.concat(temp_df)
    return df, nodes_list


# Apply function to every json file
dfs = []
nodes_ls = []
for idx, mapping in enumerate(ind_mappings):
    print(mapping)
    df, nodes_list = extract_node_link(mapping, idx + 2)
    dfs.append(df)
    nodes_ls.append(nodes_list)

nodes_ls = list(np.concatenate(nodes_ls))
df = pd.concat(dfs)
nodes = pd.DataFrame(nodes_ls)
nodes = nodes.drop_duplicates().reset_index(drop=True)
nodes_list = nodes.to_dict(orient='records')

# link list ---------------------------------------------------------
df["target"] = df["target"].apply(lambda x: nodes.index[nodes.name == x].to_list()).explode()
df["source"] = df["source"].apply(lambda x: nodes.index[nodes.name == x].to_list()).explode()
links_list = df.to_dict(orient='records')

# Export json file ---------------------------------------------------
json_prep = {"links": links_list, "nodes": nodes_list}
json_dump = json.dumps(json_prep, indent=1, sort_keys=True)
filename_out = 'snds_to_omop.json'
json_out = open(filename_out,'w')
json_out.write(json_dump)
json_out.close()