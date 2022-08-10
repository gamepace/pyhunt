from dataclasses import dataclass
import os, shutil, re, json
import datetime, time, schedule
import hashlib
import xml.etree.ElementTree as ET


# C:\Program Files (x86)\Steam\steamapps\common\Hunt Showdown\user\profiles\default

# HUNT ATTRIBUTES XML DATA CLASSES
@dataclass
class huntPlayer():
    playerName: str
    playerId: int # steamid
    playerMMR: int
    playerSkillbased: bool
    
@dataclass
class huntTeam():
    teamId: str # Generated md5 hash from all steamids
    teamHandicap: int
    teamInvite: int
    teamNumPlayers: int
    teamMMR: int
    teamUploadFlag: bool

@dataclass
class huntSettings():
    test:str = None
    
  
  
# HUNT BASE CLASS
class pyhunt():
    def __init__(self, attributesPath:str="C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml"):
        # CONFIG: SET SOURCE PATH
        if os.path.isfile(attributesPath):
            self._attributesPath = attributesPath
        else:
            # TODO: UI POPUP
            self._attributesPath = input("Please provide the path to your attributes.xml!\nThe file is located under [InstallationPath]/user/profiles/default/attributes.xml\n")
        
        # CONFIG: SET WORKING PATH AND INITIAL HASH
        self._workingAttributesPath = "./temp/attributes.xml"
        self.copyAttributesToWorkPath()
            
        # INIT: LOOP PROCESS
        # self.startProcessor()
        # self.process()
        pass
    
    def startProcessor(self, delay = 5):
        """This function starts a infitive loop to watch and process the xml.

        Args:
            delay (int, optional): Delay between file lookups. Defaults to 5.
        """
        
        schedule.every(delay).seconds.do(self.process)
        while True:
            schedule.run_pending()
            time.sleep(delay)
            
        pass
    
    
    def process(self):
        """This function is a holder for the whole process -> Lookup, copy, parsing and pushing.
        """
        # CHECK IF FILE HASH HAS CHANGED
        if self.getAttributesFileHash(self._attributesPath) != self.getAttributesFileHash(self._workingAttributesPath):
            print('INFO: New file hash was found. Copy file to working directory...')
            self.copyAttributesToWorkPath()
            
            # PARSE ATTRIBUTES FILE
            self.attributes = self.parseAttributesFile()        
            self.matchup = self.parseMatchupFromAttributes()
                  
        print(f'INFO: File hash is {self.getAttributesFileHash(self._workingAttributesPath, "md5")}' )
        pass
    
    def parseAttributesFile(self):
        """Get an dictonary from the attributes XML.

        Returns:
            dictonary: Includes all information of the attributes.xml
        """
        tree = ET.parse(self._workingAttributesPath)
        root = tree.getroot()
        attributes = {}
        for item in root.findall('./Attr'):
            attributes[item.attrib['name']] = item.attrib['value']
            
        return attributes                
                
    def parseMatchupFromAttributes(self):
        """This function reads and parses the attributes into a structured dictionary.

        Returns:
            dict: Returns a dictionary containing match, committer & team informations.
        """
        __matchup = {'match': {}, 'committer': {} , "teams": {}}
        
        # MATCH SETTINGS
        print('INFO: Parsing match attributes...')
        __matchup["match"]['unknownboss'] = True if self.attributes.get('MissionBagBoss_-1') == "true" else False
        __matchup["match"]['butcher'] = True if self.attributes.get('MissionBagBoss_0') == "true" else False
        __matchup["match"]['spider'] = True if self.attributes.get('MissionBagBoss_1') == "true" else False
        __matchup["match"]['assassin'] = True if self.attributes.get('MissionBagBoss_2') == "true" else False
        __matchup["match"]['scrapbeak'] = True if self.attributes.get('MissionBagBoss_3') == "true" else False
        
        __matchup["match"]['eventid'] = self.attributes.get('LastLiveEventIDLoaded')
        __matchup["match"]['numberofteams'] = self.attributes.get('MissionBagNumTeams')
        __matchup["match"]['quickplay'] = True if self.attributes.get('MissionBagIsQuickPlay') == "true" else False
        __matchup["match"]['region'] = self.attributes.get('Region')
        
        # COMITTER SETTINGS
        # print('INFO: Committer match attributes...')
        
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
                if __teamId not in __matchup['teams'].keys():
                    __matchup['teams'][__teamId] = {}
                    __matchup['teams'][__teamId]['players'] = {}
                
                # CHECK IF PLAYER ENTRY IS PRESENT
                if __playerId not in __matchup['teams'][__teamId]['players'].keys():
                    __matchup['teams'][__teamId]['players'][__playerId] = {}
                    
                # APPEND PLAYER ATTRIBUTE TO MATCHUP FILE
                __matchup['teams'][__teamId]['players'][__playerId][__attributeId] = __attributeValue 
               
            # TEAM BAGs 
            elif re.search(r"MissionBagTeam_[0-4].", key):
                __teamId = key.split("_")[1]
                __attributeId = "".join(key.split("_")[2:]).lower()
                __attributeValue = self.attributes[key]
            
                # CHECK IF TEAM EXISTS ALREADY
                if __teamId not in __matchup['teams'].keys():
                    __matchup['teams'][__teamId] = {}
                    __matchup['teams'][__teamId]['players'] = {}
            
                # APPEND TEAM ATTRIBUTE TO MATCHUP FILE
                __matchup["teams"][__teamId][__attributeId] = __attributeValue

        
        # SAVE TO FILE
        # TODO: Remove this part
        datestring = datetime.datetime.utcnow().strftime("%Y%m%d")
        shutil.copyfile(self._workingAttributesPath, f"temp/attributes_{datestring}_{self.getAttributesFileHash(self._workingAttributesPath, 'md5')}.xml") 
        with open(f"temp/attributes_{datestring}_{self.getAttributesFileHash(self._workingAttributesPath, 'md5')}.json", 'w') as f:
            json.dump(__matchup, f, indent=2)

        return __matchup
    
    
    def getAttributesFileHash(self, path, algo:str='sha256'):
        """This function returns the sha256-hash of the attributes.xml 
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
    
    def copyAttributesToWorkPath(self):
        """This function copies the xml file to our local working directory.
        """
        if os.path.isfile(self._workingAttributesPath):
            os.remove(self._workingAttributesPath)
        
        shutil.copyfile(self._attributesPath, self._workingAttributesPath)
        

# UAT
if __name__ == "__main__":
    hunt = pyhunt()
    hunt.startProcessor()