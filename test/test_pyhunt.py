from pyhunt import pyhunt

# parseAttributesFile
def test_parseAttributesFile():
    
    hunt = pyhunt()
    result = hunt.parseAttributesFile()
    
    # READ SAMPLE LEVEL
    try:
        level = int(result['Unlocks/UnlockRank'])
    except:
        print('Could not parse level')
        level = -1
        
    try:
        profileId = int(result['MissionBagPlayer_0_0_profileid']) 
    except:
        print('Could not parse profileid')
        profileId = -1    
        
    assert isinstance(result, dict) and len(result.keys()) > 0 and level >= 0 and level <= 100 and profileId >= 0

# parseMatchupFromAttributes
def test_parseMatchupFromAttributes():
    # GENERATE LAST FILE
    hunt = pyhunt()
    hunt.copyAttributesToWorkPath()
    hunt.parseAttributesFile()  
          
    hunt.parseMatchupFromAttributes()
    print(f"TESTING FILE HASH: {hunt.getAttributesFileHash(hunt._workingAttributesPath, 'md5')}")
    
    # TESTS
    type = isinstance(hunt.matchup, dict)
    
    match_keys = len(hunt.matchup['match'].keys()) >= 5
    match_value_check = True if (hunt.matchup['match']['butcher'] == "true" or hunt.matchup['match']['spider'] == "true" or hunt.matchup['match']['assassin'] == "true" or hunt.matchup['match']['scrapbeak'] == "true") else False
    match_region_check = len(hunt.matchup['match']['region']) >= 2  
    
    team_keys = len(hunt.matchup['teams'].keys()) > 0 
    
    passed_teams = 0

    for teamid in hunt.matchup['teams']:
        team = hunt.matchup['teams'][teamid]
        
        _team_mmr = isinstance(int(team['mmr']), int)
        _team_players = len(team['players'].keys()) > 0
        
        _passed_players = 0
        
        for playerid in team['players']:
            
            player = hunt.matchup['teams'][teamid]['players'][playerid]
            
            _player_mmr = isinstance(int(player['mmr']), int)
            _player_name = len(player['bloodlinename']) > 0
            _player_id = isinstance(int(player['profileid']), int)
            _player_keys = len(player.keys()) >= 20
            
            if _player_mmr and _player_name and _player_id and _player_keys:
                _passed_players += 1

            print(f"PLAYER {teamid}.{playerid} | MMR: {_player_mmr}, Name: {_player_name}, Id: {_player_id}, Keys: {_player_keys}")
        if _passed_players == len(team['players'].keys()) and _team_mmr and _team_players:
            passed_teams += 1
            
        print(f"TEAM ({teamid}) |  Passed: {passed_teams} of {len(team['players'].keys())} players")
    
    print(f"MATCH | Passed: {passed_teams} of {len(hunt.matchup['teams'].keys())} teams")
    
    
    team_value_check = passed_teams == len(hunt.matchup['teams'].keys())
    
    assert type and match_keys and match_value_check and match_region_check and team_keys and team_value_check

# getAttributesFileHash
def test_getAttributesFileHash():   
    hunt = pyhunt()
    # MD5
    md5 = hunt.getAttributesFileHash(hunt._workingAttributesPath, 'md5')
    # SHA256
    sha256 = hunt.getAttributesFileHash(hunt._workingAttributesPath, 'sha256')
    # Issue
    unknown = hunt.getAttributesFileHash(hunt._workingAttributesPath, 'Not an Algo.')
    
    assert isinstance(md5, str) and isinstance(sha256, str) and len(md5) == 32 and len(sha256) == 64 and unknown is None 

# getDictonaryFileHash
def test_getDictonaryFileHash():
    hunt = pyhunt()
    hunt.copyAttributesToWorkPath()
    hunt.parseAttributesFile()  
          
    hunt.parseMatchupFromAttributes()
    print(f"TESTING FILE HASH: {hunt.getAttributesFileHash(hunt._workingAttributesPath, 'md5')}")
    
    
    # MD5
    md5 = hunt.getDictonaryFileHash(hunt.matchup, 'md5')
    # SHA256
    sha256 = hunt.getDictonaryFileHash(hunt.matchup, 'sha256')
    # Issue
    unknown = hunt.getDictonaryFileHash(hunt.matchup, 'Not an Algo.') 
    
    assert isinstance(md5, str) and isinstance(sha256, str) and len(md5) == 32 and len(sha256) == 64 and unknown is None 
    

# copyAttributesToWorkPath
def test_copyAttributesToWorkPath():
    hunt = pyhunt()
    srceHash = hunt.getAttributesFileHash(hunt._attributesPath)
    hunt.copyAttributesToWorkPath()
    copyHash = hunt.getAttributesFileHash(hunt._workingAttributesPath)
    
    assert isinstance(srceHash, str) and isinstance(copyHash, str) and srceHash == copyHash
    