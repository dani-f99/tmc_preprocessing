--------------------------------------------------------------------------------
                              SYSTEM IMMUNOLOGY LAB
                                Haifa University
                                 Daniel Fridman 
                                      2026
--------------------------------------------------------------------------------


# PROJECT UPDATE:Too Many Cells Preprocessing Pipeline

## 1. OVERVIEW
This program automates and organizes the bioinformatics pipeline originally developed by Bshara Sahoury and Saif Rahal. 
It streamlines the transition from raw BCR clone data to interactive cluster visualizations.
Pipeline Overview

The pipeline consists of two primary stages:
1. Preprocessing & k-mer Analysis
   * Processes k-mers found in BCR clones alongside their associated metadata.
   * Generates a formatted input compatible with the too-many-cells spectral clustering algorithm.
   
2. Clustering & Visualization
   * Executes the too-many-cells algorithm to generate a cluster_tree in JSON format.
   * The resulting output is optimized for direct use with the too-many-cells-interactive visualization tool.


## 2. PREREQUISITES
This program works on ImmuneDB databse (see resources section)

Please ensure the following python modules are installed:
- `Pandas`
- `NumPy` 
- `SciPy`
- `tqdm`
- `pandarallel`
- `sqlalchemy`
- `pymysql`


## 3. USAGE GUIDE
1. Configuration
    Configure the sql_config.json file to establish database connectivity:
    - Rename sql_config.json.example to sql_config.json.
    - Fill in your SQL connection details and database information as specified in the Configuration section below.
    - Once configured, the script will automatically initiate and load the custom Python modules.

2. Execution
   Run the main pipeline script from your terminal:
   - python3 main.py (bash)

3. Output Location:
   The clustering results will be generated in the following directory: ./tms_output/database-subject/
   
4. The input files required for the too-many-cells-interactive tool are:
   - ./tms_output/database-subject/cluster_tree.json
   - ./tms_input/database-subject/labels.csv

5. Running Visualization
   Use the generated cluster_tree.json and labels.csv files with the too-many-cells-interactive tool to visualize the results.

* Note: A detailed run report will be saved in the reports folder for auditing and debugging. Ensure your config parameters are 
  correctly configured in your metadata to ensure proper output.


## 4. CONFIG.JSON STRUCTURE AND CONFIGURATION
The sql_config.json file is used to configure the ImmuneDB MySQL connection and specify the database for the processing pipeline.

    1. Rename sql_config.json.example to sql_config.json.
	2. Edit the file with your specific database details:
	     > sql.address: The IP address or hostname of your MySQL server.
		 > sql.port: The port number (usually 3306).
		 > database.db_name: The name of the specific database to query.
		 > database.subject_id: A comma-separated list of IDs to process (e.g., "1,2,3").
		 > database.metadata_label: The column name used for labeling (e.g., "cell_type").


## 5. DIRECTORY STRUCTURE
The program uses the following folder structure: 
`database` -> database name as configured in `sql-config.json`, `database.db_name`.
`subject` -> subject_id, each subject data in it's unique folder. configured in `sql-config.json`, `database.subject_id`.

- /reports                                   ## The program will save report for each run to this folder with as `date_database_subject.txt`.
- /source                                    ## Contains the program code.
- /temp_data                                 ## Store the files constructed along the pipeline.
    -  /temp_data/`database`                 ## Dedicated folder for each database and subject.
- /tmc_input                                 ## Store the preproceesed output, can be used as input for the too many cells algorithm.
    -  /tms_input/`database`-`subject`       ## Dedicated folder for each database and subject.
- /tmc_output                                ## Store the too-many-cells clustring output, can be used as input for the too-many-cells-interactive.
    -  /tms_output/`database`-`subject`      ## Dedicated folder for each database and subject.
- /cluster_analysis                          ## Store both csv and plot for node analysis
    - /cluster_analysis/`database`-`subject` ## Dedicated folder for each database and subject.
	
	
## 6. RESOURCES
- See original authors pdf tutorial in source\bshara folder (../source/bshara/readme.pdf)
- too-many-cells-python: https://gregoryschwartz.github.io/too-many-cells/
- too-many-cells-interactive: https://github.com/schwartzlab-methods/too-many-cells-python
- ImmuneDB: https://immunedb.com
