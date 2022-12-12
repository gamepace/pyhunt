import os
import traceback
import yaml

from .helper import *

########################################################################
# MONITOR CLASS ########################################################
########################################################################
class huntMonitor():
    def __init__(self) -> None:       
        # Create configuration directory
        self.pyhunt_path = os.path.abspath(os.path.join(os.getenv('APPDATA'), 'pyhunt'))
        self.pyhunt_config_path = os.path.abspath(os.path.join(self.pyhunt_path, 'config.yml'))
        
        # check if configuration directory exist
        if not os.path.isdir(self.pyhunt_path):
            os.mkdir(self.pyhunt_path)
        
        # Is a config file present then load the file
        if os.path.isfile(self.pyhunt_config_path):
            print(f'INFO | Loaded config file "{self.pyhunt_config_path}".')
            
            # load yaml file
            self.pyhunt_config = self.read_config()
            
        else:
            print(f'INFO | Creating config file "{self.pyhunt_config_path}".')
            # Find install path
            steam_path = find_steam_path()
            
            if not os.path.isdir(steam_path):
                print(f"ERROR | Could not initialize steam path.")
                quit()
            
            # find hunt path
            hunt_path = find_hunt_path(steam_path)
            
            if not os.path.isdir(hunt_path):
                print(f"ERROR | Could not initialize Hunt Showdown path.")
                quit()
            
            # find attributes file
            attributes_file = find_attributes_file(hunt_path)
            
            if not os.path.isfile(attributes_file):
                print(f"ERROR | Could not find attributes file.")
                quit()
            
            # Generate config dictionary
            self.pyhunt_config = {
                "pathes": {
                    "steam_path": steam_path,
                    "hunt_path": hunt_path,
                    "attributes_file": attributes_file,
                },
                "checksums": {
                    'last_match': None
                }
            }
            
            self.write_config()
                            
        # Start monitor directorymonitor_directory
        self.monitor_directory()
        pass
    
    
    def process_attributes_file(self):
        read_hunt_attributes(self.pyhunt_config['pathes']['attributes_file'])
        pass
    
    
    def monitor_directory(self):
        self.process_attributes_file()
        pass
    
    
    def write_config(self):
        with open(self.pyhunt_config_path, 'w') as f:
            yaml.dump(self.pyhunt_config, f)
               
        pass
    
    
    def read_config(self) -> dict:
        with open(self.pyhunt_config_path, 'r') as f:
            pyhunt_config = yaml.safe_load(f)    
            
        return pyhunt_config
    