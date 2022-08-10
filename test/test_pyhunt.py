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
        profileid = int(result['MissionBagPlayer_0_0_profileid']) 
    except:
        print('Could not parse profileid')
        profileid = -1    
        
    assert isinstance(result, dict) and len(result.keys()) > 0 and level >= 0 and level <= 100 and profileid >= 0

# parseMatchupFromAttributes


# getAttributesFileHash


# copyAttributesToWorkPath