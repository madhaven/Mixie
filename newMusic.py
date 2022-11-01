from abc import abstractmethod
from sys import argv
from os import sep, system, walk, environ
from os.path import isfile

TESTING = True#False#
VERSION = '6.0.0 arch'
QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue "%s"'
QUERY_VLC_PREVIEW = 'start /b vlc.exe --one-instance --playlist-enqueue "%s"'
NON_MUSIC_FILES = ('jpg', 'ini', 'mp4', 'wmv')
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()

class FileManager:
    '''handles the save and load of Mixie data'''

    @abstractmethod
    def __init__(self, libraryLocation, dbFile):
        # call super().__init__() while overriding this init
        self.libraryLocation = libraryLocation
        self.dbFile = dbFile

    @abstractmethod
    def load(self) -> dict:
        '''reads the db and returns the resultant dictionary'''
        raise NotImplementedError
    
    @abstractmethod
    def saveTagDb(self, tagDict:dict):
        '''saves the provided dictionary to the file.'''
        raise NotImplementedError
    
    def getFilesInLibrary(self, avoidNonMusic=True) -> set:
        '''walks through the file tree with `os.walk` and returns a set of all files included'''
        return {
            (root + sep + file).lower()
            for root, _, files in walk(self.libraryLocation)
            for file in files
            if avoidNonMusic and file.split('.')[-1] not in NON_MUSIC_FILES
        }

    @staticmethod
    def getManager():

        if False:
            # TODO logic for creating initiating stuff if documents don't contain file
            pass
        else:
            # TODO access data from documents
            libraryLocation = sep.join(['d:', 'music'])
            dbLocation = sep.join([environ['USERPROFILE'], 'Documents', 'musictags.db'])
            # TODO: read file and select manager accordingly
            fileManager = BabyFileManager(libraryLocation, dbLocation)

        return fileManager

class BabyFileManager(FileManager):

    def __init__(self, libraryLocation, dbLocation):
        super().__init__(libraryLocation, dbLocation)

    def load(self) -> dict:
        '''reads the db and returns the resultant dictionary'''

        if isfile(self.dbFile):
            db = open(self.dbFile, 'r', encoding='utf-16')
        else:
            db = open(self.dbFile, 'w+', encoding='utf-16')
            
        content = db.read()
        db.close()
        TAG_DB = dict() # TODO change the hardcoded name 
        exec(content) # TODO this is a vulnerability.
        return TAG_DB
    
    def saveTagDb(self, tagdict):
        '''saves the provided dictionary to the file in string format'''
        db = open(self.dbFile, 'w+', encoding='utf-16')
        db.write('TAG_DB = '+str(tagdict)) # TODO change the hardcoded name
        db.close()
        log('tagDb saved')

class MediaManager(): # TODO
    '''Handles all interaction to a media player.'''

    def __init__(self):
        '''maintains a state of the player'''
        # call super().__init__() while overriding this init
        self.state = 'nonInitialized'
    
    @abstractmethod
    def previewTrack(self, track):
        raise NotImplementedError
    
    def __init__(self, *args):
        raise NotImplementedError

class MixieController:
    '''handles all cli interaction'''
    
    def __init__(self, fileManager:FileManager):
        '''Initializes the controller'''
        self.mixie = Mixie(fileManager, self)
    
    def main(self, args):
        '''processes the arguments received from user and pushes the action'''
        if not args:
            self.showInfo()
        else:
            command = args[0].lower()
            if command == 'play':
                self.playSpecific(*args[1:])
            elif command == 'scan':
                self.scan(*args[1:])
            elif command == 'retag':
                self.tag(*args[1:])
            elif command == 'version':
                self.showInfo()
            elif command == 'alltags':
                self.showAllTags()
            else:
                self.mix(*args)
    
    def tag(self, *args):
        '''Facilitates input and output'''
        try:
            print('Add tags (space separated) to your tracks.\nPress return to skip\nPress Ctrl+C to exit tagging tracks\n')                
            search_key = (input('Search for a track: ') if not args else ' '.join(args)).lower()
            
            tracks = self.mixie.findTracks(search_key)
            if not tracks:
                print('No such track found')
            
            for track in tracks:
                print(track, ':', *self.mixie.tagsOfTrack(track), end=': ')
                system(QUERY_VLC_PREVIEW%track) # TODO: change vlc pings to Media Manager
                tags = set(input().lower().split())
                self.mixie.tag(track, tags)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log(e)
        finally:
            print('ReTagging Terminated')
    
    def scan(self, *_):
        '''
        CLI for scan operations
        '''
        untaggedFiles, badTags = self.mixie.scan()
        # TODO: add functionality to remove tags
        if untaggedFiles and 'no' not in input('\n%d untagged track(s) found, Tag them now ? '%len(untaggedFiles)).lower():
            print('Add tags (space separated) to your tracks.\nPress Ctrl+C to exit tagging tracks\n')
            try:
                for i, track in enumerate(untaggedFiles):
                    print('%5.2f%% %s'%((i+1)*100/len(untaggedFiles), track), end=' : ')
                    system(QUERY_VLC_PREVIEW%track) # TODO: media player should handle previewing songs
                    tags = set(input().lower().split())
                    self.mixie.tag(track, tags)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                log(e)
            finally:
                print('Tagging Terminated')

        if badTags and 'no' not in input('\n%d tracks were not found in library, Fix them now ? '%len(badTags)).lower():
            print('\nDrag-n-drop new file to update track location\nPress return to forget the track\nPress Ctrl+C to exit')
            try:
                for i, track in enumerate(badTags):
                    print('%5.2f%% %s'%((i+1)*100/len(badTags), track))
                    newTrack = input('drop new track : ')[1:-1].lower()
                    self.mixie.replaceTrack(track, newTrack)
            except Exception as e: log(e)
            except: pass
            finally: print('ReTracking Terminated')
    
    def playSpecific(self, *args):
        trackName = input('Song to play : ') if not args else ' '.join(args)
        self.mixie.playSpecific(trackName)
    
    def showInfo(self):
        print(
            'Music v%s'%VERSION,
            'Usage','-----',
            'music [tag] [moretags] [- [avoidtag] [moreavoidtags]]',
            'music play trackname',
            'music scan',
            'music retag [search_trackname_to_retag]',
            'music alltags',
            sep='\n'
        )
    
    def mix(self, *args):
        if not args:
            self.showAllTags()
            addtags = {x.lower() for x in input('Add Songs: ').lower().split()}
            subtags = {x.lower() for x in input('Avoid Songs : ').lower().split()}
        elif '-' in args[1:]:
            addtags = {x.lower() for x in args[:args.index('-')]}
            subtags = {x.lower() for x in args[args.index('-')+1:]}
        else:
            addtags = {x.lower() for x in args}
            subtags = set()

        self.mixie.mix(addtags, subtags)

    def loadPlaylist(self, playlist):
        system(QUERY_VLC_START)
        log(QUERY_VLC_START+"\nVLC started :\\")
        for song in playlist:
            system(QUERY_VLC_ENQUE%song)
    
    def showAllTags(self):
        self.showTags(self.mixie.allTags())
    
    def showTags(self, tags):
        if not tags:
            return
        print('\n', *['%15s'%tag for tag in tags], sep='\t\t', end='\n')

class Mixie:
    '''contains the logic to handle processes'''

    def __init__(self, fileManager:FileManager, controller:MixieController):
        self.fileManager = fileManager
        self.controller = controller
        self.db = self.fileManager.load()
        log('DB loaded')
    
    def mix(self, addtags, subtags):
        '''cooks the playlist from the choice of tags'''
        # prePlaylist = {track for track in self.db if self.db[track] & addtags}
        # finalPlaylist = {track for track in prePlaylist if not self.db[track] & subtags}
        playlist = {
            track for track in self.db
            if self.db[track] & addtags and not self.db[track] & subtags
        }
        if playlist:
            self.loadPlaylist(playlist) # TODO add media manager here
    
    def loadPlaylist(playlist): # TODO mediaManager should handle this
        system(QUERY_VLC_START)
        log(QUERY_VLC_START+'\nVLC started :\\')
        for song in playlist:
            system(QUERY_VLC_ENQUE%song)
    
    def playSpecific(self, songName):
        '''cooks the playlist depending on song matching a keyword'''
        playlist = {track for track in self.db if songName in track}
        if playlist:
            self.loadPlaylist(playlist)
    
    def findTracks(self, searchKey:str):
        '''returns a list of tracks that match the searchKey'''
        if not searchKey:
            return []
        else:
            return [
                track for track in sorted(self.db)
                if searchKey in track]
    
    def allTags(self):
        '''returns a sorted list of all the tags used across the library'''
        # printTags(sorted({tag for track in TAG_DB for tag in TAG_DB[track]}))
        return sorted({tag for track in self.db for tag in self.db[track]})
    
    def tagsOfTrack(self, track):
        return self.db[track] if track in self.db else []
    
    def scan(self):
        '''
        Scans the entire library and returns two sets.\n  
        One containing files that are not tagged\n  
        The other containing files that were tagged but don't exist in the right location.  
        '''
        files:set = self.fileManager.getFilesInLibrary() # TODO: make options for multiple library locations
        untaggedFiles = [file for file in sorted(files - set(self.db))]
        badTags = sorted(set(self.db) - set(files))
        return untaggedFiles, badTags

    def tag(self, track:str, newTags:set, keepOldTag=False):
        '''edits tags of song'''
        if newTags:
            newTags = {tag.lower() for tag in newTags}
            if keepOldTag:
                self.db[track] |= newTags
            else:
                self.db[track] = newTags
            self.saveDb()

    def replaceTrack(self, oldTrack:str, newTrack:str):
        if (oldTrack in self.db) and (oldTrack!=newTrack):
            self.db[newTrack] = self.db[oldTrack]
            self.forgetTrack(oldTrack)
    
    def forgetTrack(self, track:str):
        '''removes all tags and existence of a track from memory'''
        if track in self.db:
            self.db.pop(track)
            self.saveDb()
    
    def saveDb(self):
        '''makes fileManager save db to file'''
        self.fileManager.saveTagDb(self.db)

if __name__ == '__main__':
    cliArgs = [arg.lower() for arg in argv][1:]
    log('cliArgs:', cliArgs)
    fileManager = FileManager.getManager() # TODO should handle creation of file if it doesn't exist
    controller = MixieController(fileManager=fileManager)
    controller.main(cliArgs)