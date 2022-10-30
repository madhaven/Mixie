from abc import abstractmethod
from sys import argv
from os import sep, system, walk

TESTING = True#False#
VERSION = '6.0.0 arch'
MUSIC_DIR = sep.join(['d:', 'music']) # TODO Move to file manager
QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue "%s"'
QUERY_VLC_PREVIEW = 'start /b vlc.exe --one-instance --playlist-enqueue "%s"'
filesToAvoid = ('jpg', 'ini', 'mp4', 'wmv')
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()

class FileManager:
    '''handles the save and load of Mixie data'''

    @abstractmethod
    def load(self) -> dict:
        '''loads the db from file.'''
        raise NotImplementedError

    @staticmethod
    def getManager():
        return BabyManager() # TODO: read file and select manager accordingly

class BabyManager(FileManager):

    def load(self) -> dict:
        return dict()

class MediaManager(): # TODO
    '''Handles all interaction to a media player.'''
    
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
                self.retag(*args[1:])
            elif command == 'version':
                self.showInfo()
            elif command == 'alltags':
                self.showAllTags()
            else:
                self.mix(*args)
    
    def retag(self, *args):
        '''edits tags of songs matching the keyword'''
        print('Add tags (space separated) to your tracks.\nPress return to skip\nPress Ctrl+C to exit tagging tracks\n')
        try:
            while True:
                s = input('Search for a track: ').lower() if not args else ' '.join(args)
                foundTrack = False
                for track in self.mixie.db: # TODO: replace direct access to db
                    if s in track:
                        foundTrack = True
                        print(track, ':', *self.mixie.db[track], end=': ')
                        system(QUERY_VLC_PREVIEW%track) # TODO: change vlc pings to Media Manager

                        tags = input().split()
                        if not tags:
                            continue
                        self.mixie.reTag(track, tags)
                        self.mixie.saveDb()
                if not foundTrack:
                    print('No such track found')
                if args:
                    break
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log(e)
        finally:
            print('ReTagging Closed')
    
    def scan(self, *_):
        '''
        Scans the entire library and prompts tagging of untagged music.
        If an already tagged file is missing, prompts resetting the file location.
        '''
        # TODO: FileManager should handle file access
        files = {
            (root + sep + file).lower()
            for root, d, files in walk(MUSIC_DIR)
            for file in files
        }
        # TODO: Mixie should handle tag logic
        untaggedFiles = [
            file for file in sorted(set(files) - set(self.mixie.db))
            if file.split('.')[-1] not in filesToAvoid]
        badTags = sorted(set(self.mixie.db) - set(files))

        if untaggedFiles and 'no' not in input('\n%d untagged track(s) found, Tag them now ? '%len(untaggedFiles)).lower():
            print('Add tags (space separated) to your tracks.\nPress Ctrl+C to exit tagging tracks\n')
            try:
                for i, track in enumerate(untaggedFiles):
                    print('%5.2f%% %s'%((i+1)*100/len(untaggedFiles), track), end=' : ')
                    system(QUERY_VLC_PREVIEW%track) # TODO: media player should handle previewing songs

                    tags = set(input().lower().split())
                    if not tags:
                        continue
                    elif track in self.mixie.db:
                        self.mixie.db[track] |= tags # TODO: mixie should handle adding of tags
                    else:
                        self.mixie.db[track] = tags # TODO: mixie should handle adding of tags
                    self.mixie.saveDb() # TODO: mixie should handle adding of tags
            except Exception as e: log(e)
            except: pass
            finally: print('Tagging Terminated')

        if badTags and 'no' not in input('\n%d tracks were not found in library, Fix them now ? '%len(badTags)).lower():
            print('\nDrag-n-drop new file to update track location\nPress return to forget the track\nPress Ctrl+C to exit')
            try:
                for i, track in enumerate(badTags):
                    print('%5.2f%% %s'%((i+1)*100/len(badTags), track))
                    newTrack = input('drop new track : ')[1:-1].lower()
                    self.mixie.db[newTrack] = self.mixie.db[track] # TODO: mixie should handle adding of tags
                    self.mixie.db.pop(track)
                    self.mixie.saveDb() # TODO: mixie should handle adding of tags
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
        self.db = fileManager.load()
        self.controller = controller
    
    def playSpecific(self, songName):
        '''cooks the playlist depending on song matching a keyword'''
        playlist = {track for track in self.db if songName in track}
        if playlist:
            self.loadPlaylist(playlist)
    
    def allTags(self):
        '''returns a sorted list of all the tags used across the library'''
        return sorted({tag for track in self.db for tag in self.db[track]})
        # printTags(sorted({tag for track in TAG_DB for tag in TAG_DB[track]}))

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
    
    def reTag(self, songName:str, tags:list):
        '''updates the tags of the specified file'''
        if songName in self.db:
            self.db[songName] = set([tag.lower() for tag in tags])
    
    def saveDb(self):
        '''saves db to file'''
        raise NotImplementedError

if __name__ == '__main__':
    cliArgs = [arg.lower() for arg in argv][1:]
    log('cliArgs:', cliArgs)
    fileManager = FileManager.getManager() # TODO should handle creation of file if it doesn't exist
    controller = MixieController(fileManager=fileManager)
    controller.main(cliArgs)