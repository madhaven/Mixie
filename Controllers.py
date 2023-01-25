import Mixie
import os
import MediaManager
import abc


class BaseController(abc.ABC):
    '''Base Controller defining APIs for User Interaction'''

    # TODO: make static method to get the latest instance
    # TODO: singleton implementation

    @abc.abstractmethod
    def showInfo(self) -> None:
        '''provide all info about Mixie to the user'''
        raise NotImplementedError

    @abc.abstractmethod
    def getLibrary(self) -> str:
        '''returns the library location(s)'''
        raise NotImplementedError
    
    @abc.abstractmethod
    def main(self, args) -> None:
        '''Processes the args and decides the operation mode'''
        raise NotImplementedError
    
    @abc.abstractmethod
    def tag(self, *args) -> None:
        '''UI for tagging functionality'''
        raise NotImplementedError

    @abc.abstractmethod
    def scan(self, *args) -> None:
        '''UI for scan functionality'''
        raise NotImplementedError

    @abc.abstractmethod
    def playSpecific(self, *args) -> None:
        '''UI for playing a specific song'''
        raise NotImplementedError
    
    @abc.abstractmethod
    def mix(self, *args) -> None:
        '''UI for setting up the playlist'''
        raise NotImplementedError

class CLIController(BaseController):
    '''handles all cli interaction'''
    
    def __init__(self):
        '''Initializes the controller'''
        self.mixie:Mixie.Mixie = None # to be assigned when a Mixie instance is created
    
    def showInfo(self):
        print(
            'Mixie v%s'%self.mixie.VERSION,
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
        if os.path.isdir(library):
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
        '''UI for tagging functionality'''
        try:
            print('Add tags (space separated) to your tracks.\nPress return to skip\nPress Ctrl+C to exit tagging tracks\n')                
            search_key = (input('Search for a track: ') if not args else ' '.join(args)).lower()
            
            tracks = self.mixie.findTracks(search_key)
            if not tracks:
                print('No such track found')
            
            for track in tracks:
                print(track, ':', *self.mixie.tagsOfTrack(track), end=': ')
                os.system(MediaManager.MediaManager.QUERY_VLC_PREVIEW%track) # TODO: change vlc pings to Media Manager
                tags = set(input().lower().split())
                self.mixie.tag(track, tags)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            Mixie.log(e)
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
                    os.system(MediaManager.MediaManager.QUERY_VLC_PREVIEW%track) # TODO: media player should handle previewing songs
                    tags = set(input().lower().split())
                    self.mixie.tag(track, tags)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                os.log(e)
            finally:
                print('Tagging Terminated')

        if badTags and 'no' not in input('\n%d tracks were not found in library, Fix them now ? '%len(badTags)).lower():
            print('\nDrag-n-drop new file to update track location\nPress return to forget the track\nPress Ctrl+C to exit')
            try:
                for i, track in enumerate(badTags):
                    print('%5.2f%% %s'%((i+1)*100/len(badTags), track))
                    newTrack = input('drop new track : ')
                    if newTrack[0] == '"' == newTrack[-1]:
                        newTrack = newTrack[1:-1]
                    self.mixie.replaceTrack(track, newTrack)
            except Exception as e: Mixie.log(e)
            except: pass
            finally: print('ReTracking Terminated')
    
    def playSpecific(self, *args):
        '''UI for playing a specific song'''
        trackName = input('Song to play : ') if not args else ' '.join(args)
        playlist = self.mixie.selectSpecific(trackName)
        self.loadPlaylist(playlist)
    
    def mix(self, *args):
        '''UI for setting up the playlist'''
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

        os.system(MediaManager.MediaManager.QUERY_VLC_START)
        Mixie.log(MediaManager.MediaManager.QUERY_VLC_START+'\nVLC started :\\')
        for track in playlist:
            os.system(MediaManager.MediaManager.QUERY_VLC_ENQUE%track)
    
    def showAllTags(self):
        self.showTags(self.mixie.allTags())
    
    def showTags(self, tags):
        if not tags:
            return
        print('\n', *['%15s'%tag for tag in tags], sep='\t\t', end='\n')