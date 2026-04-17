from source.helpers import read_json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json
import sys
import os



class cluster_analysis():
    def __init__(self,
                 subject_id : int):
        
        """
        subject_id : int -> number of the subject on which the analysis will be performed.
        """

        # Config imports
        self.subject = str(subject_id)
        self.config = read_json()
        str_subject = str(self.subject)
        
        # file paths
        self.path_tmc_input = os.path.join("tmc_input", f"{self.config["database"]["db_name"]}-subject{str_subject }")
        self.path_tmc_output = os.path.join("tmc_output", f"{self.config["database"]["db_name"]}-subject{str_subject }")
        self.path_analysis = os.path.join("clusters_analysis", f"{self.config["database"]["db_name"]}-subject{str_subject }")

        # Creating folder if not exists
        if os.path.exists(self.path_analysis) is False:
            try:
                os.mkdir(self.path_analysis)
            except:
                os.mkdir("clusters_analysis")
                os.mkdir("clusters_analysis", f"{self.config["database"]["db_name"]}-subject{str_subject}")


        # Metadata labels dict
        labels = self.config["database"]["metadata_labels"].split(",")
        relabels = self.config["database"]["metadata_relabels"].split(",")
        if (relabels != "") & (len(relabels) == len(labels)):
            self.labels_dict = {i:j for i,j in zip(labels, relabels)}
        else:
            self.labels_dict = {i:j for i,j in zip(labels, labels)}

        # Required files
        tmc_files = ["cells_clusters_info.csv", "cluster_list.json", "cluster_tree.json", "clusters.csv", "graph.json", "node_info.csv"]
        self.req_files = {}

        # TMC output files -> paths into required dict
        for file in tmc_files:
            file_name = file.split(".")[0]
            self.req_files[file_name] = os.path.join(self.path_tmc_output, file)

        # labels files -> paths into required dict
        for label in self.labels_dict:
            self.req_files[label] = os.path.join(self.path_tmc_input, f"labels-{self.labels_dict[label]}.csv")

        # Verify that all of the required files indeed exsits:
        bool_files = [os.path.exists(i) for i in list(self.req_files.values())]

        if all(bool_files) is False:
            print(f"Missing files: {[i for i,j in zip(list(self.req_files.values()), bool_files) if j is False]}")

        # Joining metadata to cells-clusters fule:
        self.cell_clusters = pd.read_csv(self.req_files["cells_clusters_info"], index_col=0)

        for label in list(self.labels_dict.keys()):
            temp_lfile = pd.read_csv(self.req_files[label], index_col=0)
            temp_lfile.columns = [self.labels_dict[label]]
            self.cell_clusters = pd.merge(left=self.cell_clusters, right=temp_lfile, left_index=True, right_index=True, how="inner")


        #########################################
        ### Generating node - cells dataframe ###

        tree_json_path = self.req_files["cluster_tree"]
        # Limit recursion depth for very large trees, just in case (the tree depth is much less than 200k).
        sys.setrecursionlimit(200000)

        # Loads the entire cluster_tree.json into a Python dictionary/list structure.
        with open(tree_json_path, 'r') as f:
            tree = json.load(f)

        node_list = [] # an empty list where we will store the data for every cluster we find.
        node_id_counter = 0 # simple integer starting at 0 to give every node a unique name

        # visit every branch of the tree
        def traverse(node):
            #refering to the int counter of the current node 
            nonlocal node_id_counter 
            current_id = node_id_counter
            node_id_counter += 1
            
            # Too-many-cells stores each node as a pair: [metadata, [list_of_children]]. This line splits them up.
            meta, child = node
            
            # 1. Collect barcodes from this node and all descendants
            # (This uses a small internal helper to stay efficient)
            def get_all_barcodes(n):
                meta, child = n
                # Retriving sub-node information if not leaf node
                barcode = [item['_barcode']['unCell'] for item in meta['_item']] if meta.get('_item') else []

                for c in child:
                    barcode.extend(get_all_barcodes(c))

                return barcode

            barcodes = get_all_barcodes(node)
            
            # 2. Store node data
            node_list.append({
                'node_id': current_id,
                'cell_count': len(barcodes),
                'barcodes': ",".join(barcodes)
                              })

            # 3. Recursively visit children (DFS order)
            for child in child:
                traverse(child)

        traverse(tree)
        
        self.node_cells = pd.DataFrame(node_list)

    def lookup_node(self,
                    node_id : int,
                    save_result : bool = True):
    
        """
        node_id : int -> node id of the node to be visualized.
        save_result : bool -> boolean value, if true will save the plot.
        """
        node_cells = self.node_cells.loc[self.node_cells.node_id == node_id, "barcodes"].values[0].split(",")
        self.node_info = self.cell_clusters[self.cell_clusters.index.isin(node_cells)].copy()
        self.last_node_id = node_id

        if save_result:
            self.node_info.to_csv(os.path.join(self.path_analysis, f"node_{node_id}.csv"))

        return self.node_info
        


    def plot_node(self,
                  node_id: int,
                  by : list,
                  save_plot : bool = True):
        """
        node_id : int -> node id of the node to be visualized.
        by : list -> single value or list of value of metadata columns on which by the pie plot will be presented.
        """

        #
        if (isinstance(self.node_info, pd.DataFrame) is False) | (self.last_node_id != node_id):
            raise Exception(f"please run 'cluster_analysis.lookup_node(node_id={node_id})' before plotting the node.")

        #
        by_final = by[0]
        by_values = self.node_info[by_final]

        #
        if len(by) > 1:
            for label in by[1:]:
                by_values += " , " + self.node_info[label]
                by_final += "." + label
            
            self.node_info[by_final] = by_values


        # metadata labels to be counted in plot
        node_valcounts = by_values.value_counts()
        total = node_valcounts.sum()

        # Pie plot
        plt.pie(x = node_valcounts,
                autopct = lambda p: '{:.0f}'.format(p * total / 100),
                textprops={'fontsize': 14})

        # titles and legend
        plot_label = by_final.replace(".", ", ")
        plt.suptitle(f"Node {99132} ({plot_label})", fontsize=14)
        plt.title(f"Cell Count: {len(self.node_info)}", fontsize=12)
        plt.legend(labels = node_valcounts.index, 
                   title = plot_label, 
                   bbox_to_anchor = (0.95, 0.9))
        
        # Saving figure
        if save_plot:
            plt.savefig(os.path.join(self.path_analysis, f'node_{node_id}_pie.png'), bbox_inches='tight')
        
        plt.show()