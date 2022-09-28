from os import system, walk, environ, sep
from os.path import isfile
import sys

TESTING = False#True#
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()

VERSION = '5.3.3 db+search'
MUSIC_DIR = sep.join(['d:', 'music'])
DB_FILE = sep.join([environ['USERPROFILE'], 'Documents', 'musictags.db'])
QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue '
QUERY_VLC_PREVIEW = 'start /b vlc.exe --one-instance --playlist-enqueue "%s"'
AUDIO_FILE_EXTS = ['3gp', 'aa', 'aac', 'aax', 'act', 'aiff', 'alac', 'amr', 'ape', 'au', 'awb', 'dss', 'dvf', 'flac', 'gsm', 'iklax', 'ivs', 'm4a', 'm4b', 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'nmf', 'nmf', 'ogg', 'oga', 'mogg', 'opus', 'ra', 'rm', 'raw', 'rf64', 'sln', 'tta', 'voc', 'vox', 'wav', 'wma', 'wv', 'webm', '8svx', 'cda']
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

def allFiles(condition=lambda x: True):
    '''fetches all files in library.'''
    return {
        (root+sep+file).lower()
        for root, d, files in walk(MUSIC_DIR)
        for file in files
        if condition(file)
    }

def playWithVLC(playlist=None, preview=False):
    '''
    Opens VLC and loads the songs provided in `playlist`.\n
    `previewMode` specifies if a single song is being previewed.
    '''
    if not playlist: return
    if preview:
        if isinstance(playlist, str):
            system(QUERY_VLC_PREVIEW%playlist)
    else:
        for song in playlist: print(song)
        if not 'no' in input('\nPlay Selection ? : ').lower():
            system(QUERY_VLC_START)
            log(QUERY_VLC_START+"\nVLC started :\\")
            for song in playlist:
                system(QUERY_VLC_ENQUE + '"' + song + '"')

def reTag(args):
    try:
        if not args and 'no' in input('\nSearch and correct existing track tags ? ').lower(): return
        print('Add tags (space separated) to your tracks.\nPress return to ignore\nPress Ctrl+C to exit tagging tracks\n')
        while True:
            s = input('Search for a track : ').lower().split() if not args else args
            foundTrack = False
            for track in TAG_DB:
                if any(map(lambda ss: ss in track, s)):
                    foundTrack = True
                    print(track, ':', *TAG_DB[track], end=' : ')
                    playWithVLC(track, preview=True)

                    tags = set(input().lower().split())
                    if not tags: continue
                    TAG_DB[track] = tags
                    saveTagDb(TAG_DB)
            if not foundTrack: print('No track was found') 
            if args: break
    except Exception as e: log(e)
    except KeyboardInterrupt: pass
    finally: print('ReTagging Terminated')

def searchAndPlay(args):
    #gather required tags
    if not args:
        args = input('Search for songs : ').split()
    
    #gather files
    files = allFiles(condition=lambda file: any(map(lambda searchStr: searchStr in file, args)))
    playWithVLC(files)

class Mixie:
    '''Handles all Mixie logic'''

    def __init__(self, controller):
        self.controller = controller
        # TODO: make an interface for functions a controller hsould have...

    def play(self, *args):
        #gather required tags
        if args:
            addtags = {x.lower() for x in args[:args.index('-')]} if '-' in args else {x.lower() for x in args}
        else:
            printTags(sorted({tag for track in TAG_DB for tag in TAG_DB[track]}))
            addtags = {x.lower() for x in input("Add Songs : ").lower().split()}
        
        input(str(addtags))

        prePlaylist = {track for track in TAG_DB if TAG_DB[track] & addtags}

        #gather undesired tags from selection
        if args:
            subtags = {x.lower() for x in args[args.index('-')+1:]} if '-' in args[1:] else set()
        else:
            printTags(sorted({ tag for track in prePlaylist for tag in TAG_DB[track] }))
            subtags = {x.lower() for x in input('Remove Songs : ').lower().split()}

        finalPlaylist = {track for track in prePlaylist if not TAG_DB[track] & subtags}
        playWithVLC(finalPlaylist)
    
    def allTags(self, TAG_DB:dict) -> set:
        '''fetches every tag used.'''
        return { tag for track in TAG_DB for tag in TAG_DB[track]}

    def reScan(self, TAG_DB:dict, files:list):
        '''
        Scans the entire library and prompts tagging of untagged music.  
        If an already tagged file is missing, prompts resetting the file location.
        '''

        badTags = self.findMissingFiles(TAG_DB, files)
        untaggedFiles = self.findUntaggedFiles(TAG_DB, files)

        if untaggedFiles and 'no' not in input('\n%d untagged track(s) found, Tag them now ? '%len(untaggedFiles)).lower():
            self.fixUntaggedFiles(TAG_DB, untaggedFiles)

        if badTags and 'no' not in input('\n%d tracks were not found in library, Fix them now ? '%len(badTags)).lower():
            self.fixMissingFiles(TAG_DB, badTags)

    def findMissingFiles(self, TAG_DB:dict,  files:list) -> list:
        return sorted(set(TAG_DB) - files)
    
    def findUntaggedFiles(self, TAG_DB:dict, files:list) -> list:
        return [
            file for file in sorted(files - set(TAG_DB))
            if file.split('.')[-1] in AUDIO_FILE_EXTS
        ]
    
    def fixMissingFiles(self, TAG_DB:dict, badTags:list):
        print('\nDrag-n-drop new file to update track location\nPress return to forget the track\nPress Ctrl+C to exit')
        try:
            for i, track in enumerate(badTags):
                print('%5.2f%% %s'%((i+1)*100/len(badTags), track))
                newTrack = input('drop new track : ')[1:-1].lower()
                TAG_DB[newTrack] = TAG_DB[track]
                TAG_DB.pop(track)
                saveTagDb(TAG_DB)
        except Exception as e:
            log(e)
        finally:
            print('ReTracking Terminated')
    
    def fixUntaggedFiles(self, TAG_DB:dict, untaggedFiles:list):
        print('Add tags (space separated) to your tracks.\nPress Ctrl+C to exit tagging tracks\n')
        try:
            for i, track in enumerate(untaggedFiles):
                print('%5.2f%% %s'%((i+1)*100/len(untaggedFiles), track), end=' : ')
                playWithVLC(track, True)

                tags = set(input().lower().split())
                if not tags:
                    continue
                elif track in TAG_DB:
                    TAG_DB[track] |= tags
                else:
                    TAG_DB[track] = tags
                saveTagDb(TAG_DB)
        except Exception as e:
            log(e)
        finally:
            print('Tagging Terminated')

class MixieController:
    '''Handles all CLI user interaction'''

    def __init__(self):
        self.mixie:Mixie = Mixie(self)

    def main(self, *args):
        try:
            system('title MUSIC %s'%VERSION)
            if not args:
                self.showInformation()
                self.mixie.play()
            elif args[0] == 'retag':
                reTag(args[1:])
            elif args[0] == 'version':
                print(VERSION)
            elif args[0] == 'alltags':
                printTags(self.mixie.allTags())
            elif args[0] == 'rescan':
                files = allFiles()
                self.mixie.reScan(TAG_DB, files)
            elif args[0] == 'play':
                searchAndPlay(args[1:])
            else:
                self.mixie.play(args)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log(e, wait=True)
    
    def showInformation(self):
        print(
            'Music v'+VERSION,
            'Usage','-----',
            'music [play] [tag] [moretags] [- [avoidtag] [moreavoidtags]]',
            'music rescan',
            'music retag [search_trackname_to_retag]',
            'music alltags',
            sep='\n'
        )
    
    @classmethod
    def printTags(li):
        if not li:
            return
        print()
        for x in li:
            print('%15s'%x, end='\t\t')
        print()

if __name__=='__main__':
    args = [a.lower() for a in sys.argv[1:]]
    mixie = MixieController()
    mixie.main(*args)