from os import environ, sep
from sys import argv
from FileManager import *
from Controllers import *

TESTING = True#False#
MIXIECONFIG = sep.join([environ['USERPROFILE'], 'mixie.db']) if not TESTING else 'mixie.db'
def log(*args, wait=False, **kwargs):
    if TESTING:
        print(*args, **kwargs)
        if wait: input()

class Mixie:
    '''contains the logic to handle processes'''
    VERSION = '6.0.0 arch'

    def __init__(self, fileManager:"FileManager"):
        '''attaches the instance of Mixie to the controller and acquires an instance of the fileManager'''
        self.fileManager = fileManager
        self.dbCache = self.fileManager.loadDB()

    def mix(self, addtags:set, subtags:set=set()) -> set:
        '''cooks the playlist from the choice of tags'''
        playlist = {
            track for track in self.dbCache
            if self.dbCache[track] & addtags and not self.dbCache[track] & subtags
        }
        return playlist
    
    def selectSpecific(self, searchKey:str) -> set:
        '''cooks the playlist depending on song matching a keyword'''
        playlist = { track for track in self.dbCache if searchKey in track }
        return playlist
    
    def findTracks(self, searchKey:str) -> list:
        '''returns a list of tracks that match the searchKey'''
        return [
            track for track in sorted(self.dbCache)
            if searchKey in track
        ]
    
    def allTags(self) -> list:
        '''returns a sorted list of all the tags used across the library'''
        return sorted({tag for track in self.dbCache for tag in self.dbCache[track]})
    
    def tagsOfTrack(self, track) -> list:
        return sorted(self.dbCache[track]) if track in self.dbCache else []
    
    def scan(self):
        '''
        Scans the entire library and returns two sets.\n  
        One containing files that are not tagged\n  
        The other containing files that were tagged but don't exist in the right location.  
        '''
        filesInLib:set = self.fileManager.getFilesInLibrary() # TODO: make options for multiple library locations
        filesInCache:set = set(self.dbCache)
        untaggedFiles = sorted(filesInLib - filesInCache)
        badFiles = sorted(filesInCache - filesInLib)
        return untaggedFiles, badFiles

    def tag(self, track:str, newTags:set, keepOldTag=False):
        '''edits tags of a track'''
        if newTags:
            newTags = {tag.lower() for tag in newTags}
            if keepOldTag:
                self.dbCache[track] |= newTags
            else:
                self.dbCache[track] = newTags
            self.saveDb()

    def replaceTrack(self, oldTrack:str, newTrack:str):
        if (oldTrack in self.dbCache) and (oldTrack!=newTrack):
            self.dbCache[newTrack] = self.dbCache[oldTrack]
            self.forgetTrack(oldTrack)
    
    def forgetTrack(self, track:str):
        '''removes all tags and existence of a track from memory'''
        if track in self.dbCache:
            self.dbCache.pop(track)
            self.saveDb()
    
    def saveDb(self):
        '''makes fileManager save db to file'''
        self.fileManager.saveDB(self.dbCache)

if __name__ == '__main__':
    cliArgs = [arg.lower() for arg in argv][1:]
    log('cliArgs:', cliArgs)

    mixie = Mixie()
    controller = CLIController(mixie)
    filer = FileManager.getInstance(controller)

    controller.main(cliArgs)
