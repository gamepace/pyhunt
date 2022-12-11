import os
import traceback
import tomllib
from .helper import *

# BASE CLASS #
class huntMonitor():
    def __init__(self) -> None:       
        # TODO Read TOML config from file
        
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
        
        pass
    
    def process_attributes_file():
        pass
    
    def monitor_directory(self):
        pass