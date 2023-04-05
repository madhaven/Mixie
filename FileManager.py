import sqlite3 as sql
from abc import abstractmethod, abstractstaticmethod
import os
import Mixie


class FileManager:
    '''handles the save and load of Mixie data'''
    instance = None
    MUSIC_FILES = []
    filers = None
    latestFiler:"FileManager" = None

    qGetValueOfKey = "SELECT value FROM core WHERE key=?"
    qCoreInit = "CREATE TABLE IF NOT EXISTS core(key VARCHAR UNIQUE, value VARCHAR)"
    qCoreInsert = "INSERT INTO core(key, value) VALUES(?, ?)"

    @abstractmethod
    def __init__(self, dbFile, libraryLocation, nonMusicFileTypes:list=None):
        # call super().__init__() while overriding this init
        self.dbFile = dbFile
        self.libraryLocation = libraryLocation
        if not nonMusicFileTypes:
            self.MUSIC_FILES.extend(['mp3', 'MP3'])

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
        libFiles:set = set()
        for root, _, files in os.walk(self.libraryLocation):
            for file in files:
                if avoidNonMusic and file[file.rfind('.')+1:] in self.MUSIC_FILES:
                    filename = os.path.join(root, file)
                    if os.name == 'nt': # windows OS
                        filename = filename.lower()
                    libFiles.add(filename)
        return libFiles
    
    @classmethod
    def initializeFiles(cls, libraryLocation:str, MIXIEDB:str, useFiler:"FileManager"=None):
        '''sets up the core table of the db with basic information
        useFiler specifies a certain FileManager to be used instead of the latest available
        '''

        con = sql.connect(MIXIEDB)
        cur = con.cursor()
        cur.execute(cls.qCoreInit)
        filer = useFiler.filerID() if useFiler else cls.latestFiler.filerID()
        cur.execute(cls.qCoreInsert, ('FileManagerStandard', filer))
        cur.execute(cls.qCoreInsert, ('Library', libraryLocation))
        con.commit()
        con.close()

    @classmethod
    def getInstance(cls, controller:"Mixie.CLIController", MIXIEDB:str = None, useFiler=None) -> "FileManager":
        '''Returns a singleton instance of a fileManager
        useFiler if specified will force the usage of a specific FileManager instead of the latest'''

        if cls.instance:
            return cls.instance

        if not MIXIEDB or not os.path.isfile(MIXIEDB):
            cls.initializeFiles(controller.getLibrary(), MIXIEDB, useFiler)

        # Find apt FileManager for DB
        con = sql.connect(MIXIEDB)
        cur = con.cursor()
        cur.execute(cls.qGetValueOfKey, ('FileManagerStandard',))
        res = cur.fetchone()
        if not res:
            con.close()
            Mixie.log('handle file read errors')
            exit() # TODO: handle file read errors
        filerId = res[0]
        for filer in cls.filers:
            if filer.filerID() == filerId:
                aptFiler = filer
                break
        else:
            con.close()
            Mixie.log('handle file read errors 2')
            exit() # TODO: handle file read errors

        # Find Library location
        cur.execute(cls.qGetValueOfKey, ('Library',))
        res = cur.fetchone()
        con.commit()
        con.close()
        if not res:
            Mixie.log('handle file read errors 3')
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
    qDelSong = '''DELETE FROM song WHERE location=? and songname=?'''
    qGetSongId = '''SELECT id FROM song WHERE location=? and songname=?'''
    qPutSong = '''INSERT INTO song(location, songname) VALUES (?, ?)'''
    qGetTagId = '''SELECT id FROM tag WHERE tagname=?'''
    qPutTag = '''INSERT INTO tag(tagname) VALUES (?)'''
    qPutLink = '''INSERT INTO link(songid, tagid) VALUES (?, ?)'''
    qCreateSongTable = '''CREATE TABLE IF NOT EXISTS song(id INTEGER PRIMARY KEY, location TEXT COLLATE NOCASE, songname TEXT COLLATE NOCASE)'''
    qCreateTagTable = '''CREATE TABLE IF NOT EXISTS tag(id INTEGER PRIMARY KEY, tagname TEXT)'''
    qCreateLinkTable = '''CREATE TABLE IF NOT EXISTS link(songid, tagid)'''
    qGetDuplicateSongs = '''SELECT a.id aid, a.songname aname, b.id bid, b.songname bname from song a INNER JOIN song b on LOWER(a.songname)=LOWER(b.songname) where a.id <> b.id'''

    def __init__(self, dbLocation, libraryLocation):
        super().__init__(dbLocation, libraryLocation)
        con, cur = self._connect_()
        self.prepDB(con, cur)
        con.close()
    
    def _connect_(self):
        '''Sets up the db if not used and returns the Connection and Cursor for operations'''
        con:sql.Connection = sql.connect(self.dbFile)
        cur = con.cursor()
        return con, cur

    @staticmethod
    def filerID():
        return 'BabyFileManager'
    
    def prepDB(self, con:sql.Connection, cur:sql.Cursor):
        '''initialize DB tables'''
        cur.execute(self.qCreateSongTable)
        cur.execute(self.qCreateTagTable)
        cur.execute(self.qCreateLinkTable)
        con.commit()

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
            if os.name == 'nt': # case-insensitive Windows OS
                id = id.lower()
            if id in cache:
                cache[id] |= {tag,}
            else:
                cache[id] = {tag,}
        return cache
    
    def saveDB(self, betaCache:dict) -> None: # TODO optimize
        '''saves the provided dictionary cache to the file after finding the delta'''

        oldDb = self.loadDB()
        filesToRemove = set(oldDb) - set(betaCache)
        deltaCache = { x: betaCache[x] for x in filter(
            lambda id: id not in oldDb or oldDb[id]!=betaCache[id], 
            betaCache
        )}

        con, cur = self._connect_()
        for track in deltaCache:
            filename = track[track.rfind(os.sep) + 1:]
            location = track[:track.rfind(os.sep) + 1]
            
            if track not in oldDb:
                cur.execute(self.qPutSong, (location, filename))
                trackId = cur.lastrowid
            else:
                cur.execute(self.qGetSongId, (location, filename))
                trackId = cur.fetchone()[0]
                cur.execute(self.qDelLinks, (trackId,))

            for tag in deltaCache[track]:
                # find tagid or insert new tag
                cur.execute(self.qGetTagId, (tag,))
                tagid = cur.fetchone()
                if tagid:
                    tagid = tagid[0]
                else:
                    cur.execute(self.qPutTag, (tag,))
                    tagid = cur.lastrowid
                cur.execute(self.qPutLink, (trackId, tagid))
        
        # remove files from old db
        for track in filesToRemove:
            filename = track[track.rfind(os.sep) + 1:]
            location = track[:track.rfind(os.sep) + 1]
            cur.execute(self.qGetSongId, (location, filename))
            trackId = cur.fetchone()[0]
            cur.execute(self.qDelSong, (location, filename))
            cur.execute(self.qDelLinks, (trackId,))
        
        # TODO: remove tags not used anymore
        
        con.commit()
        con.close()
        Mixie.log('tagDb saved')

# REGISTER SUBCLASSES HERE, LATEST LAST ORDER
FileManager.filers = [BabyFileManager]
FileManager.latestFiler = FileManager.filers[-1]