import sqlite3 as sql
from abc import *
from os import sep, walk, environ
from os.path import isfile
from Mixie import log, MixieController


class FileManager:
    '''handles the save and load of Mixie data'''
    instance = None
    NON_MUSIC_FILES = []
    filers = None
    latestFiler:"FileManager" = None

    @abstractmethod
    def __init__(self, dbFile, libraryLocation, nonMusicFileTypes:list=None):
        # call super().__init__() while overriding this init
        self.dbFile = dbFile
        self.libraryLocation = libraryLocation
        if not nonMusicFileTypes:
            self.NON_MUSIC_FILES.extend(['jpg', 'ini', 'mp4', 'wmv'])

    @abstractstaticmethod
    def filerID(self):
        '''should return a string that identifies the FileManager'''
        raise NotImplementedError

    @abstractmethod
    def loadDB(self) -> dict:
        '''reads the db and returns the resultant dictionary'''
        raise NotImplementedError
    
    @abstractmethod
    def saveDB(self, tagDict:dict):
        '''saves the provided dictionary to the file.'''
        raise NotImplementedError
    
    def getFilesInLibrary(self, avoidNonMusic=True) -> set:
        '''walks through the file tree with `os.walk` and returns a set of all files included'''
        return {
            (root + sep + file)
            for root, _, files in walk(self.libraryLocation)
            for file in files
            if avoidNonMusic and file.split('.')[-1] not in self.NON_MUSIC_FILES
        }
    
    @classmethod
    def initializeFiles(cls, libraryLocation:str, MIXIEDB:str, useFiler:"FileManager"=None):
        '''sets up the core table of the db with basic information
        useFiler forces the usage of a specific FileManager instead of the latest available
        '''
        
        qCoreInit = "CREATE TABLE IF NOT EXISTS core(key VARCHAR UNIQUE, value VARCHAR)"
        qCoreInsert = "INSERT INTO core(key, value) VALUES(?, ?)"

        con = sql.connect(MIXIEDB)
        cur = con.cursor()
        cur.execute(qCoreInit)
        filer = useFiler.filerID() if useFiler else cls.latestFiler.filerID()
        cur.execute(qCoreInsert, ('FileManagerStandard', filer))
        cur.execute(qCoreInsert, ('Library', libraryLocation))
        con.commit()
        con.close()

    @classmethod
    def getInstance(cls, controller:"MixieController", MIXIEDB:str = None, useFiler=None) -> "FileManager":
        '''Returns a singleton instance of a fileManager
        useFiler if specified will force the usage of a specific FileManager instead of the latest'''

        if cls.instance:
            return cls.instance

        if not MIXIEDB or not isfile(MIXIEDB):
            cls.initializeFiles(controller.getLibrary(), MIXIEDB, useFiler)

        con = sql.connect(MIXIEDB)
        cur = con.cursor()
        cur.execute("SELECT value FROM core WHERE key=?", ('FileManagerStandard',))
        res = cur.fetchone()
        if not res:
            con.close()
            log('handle file read errors')
            exit() # TODO: handle file read errors
        filerId = res[0]
        for filer in cls.filers:
            if filer.filerID() == filerId:
                aptFiler = filer
                break
        else:
            con.close()
            log('handle file read errors 2')
            exit() # TODO: handle file read errors

        cur.execute("SELECT value FROM core WHERE key=?", ('Library',))
        res = cur.fetchone()
        con.commit()
        con.close()
        if not res:
            log('handle file read errors 3')
            exit() # TODO: handle file read errors
        library = res[0] # TODO: add multiple locations
        cls.instance = aptFiler(MIXIEDB, library)
        return cls.instance

    @classmethod
    def clearInstance(cls):
        '''Clears the singleton class from usage'''
        if cls.instance:
            cls.instance = None

class BabyFileManager(FileManager):
    qDelLinks = '''DELETE FROM link WHERE songid=?'''
    qFetchSongId = '''SELECT id FROM song WHERE location=? and songname=?'''
    qInsertSong = '''INSERT INTO song(location, songname) VALUES (?, ?)'''
    qFetchTagId = '''SELECT id FROM tag WHERE tagname=?'''
    qInsertTag = '''INSERT INTO tag(tagname) VALUES (?)'''
    qInsertLink = '''INSERT INTO link(songid, tagid) VALUES (?, ?)'''
    qCreateSongTable = '''CREATE TABLE IF NOT EXISTS song(id INTEGER PRIMARY KEY, location VARCHAR, songname VARCHAR)'''
    qCreateTagTable = '''CREATE TABLE IF NOT EXISTS tag(id INTEGER PRIMARY KEY, tagname VARCHAR)'''
    qCreateLinkTable = '''CREATE TABLE IF NOT EXISTS link(songid, tagid)'''

    def __init__(self, dbLocation, libraryLocation):
        super().__init__(dbLocation, libraryLocation)
        con, cur = self._connect_()
        self.prepDB(con, cur)
        con.close()
    
    @staticmethod
    def filerID():
        return 'BabyFileManager'
    
    def prepDB(self, con:sql.Connection, cur:sql.Cursor):
        '''initialize DB'''
        cur.execute(self.qCreateSongTable)
        cur.execute(self.qCreateTagTable)
        cur.execute(self.qCreateLinkTable)
        con.commit()
    
    def _connect_(self):
        '''Sets up the db if not used and returns the Connection and Cursor for operations'''
        con:sql.Connection = sql.connect(self.dbFile)
        cur = con.cursor()
        return con, cur

    def loadDB(self) -> dict:
        '''reads the db and returns the resultant dictionary'''
        con, cur = self._connect_()
        query = "SELECT location, songname, tagname FROM song s INNER JOIN link l on s.id=l.songid INNER JOIN tag t on t.id=l.tagid"
        cur.execute(query)
        res = cur.fetchall()
        con.close()

        cache = dict()
        for location, track, tag in res:
            id = location + track
            if id in cache:
                cache[id] |= {tag,}
            else:
                cache[id] = {tag,}
        return cache
    
    def saveDB(self, betaCache:dict) -> None:
        '''saves the provided dictionary cache to the file after finding the delta'''
        alphaCache = self.loadDB()
        deltaCache = dict()
        for id in betaCache:
            if id in alphaCache:
                if alphaCache[id] != betaCache[id]:
                    deltaCache[id] = betaCache[id]
            else:
                deltaCache[id] = betaCache[id]
        # TODO: what's teh poitn of this ?

        con, cur = self._connect_()
        for id in deltaCache:
            # find song id or insert new song
            track = id.split(sep)[-1]
            location = sep.join(id.split(sep)[:-1])
            cur.execute(self.qFetchSongId, (location, track))
            trackId = cur.fetchone()
            if not trackId:
                cur.execute(self.qInsertSong, (location, track))
                trackId = cur.lastrowid
            else:
                trackId = trackId[0]
                cur.execute(self.qDelLinks, (trackId,))

            for tag in deltaCache[id]:
                # find tagid or insert new tag
                cur.execute(self.qFetchTagId, (tag,))
                tagid = cur.fetchone()
                if tagid:
                    tagid = tagid[0]
                else:
                    cur.execute(self.qInsertTag, (tag,))
                    tagid = cur.lastrowid
                cur.execute(self.qInsertLink, (trackId, tagid))
        
        con.commit()
        con.close()
        log('tagDb saved')

#REGISTER SUBCLASSES HERE, LATEST LAST ORDER
FileManager.filers = [BabyFileManager]
FileManager.latestFiler = FileManager.filers[-1]