import os, shutil, re, json, glob
import datetime, time, schedule
import textwrap
import hashlib
import xml.etree.ElementTree as ET
import winreg
import vdf
from confluent_kafka import Producer
 
############################
### BASE ATTRIBUTE CLASS ###
############################
class pyhunt():
    def __init__(self, attributes_path:str="C:/Program Files (x86)/Steam/steamapps/common/Hunt Showdown/user/profiles/default/attributes.xml"):
        if os.path.isfile(attributes_path):
            self.attributes_path = attributes_path
            self.attributes = self.read_attributes_file()
            self.content = self.get_match_from_attributes()
        
        else:
            print(f"ISSUE: Attributes is not valid. Please check the provided path! Quitting...")
            quit(1)

    
    def read_attributes_file(self):
        """Get a dictonary from the attributes XML.

        Returns:
            dictonary: Includes all information of the attributes.xml
        """
        tree = ET.parse(self.attributes_path)
        root = tree.getroot()
        
        attributes = {}
        
        for item in root.findall('./Attr'):
            attributes[item.attrib['name']] = item.attrib['value']
            
        return attributes
                     
    def get_match_from_attributes(self):
        """This function reads and parses the attributes into a semi-structured dictionary.

        Args:
            attributes (dictonary): Parsed attributes.xml file

        Returns:
            dict: Returns a dictionary containing match, committer & team informations.
            str: Returns the md5 hash of the match, committer & team informations.
        """
        match = {'match': {}, 'committer': {}, "teams": {}}
        
        # MATCH SETTINGS
        print('INFO: Parsing match attributes...')
        match["match"]['UnknownbossFlag'] = self.attributes.get('MissionBagBoss_-1')
        match["match"]['ButcherFlag'] = self.attributes.get('MissionBagBoss_0')
        match["match"]['SpiderFlag'] = self.attributes.get('MissionBagBoss_1')
        match["match"]['AssassinFlag'] = self.attributes.get('MissionBagBoss_2')
        match["match"]['ScrapbeakFlag'] = self.attributes.get('MissionBagBoss_3')
        
        match["match"]['EventId'] = self.attributes.get('LastLiveEventIDLoaded')
        match["match"]['NumberOfTeams'] = self.attributes.get('MissionBagNumTeams')
        match["match"]['QuickplayFlag'] = self.attributes.get('MissionBagIsQuickPlay')
        match["match"]['Region'] = self.attributes.get('Region')
        
        # COMITTER SETTINGS
        print('INFO: Committer match attributes...')
        
        # SETTINGS
        match["committer"]['settings'] = {}
        settings_attributes = [
            'AimMode', 'DepthOfField', 'FieldOfView', 'MotionBlur', 'MouseSensitivity', 
            'MouseSensitivityX', 'MouseSensitivityY', 'MusicVolume', 'MuteVOIPOnDeath', 
            'Gamma', 'MasterVolume', 'MaxFPS', 'MenuAmbienceVolume', 'PerformanceStatVerbosity', 
            'RenderResolution', 'Resolution', 'SFXVolume', 'SysSpec', 'SysSpecEffects', 'SysSpecObject',
            'SysSpecPostProcess', 'SysSpecTextureQuality', 'VOIPInputDevice', 'VOIPOutputDevice', 
            'ControllerAccelerationTime', 'ControllerAddPercentage'           
        ]
        
        for attribute in settings_attributes:
            match["committer"]['settings'][attribute] = self.attributes.get(attribute)
            
        # MISSION
        match["committer"]['mission'] = {}
        mission_attributes = [
            'MissionBagFbeGoldBonus', 'MissionBagFbeHunterXpBonus',
            'MissionBagIsFbeBonusEnabled', 'MouseSensitivity', 'MissionBagIsHunterDead', 
            'HadSummaryScreen', 'HasSeenBrightness', 'HasSeenDarkTribute', 'HasSeenGameModesAdvertisement',
            'HasSeenIntroductionBountyHunt', 'HasSeenSafeZoneOver', 'HighlightMode', 
            'HipMouseSensitivity', 'LevelLoadingTimeMissionUnload', 'PCLevelLoadingTimeMissionUnload',
            'MissionBagNumAccolades', 'MissionBagNumEntries', 'OpenActiveDailies', 'OpenActiveQuests', 
            'OptOutRichPresence', 'OptionsOpenedFromPauseMenu', 'ShowAdditionalHintBanners', 'ShowTutorials', 
            'PVEModeLastSelected', 'PVEModeLastSelected/cemetery', 'PVEModeLastSelected/civilwar', 
            'PVEModeLastSelected/creek', 'Unlocks/UnlockRank'
        ]
        
        for attribute in mission_attributes:
            match["committer"]['mission'][attribute.replace('/', '_')] = self.attributes.get(attribute.replace('/', '_'))
        
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
                if __teamId not in match['teams'].keys():
                    match['teams'][__teamId] = {}
                    match['teams'][__teamId]['players'] = {}
                
                # CHECK IF PLAYER ENTRY IS PRESENT
                if __playerId not in match['teams'][__teamId]['players'].keys():
                    match['teams'][__teamId]['players'][__playerId] = {}
                    
                # APPEND PLAYER ATTRIBUTE TO MATCHUP FILE
                match['teams'][__teamId]['players'][__playerId][__attributeId] = __attributeValue 
               
            # TEAM BAGs 
            elif re.search(r"MissionBagTeam_[0-4].", key):
                __teamId = key.split("_")[1]
                __attributeId = "".join(key.split("_")[2:]).lower()
                __attributeValue = self.attributes[key]
            
                # CHECK IF TEAM EXISTS ALREADY
                if __teamId not in match['teams'].keys():
                    match['teams'][__teamId] = {}
                    match['teams'][__teamId]['players'] = {}
            
                # APPEND TEAM ATTRIBUTE TO MATCHUP FILE
                match["teams"][__teamId][__attributeId] = __attributeValue       
        
        return match
            

############################
### CLIENT CLASS ###########
############################  
class PyhuntClient():
    """Class for basic client functions like configs, monitoring, etc...
    """
    def __init__(self, debug:bool=False) -> None:
        # INITIALIZE CONFIG  
        self.initialize_config() 
        self.debug = debug
        
        # INITIALIZE KAFKA
        try:
            self.kafka = Producer(self.kafka_config['main'])
            print(f'INFO: Initialized KAFKA Producer.')
        except:
            print(f"WARN: Could not initialize KAFKA Producer!")
            self.kafka = None         
        pass
    
    ### CONFIG ######################################################
    def initialize_config(self):
        # TRY READ CONFIG AND UPDATE
        self.config_path = PyHuntUtility.get_user_config_file()
        self.config_dir = os.path.dirname(self.config_path)
        self.kafka_config = json.load(open(".creds/kafka.json", 'r'))     
        
        os.makedirs(self.config_dir, mode=0o777, exist_ok=True)
        
        # WRITE NEW CONFIG
        if not os.path.isfile(self.config_path):
            print('INFO: Generate new config file...')
            self.config = self.generate_new_config()
            self.write_config()
            
        # READ FILE  
        elif os.path.isfile(self.config_path):
            print("INFO: Read existing config file...")
            self.read_config()
        
        # VALIDATE
        if not self.config['steam_install_path'] and os.path.isfile(os.path.join(self.config['steam_install_path'], 'steam.exe')): 
            print(f'ERR: Steam path is not valid. Please add a valid Steam path in {self.config_path}!')
            quit(1)
        
        if not self.config['hunt_install_path'] and os.path.isfile(os.path.join(self.config['hunt_install_path'], 'hunt.exe')): 
            print(f'ERR: Hunt Showdown path is not valid. Please add a valid Hunt Showdown path in {self.config_path}!')
            quit(1)

        # OVERWRITE CHANGES
        self.write_config()

        pass
 
    
    def write_config(self):
        json.dump(self.config, open(self.config_path, 'w'), indent=2)
        pass

    
    def read_config(self):
        self.config = json.load(open(self.config_path, 'r'))
      
    
    def generate_new_config(self):
        # STEAM CONFIG
        print('INFO: Searching for steam installation path...')
        _steam_path = PyHuntUtility.get_steam_install_path()
        if not _steam_path:
            print('Please enter steam installation path (e.g.: "C:\Program Files (x86)\Steam\\"):\n')
            _steam_path = input()
        
        # HUNT INSTALLATION
        print('INFO: Searching for Hunt Showdown installation path...')
        _hunt_path = PyHuntUtility.get_hunt_install_path(_steam_path)
        _attributes_path = os.path.join(_hunt_path, 'user\\profiles\\default\\attributes.xml')
        if not _hunt_path:
            print('Please enter steam installation path (e.g.: "C:\Program Files (x86)\Steam\steamapps\common\Hunt Showdown"):\n')
            _hunt_path = input()
        
        config = {
            "steam_install_path": _steam_path,
            "hunt_install_path": _hunt_path,
            "hunt_attributes_path": _attributes_path,
            "last_file_hash": "",
            "last_content_hash": "",
            "last_enriched_content_hash": ""
        }
        
        return config
    
    def enrich_content(self):        
        # STEAM PROFILE
        _content = self.content
        _content['committer']['SteamName'] = self.steam_profile['AccountName']
        _content['committer']['SteamDisplayName'] = self.steam_profile['PersonaName']
        _content['committer']['SteamID'] = self.steam_profile['SteamID']
        
        _team_id = PyHuntUtility.get_committer_team_id(_content, _content['committer']['SteamDisplayName'])
        _content['committer']['TeamID'] = _team_id
        
        # REMOVE NON-TEAM PLAYER & GET COMMITTER PROFILE ID
        if _team_id:
            for player in _content['teams'][_team_id]['players']:
                if _content['teams'][_team_id]['players'][player]['bloodlinename'] == _content['committer']['SteamDisplayName']:
                    _content['committer']['ProfileID'] = _content['teams'][_team_id]['players'][player]['profileid']
                    
            for player in _content['teams'][_team_id]['players']:                    
                if _content['teams'][_team_id]['players'][player]['bloodlinename'] != _content['committer']['SteamDisplayName'] and _content['teams'][_team_id]['players'][player]['ispartner'] != 'true':
                    del _content['teams'][_team_id]['players'][player]
                    break
     
        # GENERATE TEAM IDs
        team_ids = PyHuntUtility.get_team_ids(_content['teams'])
    
        # GENERATE MATCH ID
        _content['match']['MatchCode'] = PyHuntUtility.get_identifier_from_list(team_ids)
               
        # PARSE KILL FEED
        _content = PyHuntUtility.get_committer_killfeed(_content)     
             
                       
        return _content  
    
    def get_team_summary(self) -> dict:       
        _team_id = self.enriched_content['committer']['TeamID']
        _player_name = self.enriched_content['committer']['SteamDisplayName']
        _player_cards = []
        
        for _playerid in self.enriched_content['teams'][_team_id]['players']:
            _player_card = self.enriched_content['teams'][_team_id]['players'][_playerid]
            
            if _player_card['bloodlinename'] == _player_name:
                _player_card['SteamDisplayName'] = _player_name
                _player_card['SteamName'] = self.enriched_content['committer']['SteamName']
                _player_card['SteamID'] = self.enriched_content['committer']['SteamID']
                
            else:
                _player_card['SteamDisplayName'] = "N/A"
                _player_card['SteamName'] = "N/A"
                _player_card['SteamID'] = "N/A"
                
            _player_cards.append(_player_card)
        
        return _player_cards
    
    def print_committer_summary(self):
        player_cards = self.get_team_summary()
        
        print(f"{'-'*64}")
        
        print(f"""Match:
        Match Code: {self.enriched_content['match']['MatchCode']}
        Region: {self.enriched_content['match']['Region'].upper()}
        Event: {self.enriched_content['match']['EventId']}
        Quick Play: {self.enriched_content['match']['QuickplayFlag']}
        """)
        
        print(f"""Bosses:
        UnknownBoss: {self.enriched_content['match']['UnknownbossFlag']}
        Butcher: {self.enriched_content['match']['ButcherFlag']}
        Spider: {self.enriched_content['match']['SpiderFlag']}
        Scrapbeak: {self.enriched_content['match']['ScrapbeakFlag']}
        """)
        
        for i, player_card in enumerate(player_cards):
            print(f"Player {i}:")
            print(f"\tSteam Player: {player_card['SteamDisplayName']} ({player_card['SteamName']} | {player_card['SteamID']})")
            print(f"\tHunt Player: {player_card['bloodlinename']} ({player_card['profileid']})")
            print(f"\tBounty Pickup: {player_card['bountypickedup']} | Bounty Extract: {player_card['bountyextracted']} | Had Bounty: {player_card['hadbounty']}")
            print(f"\tHad Wellspring: {player_card['hadwellspring']} | Is Soul Survivor: {player_card['issoulsurvivor']}")
            print(f"\tMMR: {player_card['mmr']} | Skillbased: {player_card['skillbased']}")
        
        print(f"""Committer:
        Downs: {self.enriched_content['committer']['killfeed']['numdeaths']}
        Kills: {self.enriched_content['committer']['killfeed']['numkills']}
        Log: {self.enriched_content['committer']['killfeed']['feed']}
        """)
        
        print(f"{'-'*64}")
        
        
        pass
    
    ### PROCESS ######################################################        
    def process(self):
        # CHECK IF FILE HASH IS DIFFERENT TO LAST KNOWN
        print(f'INFO: Monitoring {self.config["hunt_attributes_path"]}...')
        file_hash = PyHuntUtility.get_file_hash(self.config['hunt_attributes_path'])
        if file_hash != self.config['last_file_hash'] or self.debug:
            print(f"INFO: New file hash found: {file_hash}")
            self.config['last_file_hash'] = file_hash
            self.write_config()
                        
            # READ FILE IF NEW FILE HASH WAS FOUND
            content = pyhunt(self.config['hunt_attributes_path']).content
            content_hash = PyHuntUtility.get_dict_hash(content)
            
            if content_hash != self.config['last_content_hash'] or self.debug:
                print(f'INFO: New content hash was found: {content_hash}')
                self.content = content       
                self.config['last_content_hash'] = content_hash
                self.write_config()
                
                # Enrich content
                self.steam_profile = PyHuntUtility.get_active_steam_profile(self.config['steam_install_path'])
                enriched_content = self.enrich_content()
                enriched_content_hash = PyHuntUtility.get_dict_hash(enriched_content)
                
                if enriched_content_hash != self.config['last_enriched_content_hash'] or self.debug:
                    print(f'INFO: New enriched content hash was found: {enriched_content_hash}')
                    self.enriched_content = enriched_content     
                    self.config['last_enriched_content_hash'] = enriched_content_hash                                
                    self.write_config()

                    # COPY TO FILE
                    if self.debug:
                        datestring = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                        shutil.copyfile(self.config['hunt_attributes_path'], f"temp/attributes_{datestring}_{file_hash}.xml") 
                        
                        with open(f"temp/attributes_{datestring}_{file_hash}.json", 'w') as f:
                            json.dump(self.enriched_content, f, indent=2)

                    # DUMP PLAYER
                    if self.debug:
                        self.print_committer_summary()                   

                    # Push to Kafka
                    if not self.debug:
                        try:
                            print(f'INFO: Pushing {content_hash} to KAFKA...')
                            self.kafka.produce(
                                topic = "pyhunt_matches", 
                                key=self.enriched_content['match']['MatchCode'], 
                                value=json.dumps(self.enriched_content)
                            )
                            self.kafka.poll(0)
                            self.kafka.flush()
                        except:
                            pass
                        
                                        
        pass
        
    
    ### PROCESSOR ####################################################
    def start_processor(self, delay = 5):
        """This function starts a infitive loop to watch and process the xml.

        Args:
            delay (int, optional): Delay between file lookups. Defaults to 5.
        """
        print(f'INFO: Start process with delay of {delay} seconds and debug is {self.debug}')
        schedule.every(delay).seconds.do(self.process)
        while True:
            schedule.run_pending()
            time.sleep(delay)
    
############################
### UTILITY CLASS ##########
############################       
class PyHuntUtility():
    """Class for a collection of utility functions.    
    """
    def __init__(self) -> None:
        pass
    
    
    def get_user_config_file():
        """Returns the path to our config file

        Returns:
            _type_: _description_
        """
        return os.path.join(os.path.expanduser('~'), 'Documents', 'PyHunt', 'config.json')

    
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
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")       
            return winreg.QueryValueEx(hkey, "InstallPath")[0]
        except:
            return None
    
    
    def get_active_steam_profile(steam_path):
        """This function returns the current logged in user as a dictionary

        Returns:
            dictonary: Holds information about the current steam user
        """            
        path = os.path.join(steam_path, "config")
        raw_profiles = vdf.load(open(os.path.join(path, "loginusers.vdf"), 'r'))['users']
        
        # FIND LAST USER LOGIN
        for user in raw_profiles:
            
            if int(raw_profiles[user]['MostRecent']) == 1:
                steam_profile = raw_profiles[user]
                break
        
        # GET STEAM PROFILE INFO VIA FILE 
        steam_config = vdf.load(open(os.path.join(path, "config.vdf"), 'r'))
        steam_profile['SteamID'] = steam_config['InstallConfigStore']['Software']['Valve']['steam']['Accounts'][steam_profile['AccountName']]['SteamID']
        print(f"INFO: Currently logged in is: {steam_profile['PersonaName']} ({steam_profile['AccountName']} | {steam_profile['SteamID']})") 
        return steam_profile
    
    def get_hunt_install_path(path_hint=None):
        install_path = None
        
        if path_hint:
            pattern = path_hint + "\**\hunt.exe"
            files = glob.glob(pattern, recursive=True)
            if len(files) > 0:
                install_path = os.path.dirname(files[0])
                    
        return install_path
    
    def get_committer_team_id(content:dict, steam_display_name:str) -> int:
        """Returns the team id of a given Steam Display Name.

        Args:
            content (dict): Parsed content from attributes.xml
            steam_display_name (str): Steam Display Name

        Returns:
            int: Team ID
        """
        for team in content['teams']:
            if content['teams'][team]['ownteam'] == "true":
                for player in content['teams'][team]['players']:
                    if content['teams'][team]['players'][player]['bloodlinename'] == steam_display_name:
                        return team            
    
    
    def get_identifier_from_list(list:list, algo:str='md5') -> str:
        _string = "_".join(sorted(list))
        if algo.lower() == 'md5':
            return hashlib.md5(_string.encode()).hexdigest()
        
        elif algo.lower() == 'sha256':
            return hashlib.sha256(_string.encode()).hexdigest()

        else:
            print(f'Invalid algo called: {algo}')
            return None 
        
        
    def get_team_ids(teams:list) -> list:
        """This function generates all team ids. 

        Args:
            teams (_type_): List of team dictornaries

        Returns:
            list: List of generated team ids (md5-hash of profiles)
        """
        team_ids = []
        
        # LOOP OVER TEAMS
        for team in teams:
            profileids = [] 
            # LOOP OVER PLAYERs
            for player in teams[team]['players']:
                profileids.append(teams[team]['players'][player]['profileid'])
                
            teams[team]['TeamCode'] = PyHuntUtility.get_identifier_from_list(profileids)
            team_ids.append(teams[team]['TeamCode'])
        
        return team_ids
    
    
    def get_events_from_string(string:str, source:str, target:str, type:str)-> list:
        string_split = string.split('@')
        events = []
        for event in string_split:
            if re.search(r'~\d{1,2}:\d{1,2}', event):
                events.append({"target": target, "source": source, "time": event.split(' ~')[1].replace('~', ''), "type": type})

        return events

    def get_committer_killfeed(content)-> dict:
        _content = content
        _committer_profileid = content['committer']['ProfileID']
        feed = []
        downs = 0
        kills = 0
        
        for teamnum in content['teams']:
            _team = content['teams'][teamnum]
            for playernum in _team['players']:
                _player = _team['players'][playernum]
                
                # EVENT PARSING
                killlog = PyHuntUtility.get_events_from_string(_player['tooltipkilledbyme'], _committer_profileid, _player['profileid'], 'killedbycommitter')
                downlog = PyHuntUtility.get_events_from_string(_player['tooltipdownedbyme'], _committer_profileid, _player['profileid'], 'downedbycommitter')
                deathlog =  PyHuntUtility.get_events_from_string(_player['tooltipkilledme'], _player['profileid'], _committer_profileid, 'committerdeath')
                downedlog = PyHuntUtility.get_events_from_string(_player['tooltipdownedme'], _player['profileid'], _committer_profileid, 'committerdowned')

                # APPEND TO LOG
                feed.extend(killlog)
                feed.extend(downlog)
                feed.extend(deathlog)
                feed.extend(downedlog)
                
                kills += (len(killlog) + len(downlog))
                downs += (len(downedlog) + len(deathlog))

        # APPEND TO FEED       
        _content['committer']['killfeed'] = {}
        _content['committer']['killfeed']['feed'] = feed        
        _content['committer']['killfeed']['numkills'] = kills
        _content['committer']['killfeed']['numdeaths'] = downs
                
        return _content

    
    
            
        
        
    
####################
# UAT ##############
####################
if __name__ == "__main__":
    huntClient = PyhuntClient(True)
    huntClient.start_processor()
    quit()