import os, shutil, re, json, glob
import datetime, time, schedule
import hashlib
import xml.etree.ElementTree as ET
import winreg
import vdf

# C:\Program Files (x86)\Steam\steamapps\common\Hunt Showdown\user\profiles\default
 
############################
### BASE ATTRIBUTE CLASS ###
############################
class pyhunt():
    def __init__(self, attributesPath:str="C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml"):
        # CONFIG: SET SOURCE PATH       
        if os.path.isfile(attributesPath):
            self._attributesPath = attributesPath
        else:
            print(f"ISSUE: Attributes is not valid. Please check the provided path! Quitting...")
            quit(1)

        pass
        
    def parseAttributesFile(self):
        """Get an dictonary from the attributes XML.

        Returns:
            dictonary: Includes all information of the attributes.xml
        """
        tree = ET.parse(self._workingAttributesPath)
        root = tree.getroot()
        _attributes = {}
        for item in root.findall('./Attr'):
            _attributes[item.attrib['name']] = item.attrib['value']
            
        self.attributes = _attributes
        
        return _attributes                
       
    def enrichMatchup(self, matchup):
        pass
                
    def parseMatchupFromAttributes(self):
        """This function reads and parses the attributes into a structured dictionary.

        Returns:
            dict: Returns a dictionary containing match, committer & team informations.
        """
        _matchup = {'match': {}, 'committer': {} , "teams": {}}
        
        # MATCH SETTINGS
        print('INFO: Parsing match attributes...')
        _matchup["match"]['unknownboss'] = self.attributes.get('MissionBagBoss_-1')
        _matchup["match"]['butcher'] = self.attributes.get('MissionBagBoss_0')
        _matchup["match"]['spider'] = self.attributes.get('MissionBagBoss_1')
        _matchup["match"]['assassin'] = self.attributes.get('MissionBagBoss_2')
        _matchup["match"]['scrapbeak'] = self.attributes.get('MissionBagBoss_3')
        
        _matchup["match"]['eventid'] = self.attributes.get('LastLiveEventIDLoaded')
        _matchup["match"]['numberofteams'] = self.attributes.get('MissionBagNumTeams')
        _matchup["match"]['quickplay'] = self.attributes.get('MissionBagIsQuickPlay')
        _matchup["match"]['region'] = self.attributes.get('Region')
        
        # COMITTER SETTINGS
        print('INFO: Committer match attributes...')
        _matchup["committer"]['displayName'] = self._steamProfile['PersonaName']
        _matchup["committer"]['steamName'] = self._steamProfile['PersonaName']
        # PARSING KEYS FOR PLAYER / TEAMS
        print('INFO: Parsing player and team attributes...')
        for key in self.attributes.keys(): 
            # PLAYER BAGs      
            if re.search(r"MissionBagPlayer_[0-4]_[0-2].", key):
                __teamId = key.split("_")[1]
                __playerId = key.split("_")[2]
                __attributeId = "".join(key.split("_")[3:]).lower()
                __attributeValue = self.attributes[key]
                
                # CHECK IF TEAM EXISTS ALREADY
                if __teamId not in _matchup['teams'].keys():
                    _matchup['teams'][__teamId] = {}
                    _matchup['teams'][__teamId]['players'] = {}
                
                # CHECK IF PLAYER ENTRY IS PRESENT
                if __playerId not in _matchup['teams'][__teamId]['players'].keys():
                    _matchup['teams'][__teamId]['players'][__playerId] = {}
                    
                # APPEND PLAYER ATTRIBUTE TO MATCHUP FILE
                _matchup['teams'][__teamId]['players'][__playerId][__attributeId] = __attributeValue 
               
            # TEAM BAGs 
            elif re.search(r"MissionBagTeam_[0-4].", key):
                __teamId = key.split("_")[1]
                __attributeId = "".join(key.split("_")[2:]).lower()
                __attributeValue = self.attributes[key]
            
                # CHECK IF TEAM EXISTS ALREADY
                if __teamId not in _matchup['teams'].keys():
                    _matchup['teams'][__teamId] = {}
                    _matchup['teams'][__teamId]['players'] = {}
            
                # APPEND TEAM ATTRIBUTE TO MATCHUP FILE
                _matchup["teams"][__teamId][__attributeId] = __attributeValue       
        
        # Cleanup match
        
        # Check if matchup is the same:
        if self.getDictonaryFileHash(_matchup, 'md5') != self.getDictonaryFileHash(self.matchup, 'md5'):
            print(f"INFO: New match hash was found... {self.getDictonaryFileHash(_matchup, 'md5')}")
            self.matchup = _matchup
            # CLEAN UP SETP
            
            
            # TODO: COPY TO FILE // Change to kafka-producer
            datestring = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
            shutil.copyfile(self._workingAttributesPath, f"temp/attributes_{datestring}_{self.getAttributesFileHash(self._workingAttributesPath, 'md5')}.xml") 
            with open(f"temp/attributes_{datestring}_{self.getAttributesFileHash(self._workingAttributesPath, 'md5')}.json", 'w') as f:
                json.dump(_matchup, f, indent=2)
                
            return _matchup
                
        else:
            print(f"INFO: The match hash is {self.getDictonaryFileHash(self.matchup, 'md5')}")
            return self.matchup
    
    def copyAttributesToWorkPath(self):
        """This function copies the xml file to our local working directory.
        """
        if os.path.isfile(self._workingAttributesPath):
            os.remove(self._workingAttributesPath)
        
        shutil.copyfile(self._attributesPath, self._workingAttributesPath)
        
    

############################
### CLIENT CLASS ###########
############################  
class PyhuntClient():
    """Class for basic client functions like configs, monitoring, etc...
    """
    def __init__(self) -> None:
        # TRY READ CONFIG AND UPDATE
        
        pass
    
    def start_processor(self, delay = 5):
        """This function starts a infitive loop to watch and process the xml.

        Args:
            delay (int, optional): Delay between file lookups. Defaults to 5.
        """
        
        schedule.every(delay).seconds.do(self.process)
        while True:
            schedule.run_pending()
            time.sleep(delay)
            
    def process(self):
        """This function is a holder for the whole process -> Lookup, copy, parsing and pushing.
        """
        # GET LOGGED IN USER
        self.parsePlayerProfileFromSteam()
        
        # CHECK IF FILE HASH HAS CHANGED
        
        if self.getAttributesFileHash(self._attributesPath) != self.getAttributesFileHash(self._workingAttributesPath):
            print('INFO: New file hash was found. Copy file to working directory...')
            self.copyAttributesToWorkPath()
            
            # PARSE ATTRIBUTES FILE
            self.parseAttributesFile()        
            self.parseMatchupFromAttributes()
                  
        print(f'INFO: File hash is {self.getAttributesFileHash(self._workingAttributesPath, "md5")}' )
        pass
    
############################
### UTILITY CLASS ##########
############################       
class PyHuntUtility():
    """Class for a collection of utility functions.    
    """
    
    def __init__(self) -> None:
        pass
    
    
    def get_file_hash(path:str, algo='md5'):
        """This function returns the sha256-hash or md4-hash of any given file path 
        
        Returns:
            str: Hash of given file content 
        """
        if algo.lower() == "sha256":
            sha256 = hashlib.sha256()
            with open(path,'rb') as f:
                hash = f.read()
                sha256.update(hash)
            
            return sha256.hexdigest()
        
        elif algo.lower() == "md5":
            md5 = hashlib.md5()
            with open(path,'rb') as f:
                hash = f.read()
                md5.update(hash)
            
            return md5.hexdigest()

        else:
            print(f'Invalid algo called: {algo}')
            return None
    
    
    def get_dict_hash(dictionary:dict, algo='md5'):
        """This function returns the sha256-hash or md5-hash of a given dictionary
        
        Returns:
            str: Hash of given dictionary
        """
        
        if algo.lower() == "sha256":
            sha256 = hashlib.sha256()  
            sha256.update(json.dumps(dictionary).encode())    
            return sha256.hexdigest()
        
        elif algo.lower() == "md5":
            md5 = hashlib.md5() 
            md5.update(json.dumps(dictionary).encode())               
            return md5.hexdigest()
        
        else:
            print(f'Invalid algo called: {algo}')
            return None 
    
    
    def get_steam_install_path():
        """This function returns the steam installation path.

        Returns:
            str: Install path of steam
        """
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")       
        return winreg.QueryValueEx(hkey, "InstallPath")[0]
    
    def get_steam_profile(steam_path):
        """This function returns the current logged in user as a dictionary

        Returns:
            dictonary: Holds information about the current steam user
        """            
        path = os.path.join(steam_path, "config/loginusers.vdf")
        raw_profiles = vdf.load(open(path, 'r'))['users']
        
        # FIND LAST USER LOGIN
        for user in raw_profiles:
            
            if int(raw_profiles[user]['MostRecent']) == 1:
                steamProfile = raw_profiles[user]
                break
        
        # TODO: GET STEAM PROFILE INFO VIA FILE OR WEBREQUEST
        
        
        print(f"INFO: Currently logged in is: {steamProfile['PersonaName']} ({steamProfile['AccountName']})") 
        return steamProfile
    
    
####################
# UAT ##############
####################
if __name__ == "__main__":
    hunt = pyhunt()
    hunt.startProcessor()