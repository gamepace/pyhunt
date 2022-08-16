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
    assert True

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

# copyAttributesToWorkPath
def test_copyAttributesToWorkPath():
    hunt = pyhunt()
    srceHash = hunt.getAttributesFileHash(hunt._attributesPath)
    hunt.copyAttributesToWorkPath()
    copyHash = hunt.getAttributesFileHash(hunt._workingAttributesPath)
    
    assert isinstance(srceHash, str) and isinstance(copyHash, str) and srceHash == copyHash
    