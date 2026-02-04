from source.helpers import read_json, create_folders
from toomanycells import TooManyCells as tmc
import unittest
import subprocess
import os

# Pipeline for too many cells run
class RunTmsTest(unittest.TestCase):
    """
    Pipeline that will run the too many cells spectral clustring analysis
    on the pipeline 2 output (pipeline2_matrixmaker).
    """

    ##################
    # Class initiation 
    @classmethod
    def setUpClass(cls):
        print("--- Initializing Too Many Cells Pipeline Environment ---")
        
        # Importing database and subjects information -> for folder creation
        config = read_json()
        cls.db_name = config["database"]["db_name"]
        cls.db_subjects = config["database"]["subject_id"].split(",")

    # Creating required folders
    def test_01_folders_creation(self):        
        self.path_mainf = "tms_output"
        req_folders = [self.path_mainf] + [os.path.join(self.path_mainf, "-".join([self.db_name, f"subject{i}"])) for i in self.db_subjects]
        create_folders(req_folders)


    # Running the too many cells spectral clusring algorthim on the input data
    def test_02_run_tms(self):
        for i in self.db_subjects:
            # output and input path
            folder_name = "-".join([self.db_name, f"subject{i}"])
            i_input = os.path.join("tms_input", folder_name)
            i_output = os.path.join("tms_output", folder_name)

            # output files, used to check if the output already exists
            output_required = ["cluster_list.json", "cluster_tree.json", "clusters.csv","graph.json", "node_info.csv"]
            output_actual = os.listdir(i_output)
            
            # Checking if the output already exists
            if set(output_required) == set(output_actual):
                print(f"> too many cells already processed subject {i}.")

            # if not, run too many cells on the subject
            else:
                try:
                    # Creating too many cells object with the loaded data.
                    tmc_obj = tmc(i_input,
                                   i_output,
                                  input_is_matrix_market=True)

                    # Runnig the spectral clustring 
                    tmc_obj.run_spectral_clustering()

                    # Storing the outputs in the input folder
                    tmc_obj.store_outputs()
                
                except subprocess.CalledProcessError as pr_error:
                    print(f"Encounted error while trying to run python-toomacnycells")