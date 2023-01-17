from abc import abstractmethod
from os import environ, sep, system
from os.path import isdir
from sys import argv
from FileManager import *

TESTING = True#False#
VERSION = '6.0.0 arch'
QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue "%s"'
QUERY_VLC_PREVIEW = 'start /b vlc.exe --playlist-enqueue "%s"'
MIXIECONFIG = sep.join([environ['USERPROFILE'], 'mixie.db']) if not TESTING else 'mixie.db'
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()


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
    
    def __init__(self):
        '''Initializes the controller'''
        self.mixie:Mixie = None # to be assigned when a Mixie instance is created
    
    def showInfo(self):
        print(
            'Mixie v%s'%VERSION,
            'Usage','-----',
            'mixie [tag] [moretags] [- [avoidtag] [moreavoidtags]]',
            'mixie play trackname',
            'mixie scan',
            'mixie retag [search_trackname_to_retag]',
            'mixie alltags',
            sep='\n'
        )

    def getLibrary(self) -> str:
        '''to ask User for the library location(s)'''
        print(
            'Mixie needs to scan your Music Library for setup',
            'Run `mixie scan` after setup to tag contents in your library for use',
            'Library Location : ',
            sep='\n', end='')
        library = input()
        if isdir(library):
            print('Mixie Setup complete')
            return library
        else:
            print("Mixie Setup failed: directory is invalid")
            exit() # TODO handle error gracefully
        
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
        '''UI for tag functionality'''
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
        '''UI for scan functionality'''
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
        playlist = self.mixie.selectSpecific(trackName)
        self.loadPlaylist(playlist)
    
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

        playlist = self.mixie.mix(addtags, subtags)
        self.loadPlaylist(playlist)

    def loadPlaylist(self, playlist): # TODO mediaManager should handle this
        if not playlist:
            return
        print(*playlist, '', 'Play Selection ? ', sep='\n', end='')
        if 'no' in input().lower():
            return

        system(QUERY_VLC_START)
        log(QUERY_VLC_START+'\nVLC started :\\')
        for track in playlist:
            system(QUERY_VLC_ENQUE%track)
    
    def showAllTags(self):
        self.showTags(self.mixie.allTags())
    
    def showTags(self, tags):
        if not tags:
            return
        print('\n', *['%15s'%tag for tag in tags], sep='\t\t', end='\n')

class Mixie:
    '''contains the logic to handle processes'''

    def __init__(self, controller:MixieController):
        '''attaches the instance of Mixie to the controller and acquires an instance of the fileManager'''
        controller.mixie = self
        self.fileManager = FileManager.getInstance(controller, MIXIECONFIG)
        self.db = self.fileManager.loadDB() # TODO rename db to cache for understanding

    def mix(self, addtags, subtags):
        '''cooks the playlist from the choice of tags'''
        playlist = {
            track for track in self.db
            if self.db[track] & addtags and not self.db[track] & subtags
        }
        return playlist
    
    def selectSpecific(self, trackName):
        '''cooks the playlist depending on song matching a keyword'''
        playlist = {track for track in self.db if trackName in track}
        return playlist
    
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
        filesInLib:set = self.fileManager.getFilesInLibrary() # TODO: make options for multiple library locations
        filesInCache:set = set(self.db)
        untaggedFiles = [file for file in sorted(filesInLib - filesInCache)]
        badTags = sorted(set(self.db) - filesInCache)
        return untaggedFiles, badTags

    def tag(self, track:str, newTags:set, keepOldTag=False):
        '''edits tags of a track'''
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
        self.fileManager.saveDB(self.db)

if __name__ == '__main__':
    cliArgs = [arg.lower() for arg in argv][1:]
    log('cliArgs:', cliArgs)

    controller = MixieController()
    # filer = FileManager.getInstance(controller)
    mixie = Mixie(controller)

    controller.main(cliArgs)
