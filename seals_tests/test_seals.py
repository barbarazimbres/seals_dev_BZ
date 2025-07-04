import unittest, os, sys
import hazelbean as hb

import seals
from seals import seals_initialize_project

class TestSEALS(unittest.TestCase):
    def setUp(self):
        self.do_full_seals_test = False  # Set to True to force a full rerun. This is done regardless the firsttime, but subsequent runs will skip if False.

    def test_seals_standard_fast(self):
        """Check if TIFF files are valid Cloud-Optimized GeoTIFFs (COGs)."""

        with self.subTest():
            ### ------- ENVIRONMENT SETTINGS -------------------------------
            # Users should only need to edit lines in this section
            
            # Create a ProjectFlow Object to organize directories and enable parallel processing.
            p = hb.ProjectFlow()

            # Assign project-level attributes to the p object (such as in p.base_data_dir = ... below)
            # including where the project_dir and base_data are located.
            # The project_name is used to name the project directory below. If the directory exists, each task will not recreate
            # files that already exist. 
            p.user_dir = os.path.expanduser('~')        
            p.extra_dirs = ['Files', 'seals', 'projects', 'tests']
            p.project_name = 'Brazil_magpie_mapbiomas'
            if self.do_full_seals_test:
                p.project_name = p.project_name + '_' + hb.pretty_time() # If don't you want to recreate everything each time, comment out this line.
            
            # Based on the paths above, set the project_dir. All files will be created in this directory.
            p.project_dir = os.path.join(p.user_dir, os.sep.join(p.extra_dirs), p.project_name)
            p.set_project_dir(p.project_dir) 
            
            p.run_in_parallel = 1 # Must be set before building the task tree if the task tree has parralel iterator tasks.

            # Build the task tree via a building function and assign it to p. IF YOU WANT TO LOOK AT THE MODEL LOGIC, INSPECT THIS FUNCTION
            seals_initialize_project.build_standard_task_tree(p)

            # Set the base data dir. The model will check here to see if it has everything it needs to run.
            # If anything is missing, it will download it. You can use the same base_data dir across multiple projects.
            # Additionally, if you're clever, you can move files generated in your tasks to the right base_data_dir
            # directory so that they are available for future projects and avoids redundant processing.
            # The final directory has to be named base_data to match the naming convention on the google cloud bucket.
            p.base_data_dir = os.path.join(p.user_dir, 'Files/base_data')

            # ProjectFlow downloads all files automatically via the p.get_path() function. If you want it to download from a different 
            # bucket than default, provide the name and credentials here. Otherwise uses default public data 'gtap_invest_seals_2023_04_21'.
            p.data_credentials_path = None
            p.input_bucket_name = None
            
            ## Set defaults and generate the scenario_definitions.csv if it doesn't exist.
            # SEALS will run based on the scenarios defined in a scenario_definitions.csv
            # If you have not run SEALS before, SEALS will generate it in your project's input_dir.
            # A useful way to get started is to to run SEALS on the test data without modification
            # and then edit the scenario_definitions.csv to your project needs.   
            p.scenario_definitions_filename = 'standard_scenarios_BRA_magpie_mapbiomas2.csv' 
            p.scenario_definitions_path = os.path.join(p.input_dir, p.scenario_definitions_filename)
            seals_initialize_project.initialize_scenario_definitions(p)
                
            # Set processing resolution: determines how large of a chunk should be processed at a time. 4 deg is about max for 64gb memory systems
            p.processing_resolution = 1.0 # In degrees. Must be in pyramid_compatible_resolutions

            seals_initialize_project.set_advanced_options(p)
            
            p.L = hb.get_logger('test_run_seals')
            hb.log('Created ProjectFlow object at ' + p.project_dir + '\n    from script ' + p.calling_script + '\n    with base_data set at ' + p.base_data_dir)
            
            p.execute()

            result = 'Done!'            

            required_result_path = os.path.join(p.stitched_lulc_simplified_scenarios_dir, 'lulc_esa_seals7_ssp2_rcp45_luh2-message_bau_shift_2050.tif')
            result = hb.path_exists(required_result_path)
            self.assertTrue(result)
            

    

if __name__ == "__main__":
    unittest.main()

