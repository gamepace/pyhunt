import os
import traceback
import tomlkit

from .helper import *

########################################################################
# MONITOR CLASS ########################################################
########################################################################
class huntMonitor():
    def __init__(self) -> None:       
        # Create configuration directory
        self.pyhunt_path = os.path.abspath(os.path.join(os.getenv('APPDATA'), 'pyhunt'))
        self.pyhunt_config_path = os.path.abspath(os.path.join(self.pyhunt_path, 'config.toml'))
        
        # check if configuration directory exist
        if not os.path.isdir(self.pyhunt_path):
            os.mkdir(self.pyhunt_path)
        
        # Is a config file present then load the file
        if os.path.isfile(self.pyhunt_config_path):
            print(f'INFO | Loaded config file "{self.pyhunt_config_path}".')
            with open(self.pyhunt_config_path,'r') as f:
                pyhunt_toml = tomlkit.parse(f.read())
            
            # assign variables
            self.steam_path = pyhunt_toml['pathes']['steam_path']
            self.hunt_path = pyhunt_toml['pathes']['hunt_path']
            self.attributes_file = pyhunt_toml['pathes']['attributes_file']
            
        else:
            print(f'INFO | Creating config file "{self.pyhunt_config_path}".')
            # Find install path
            self.steam_path = find_steam_path()
            
            if not os.path.isdir(self.steam_path):
                print(f"ERROR | Could not initialize steam path.")
                quit()
            
            # find hunt path
            self.hunt_path = find_hunt_path(self.steam_path)
            
            if not os.path.isdir(self.hunt_path):
                print(f"ERROR | Could not initialize Hunt Showdown path.")
                quit()
            
            # find attributes file
            self.attributes_file = find_attributes_file(self.hunt_path)
            
            if not os.path.isfile(self.attributes_file):
                print(f"ERROR | Could not find attributes file.")
                quit()
            
            # Generate TOML document
            pyhunt_toml = tomlkit.document()
            toml_pathes = tomlkit.table()
            toml_pathes.add('steam_path', self.steam_path)
            toml_pathes.add('hunt_path', self.hunt_path)
            toml_pathes.add('attributes_file', self.attributes_file)
            pyhunt_toml.add('pathes', toml_pathes)
            
            with open(self.pyhunt_config_path, 'w') as f:
                f.write(tomlkit.dumps(pyhunt_toml))
                
        # Start monitor directorymonitor_directory
        self.monitor_directory()
        pass
    
    def process_attributes_file(self):
        read_hunt_attributes(self.attributes_file)
        pass
    
    def monitor_directory(self):
        self.process_attributes_file()
        pass