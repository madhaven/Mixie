import sqlite3 as sql
from abc import abstractmethod
from os import environ, sep, system, walk
from os.path import isfile
from sys import argv

TESTING = True#False#
VERSION = '6.0.0 arch'
QUERY_VLC_START = 'start vlc --random --loop --playlist-autostart --qt-start-minimized --one-instance --mmdevice-volume=0.35'
QUERY_VLC_ENQUE = 'start vlc --qt-start-minimized --one-instance --playlist-enqueue "%s"'
QUERY_VLC_PREVIEW = 'start /b vlc.exe --playlist-enqueue "%s"'
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()

class FileManager:
    NON_MUSIC_FILES = ('jpg', 'ini', 'mp4', 'wmv')
    '''handles the save and load of Mixie data'''

    @abstractmethod
    def __init__(self, libraryLocation, dbFile):
        # call super().__init__() while overriding this init
        self.libraryLocation = libraryLocation
        self.dbFile = dbFile
        if TESTING:
            self.dbFile = 'mixie.db'
    
    @abstractmethod
    def getSongs(self, tags:list, matchAll=False):
        '''returns a list of tracks that contain any/all of the tags in the list provided'''
        raise NotImplementedError

    @abstractmethod
    def tagsOfTrack(self, trackName):
        '''returns a list of tags associated to a track'''
        raise NotImplementedError # todo change implementation to trackid
    
    @abstractmethod
    def getSongsFromSearch(self, keyword:str):
        '''returns a list of track that contain the keyword in their full file name.'''
        raise NotImplementedError
    
    def getFilesInLibrary(self, avoidNonMusic=True) -> set:
        '''walks through the file tree with `os.walk` and returns a set of all files included'''
        return {
            (root + sep + file).lower()
            for root, _, files in walk(self.libraryLocation)
            for file in files
            if avoidNonMusic and file.split('.')[-1] not in self.NON_MUSIC_FILES
        }
    
    @abstractmethod
    def getFilesInDb(self) -> set:
        '''walks through the db and returns a set of all files included'''
        raise NotImplementedError

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
    
    def setupDB(self, con:sql.Connection=None):
        '''initialize tables'''
        if not con:
            con2, cur = self._connect_()
        else:
            cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS song(id, location, songname)")
        cur.execute("CREATE TABLE IF NOT EXISTS tag(id, tagname)")
        cur.execute("CREATE TABLE IF NOT EXISTS link(songid, tagid)")
        if not con:
            con2.commit()
            con2.close()
        else:
            con.commit()
    
    def _connect_(self):
        '''Sets up the db if not used and returns the Connection and Cursor for operations.\n
        `.close()` should be called on the connection after operations'''
        if not isfile(self.dbFile):
            con:sql.Connection = sql.connect(self.dbFile)
            self.setupDB(con)
        else:
            con:sql.Connection = sql.connect(self.dbFile)
        cur = con.cursor()
        return con, cur
    
    def getSongs(self, tags:list, avoidList:list=None, matchAll=False):
        '''returns a records of songs which contain the tags'''
        con, cur = self._connect_()
        tags = ', '.join(["'%s'"%tag for tag in tags])
        avoidList = ', '.join(["'%s'"%tag for tag in avoidList]) if avoidList else ''
        if matchAll:
            raise NotImplementedError # TODO
        query = '''
SELECT location, songname FROM song s INNER JOIN link l ON s.id=l.songid INNER JOIN tag t ON l.tagid=t.id WHERE t.tagname IN (%s)
EXCEPT
SELECT location, songname FROM song s INNER JOIN link l ON s.id=l.songid INNER JOIN tag t ON l.tagid=t.id WHERE t.tagname IN (%s)
        '''%(tags, avoidList)
        cur.execute(query)
        res = cur.fetchall()
        con.close()
        return res
    
    def tagsOfTrack(self, trackName):
        con, cur = self._connect_()
        query = '''SELECT tagname FROM tag IF id IN (SELECT tagid FROM song s INNER JOIN link l ON s.id=l.songid WHERE songname = ?)'''
        cur.execute(query, (trackName,))
        con.close()
        return
    
    def getSongsFromSearch(self, keyword: str):
        '''returns songs with the keyword in their full address'''
        con, cur = self._connect_()
        query = '''SELECT location, songname FROM song WHERE location like '%%%s%%' OR songname like '%%%s%%' '''%(keyword, keyword)
        cur.execute(query)
        res = cur.fetchall()
        con.close()
        return res
    
    def getFilesInDb(self):
        con, cur = self._connect_()
        query = '''SELECT location, songname from song'''
        cur.execute(query)
        res = cur.fetchall()
        con.close()
        return {location + track for location, track in res}

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
            'Mixie v%s'%VERSION,
            'Usage','-----',
            'mixie [tag] [moretags] [- [avoidtag] [moreavoidtags]]',
            'mixie play trackname',
            'mixie scan',
            'mixie retag [search_trackname_to_retag]',
            'mixie alltags',
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
    
    def mix(self, addtags, subtags):
        '''cooks the playlist from the choice of tags'''
        tracks = self.fileManager.getSongs(addtags, subtags)
        playlist = [location+track for location, track in tracks]
        if playlist:
            self.loadPlaylist(playlist) # TODO add media manager here
    
    def loadPlaylist(self, playlist): # TODO mediaManager should handle this
        system(QUERY_VLC_START)
        log(QUERY_VLC_START+'\nVLC started :\\')
        for song in playlist:
            log(QUERY_VLC_ENQUE%song)
            system(QUERY_VLC_ENQUE%song)
    
    def playSpecific(self, songName):
        '''cooks the playlist depending on song matching a keyword'''
        playlist = self.findTracks(songName)
        if playlist:
            self.loadPlaylist(playlist)
    
    def findTracks(self, searchKey:str) -> set:
        '''returns a set of tracks that match the searchKey'''
        if not searchKey:
            return set()
        else:
            return {
                location + track
                for location, track in self.fileManager.getSongsFromSearch(searchKey)}
    
    def allTags(self):
        '''returns a sorted list of all the tags used across the library'''
        # printTags(sorted({tag for track in TAG_DB for tag in TAG_DB[track]}))
        return sorted({tag for track in self.db for tag in self.db[track]})
    
    def tagsOfTrack(self, track):
        tags = self.fileManager.tagsOfTrack(track)
        return {tag for tag in tags}
    
    def scan(self):
        '''
        Scans the entire library and returns two sets.\n  
        One containing files that are not tagged\n  
        The other containing files that were tagged but don't exist in the saved location.  
        '''
        filesInLib:set = self.fileManager.getFilesInLibrary() # TODO: make options for multiple library locations
        filesInDB:set = self.fileManager.getFilesInDb()
        untaggedFiles = sorted(filesInLib - filesInDB)
        badTags = sorted(filesInDB - filesInLib)
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