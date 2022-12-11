from .context import pyhunt

import os

########################################################################
### Helper Tests #######################################################
########################################################################

def test_find_steam_path():
    variable_type = type(pyhunt.helper.find_steam_path())
    is_directory = os.path.isdir(pyhunt.helper.find_steam_path())
    assert variable_type == str and is_directory == True

    
def test_find_hunt_path():
    steam_path = pyhunt.helper.find_steam_path()
    hunt_path = pyhunt.helper.find_hunt_path(steam_path)
    variable_type = type(hunt_path)
    is_directory = os.path.isdir(hunt_path)
    assert variable_type == str and is_directory == True
    

def test_find_attributes_file():
    steam_path = pyhunt.helper.find_steam_path()
    hunt_path = pyhunt.helper.find_hunt_path(steam_path)
    attributes_file = pyhunt.helper.find_attributes_file(hunt_path)
    variable_type = type(attributes_file)
    is_file = os.path.isfile(attributes_file)
    assert variable_type == str and is_file == True
    