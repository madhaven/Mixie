from os import system, walk, environ, sep
from os.path import isfile
import sys

TESTING = False#True#
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()

VERSION = '5.3.2 db+'
MUSIC_DIR = sep.join(['d:', 'music'])
DB_FILE = sep.join([environ['USERPROFILE'], 'Documents', 'musictags.db'])
QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue '
QUERY_VLC_PREVIEW = 'start /b vlc.exe --one-instance --playlist-enqueue "%s"'
TAG_DB = dict() # identifier is used in musictags.db, rename discouraged

# load db from file
if isfile(DB_FILE): db = open(DB_FILE, 'r', encoding='utf-16')
else: db = open(DB_FILE, 'w+', encoding='utf-16')
exec(db.read())
db.close()

def saveTagDb(tagdict, db_file = DB_FILE):
    db = open(db_file, 'w+', encoding='utf-16')
    db.write('TAG_DB = '+str(tagdict))
    db.close()

def printTags(li):
    if not li: return
    print()
    for x in li:
        print('%15s'%x, end='\t\t')
    print()

def allTags():
    '''fetches all the tags used.'''
    return { tag for track in TAG_DB for tag in TAG_DB[track]}

def reScan():
    '''
    Scans the entire library and prompts tagging of untagged music.  
    If an already tagged file is missing, prompts resetting the file location.
    '''
    files = {
        (root+sep+file).lower()
        for root, d, files in walk(MUSIC_DIR)
        for file in files}
    untaggedFiles = [
        file for file in sorted(set(files) - set(TAG_DB))
        if file.split('.')[-1] not in ('jpg', 'ini', 'mp4', 'wmv')]
    badTags = sorted(set(TAG_DB) - set(files))

    if untaggedFiles and 'no' not in input('\n%d untagged track(s) found, Tag them now ? '%len(untaggedFiles)).lower():
        print('Add tags (space separated) to your tracks.\nPress Ctrl+C to exit tagging tracks\n')
        try:
            for i, track in enumerate(untaggedFiles):
                print('%5.2f%% %s'%((i+1)*100/len(untaggedFiles), track), end=' : ')
                system(QUERY_VLC_PREVIEW%track)

                tags = set(input().lower().split())
                if not tags: continue
                elif track in TAG_DB: TAG_DB[track] |= tags
                else: TAG_DB[track] = tags
                saveTagDb(TAG_DB)
        except Exception as e: log(e)
        except: pass
        finally: print('Tagging Terminated')

    if badTags and 'no' not in input('\n%d tracks were not found in library, Fix them now ? '%len(badTags)).lower():
        print('\nDrag-n-drop new file to update track location\nPress return to forget the track\nPress Ctrl+C to exit')
        try:
            for i, track in enumerate(badTags):
                print('%5.2f%% %s'%((i+1)*100/len(badTags), track))
                newTrack = input('drop new track : ')[1:-1].lower()
                TAG_DB[newTrack] = TAG_DB[track]
                TAG_DB.pop(track)
                saveTagDb(TAG_DB)
        except Exception as e: log(e)
        except: pass
        finally: print('ReTracking Terminated')

def reTag(args):
    try:
        if not args and 'no' in input('\nSearch and correct existing track tags ? ').lower(): return
        print('Add tags (space separated) to your tracks.\nPress return to ignore\nPress Ctrl+C to exit tagging tracks\n')
        while True:
            s = input('Search for a track : ').lower() if not args else ' '.join(args)
            foundTrack = False
            for track in TAG_DB:
                if s in track:
                    foundTrack = True
                    print(track, ':', *TAG_DB[track], end=' : ')
                    system(QUERY_VLC_PREVIEW%track)

                    tags = set(input().lower().split())
                    if not tags: continue
                    TAG_DB[track] = tags
                    saveTagDb(TAG_DB)
            if not foundTrack: print('No track was found') 
            if args: break
    except Exception as e: log(e)
    except KeyboardInterrupt: pass
    finally: print('ReTagging Terminated')

def play(args):
    #gather required tags
    if args:
        addtags = {x.lower() for x in args[:args.index('-')]} if '-' in args else {x.lower() for x in args}
    else:
        printTags(sorted({tag for track in TAG_DB for tag in TAG_DB[track]}))
        addtags = {x.lower() for x in input("Add Songs : ").lower().split()}

    prePlaylist = {track for track in TAG_DB if TAG_DB[track] & addtags}

    #gather undesired tags from selection
    if args:
        subtags = {x.lower() for x in args[args.index('-')+1:]} if '-' in args[1:] else set()
    else:
        printTags(sorted({ tag for track in prePlaylist for tag in TAG_DB[track] }))
        subtags = {x.lower() for x in input('Remove Songs : ').lower().split()}

    finalPlaylist = {track for track in prePlaylist if not TAG_DB[track] & subtags}

    if finalPlaylist:
        for song in finalPlaylist: print(song)
        if 'no' in input('\nPlay Selection ? : ').lower(): return

        system(QUERY_VLC_START)
        log(QUERY_VLC_START+"\nVLC started :\\")
        for song in finalPlaylist:
            system(QUERY_VLC_ENQUE + '"' + song + '"')

def showInformation():
    print(
        'Music v'+VERSION,
        'Usage','-----',
        'music [play] [tag] [moretags] [- [avoidtag] [moreavoidtags]]',
        'music rescan',
        'music retag [search_trackname_to_retag]',
        'music alltags',
        sep='\n'
    )

if __name__=='__main__':
    try:
        system('title MUSIC %s'%VERSION)
        args = [a.lower() for a in sys.argv[1:]]
        if not args:
            showInformation()
        elif args[0] == 'retag':
            reTag(args[1:])
        elif args[0] == 'version':
            print(VERSION)
        elif args[0] == 'alltags':
            printTags(allTags())
        elif args[0] == 'rescan':
            reScan()
        elif args[0] == 'play':
            play(args[1:])
        else:
            play(args)
    except KeyboardInterrupt: pass
    except Exception as e:
        log(e, wait=True)