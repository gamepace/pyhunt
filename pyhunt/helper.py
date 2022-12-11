import os
import glob
import winreg
import traceback
import bs4

def find_steam_path() -> str:
    """This function uses the windows registry to find the steam installation path.

    Returns:
        str: This is the steam installation path.
    """
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
        install_path = os.path.abspath(winreg.QueryValueEx(hkey, "InstallPath")[0])
    except:
        print(f'ERROR | Can not get steam path from registry')
        traceback.print_exc()
        install_path = None
    
    return install_path


def find_hunt_path(steam_path:str = "C:\Program Files (x86)\Steam") -> str:
    """This function returns the installation path of Hunt Showdown.

    Args:
        steam_path (str, optional): Steam path to scan. Defaults to "C:\Program Files (x86)\Steam".

    Returns:
        str: This is the base directory of Hunt Showdown.
    """
    # Try default steam path
    if os.path.isdir("C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/"):
       return os.path.abspath("C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/")
    
    # Scan steam path
    steam_scanned_dirs = glob.glob("**/Hunt Showdown/", root_dir=steam_path, recursive=True)
    
    if len(steam_scanned_dirs) > 0:
        if os.path.isdir(os.path.abspath(os.path.join(steam_path, steam_scanned_dirs[0]))):
            if os.path.isfile(os.path.abspath(os.path.join(steam_path, steam_scanned_dirs[0], 'hunt.exe'))):
                return os.path.abspath(os.path.join(steam_path, steam_scanned_dirs[0]))
    
    # User input
    if len(steam_scanned_dirs) == 0:
        print('INFO | Please enter your absolute Hunt Showdown path (e.g.: "C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/"):')
        user_path = input()
        
        if os.path.isdir(os.path.abspath(user_path)):
            if os.path.isfile(os.path.abspath(os.path.join(user_path, 'hunt.exe'))):
                return os.path.abspath(user_path)
            else:
                print(f'ERROR | The provided path is not valid. ("hunt.exe" was not found.)')
                return None
        else:
            print(f'ERROR | The provided path is not valid. (The path is no a valid directory.)')
            return None

def find_attributes_file(hunt_path:str = "C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/") -> str:
    """This function finds the attributes.xml file inside the Hunt Showdown path.

    Args:
        hunt_path (str, optional): Hunt Showdown directory scan hint. Defaults to "C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/".

    Returns:
        str: This is the attributes file path.
    """
    # try default attributes path
    if os.path.isfile("C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml"):
       return os.path.abspath("C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml")
    
    # find in hunt path
    hunt_scanned_files = glob.glob("**/attributes.xml", root_dir=hunt_path, recursive=True)
    
    if len(hunt_scanned_files) > 0:
        if os.path.isdir(os.path.abspath(os.path.join(hunt_path, hunt_scanned_files[0]))):
            if os.path.isfile(os.path.abspath(os.path.join(hunt_path, hunt_scanned_files[0]))):
                return os.path.abspath(os.path.join(hunt_path, hunt_scanned_files[0]))
    else:
        return None

def read_hunt_attributes(attributes_file:str="C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml"):
    pass