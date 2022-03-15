from stagger import read_tag

def fetchfiles(dirr):
    '''To fetch all files recursively from the directory'''
    from os import listdir
    if not dirr: return None
    elif dirr[-1] != '/' and dirr[-1] != '\\': dirr=dirr+'\\'
    
    files = [x for x in listdir(dirr) if len(x.split('.')) >= 2]
    filenames = [dirr+x for x in listdir(dirr) if len(x.split('.')) >= 2]
    folders = [x for x in listdir(dirr) if len(x.split('.')) == 1]
    
    for x in folders:
        filenames.extend(fetchfiles(dirr+x+'\\'))
    return filenames