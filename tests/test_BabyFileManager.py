from unittest import TestCase, main
from FileManager import BabyFileManager, FileManager
import sqlite3 as sql
from os import sep, path, remove
from Controllers import BaseController, CLIController
from random import randint


class DummyCLIController(CLIController):
    def getLibrary(self) -> str:
        return '.'

class BabyFileManagerTests(TestCase):
    testDB = 'test_testDB_1323.db'
    testLib = '.'

    def setUp(self):
        self.testDB = 'test_testDB_%d.db'%randint(0, 9999)
        return super().setUp()
    
    def tearDown(self):
        if path.isfile(self.testDB):
            remove(self.testDB)
        return super().tearDown()

    def test_properIDReturned(self):
        filer = FileManager.getInstance(DummyCLIController(), self.testDB, BabyFileManager)
        if path.isfile(self.testDB):
            remove(self.testDB)
        self.assertEqual('BabyFileManager', filer.filerID(), 'Improper ID returned')

    def test_loadDB(self):
        filer = FileManager.getInstance(DummyCLIController(), self.testDB, BabyFileManager)
        filer.clearInstance()
        con = sql.connect(self.testDB)
        cur = con.cursor()
        cur.execute(BabyFileManager.qCreateSongTable)
        cur.execute(BabyFileManager.qCreateLinkTable)
        cur.execute(BabyFileManager.qCreateTagTable)

        cur.execute(BabyFileManager.qPutSong, ('.'+sep, 'sample.mp3'))
        cur.execute(BabyFileManager.qPutTag, ('happy',))
        cur.execute(BabyFileManager.qGetSongId, ('.'+sep, 'sample.mp3'))
        songid = cur.fetchone()[0]
        cur.execute(BabyFileManager.qGetTagId, ('happy',))
        happyTagId = cur.fetchone()[0]
        cur.execute(BabyFileManager.qPutLink, (songid, happyTagId))

        cur.execute(BabyFileManager.qPutSong, ('.'+sep, 'sample2.mp3'))
        cur.execute(BabyFileManager.qPutTag, ('crazy',))
        cur.execute(BabyFileManager.qGetSongId, ('.'+sep, 'sample2.mp3'))
        songid = cur.fetchone()[0]
        cur.execute(BabyFileManager.qGetTagId, ('crazy',))
        crazyTagId = cur.fetchone()[0]
        cur.execute(BabyFileManager.qPutLink, (songid, happyTagId))
        cur.execute(BabyFileManager.qPutLink, (songid, crazyTagId))

        con.commit()
        con.close()
        
        filer = BabyFileManager(self.testDB, self.testLib)
        d1 = filer.loadDB()
        d2 = {
            sep.join(['.', 'sample.mp3']): {'happy',},
            sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'}
        }
        if path.isfile(self.testDB):
            remove(self.testDB)
        self.assertDictEqual(d1, d2, 'DB not loaded properly')

    def test_saveDB(self):
        if path.isfile(self.testDB):
            remove(self.testDB)
        filer:BabyFileManager = FileManager.getInstance(DummyCLIController(), self.testDB, BabyFileManager)
        filer.saveDB({
            sep.join(['.', 'sample.mp3']): {'happy',},
            sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'}
        })

        con = sql.connect(self.testDB)
        cur = con.cursor()
        cur.execute("SELECT * FROM song")
        songs = set(cur.fetchall())
        cur.execute("SELECT * FROM tag")
        tags = set(cur.fetchall())
        cur.execute("SELECT * from link")
        links = set(cur.fetchall())
        con.close()
        if path.isfile(self.testDB):
            remove(self.testDB)

        self.assertSetEqual(songs, {
            (1, '.' + sep, 'sample.mp3'),
            (2, '.' + sep, 'sample2.mp3')
        }, 'DB not saved properly')
        self.assertSetEqual(tags, {
            (1, 'happy'),
            (2, 'crazy')
        }, 'DB not saved properly')
        self.assertSetEqual(links, {
            (1, 1),
            (2, 1),
            (2, 2)
        }, 'DB not saved properly')
    
    def test_saveDB2(self):
        if path.isfile(self.testDB):
            remove(self.testDB)
        filer:BabyFileManager = FileManager.getInstance(DummyCLIController(), self.testDB, BabyFileManager)
        filer.saveDB({
            sep.join(['.', 'sample.mp3']): {'happy',},
            sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'}
        })
        filer.saveDB({
            sep.join(['.', 'sample.mp3']): {'happy',},
            sep.join(['.', 'sample2.mp3']): {'sad',}
        })

        con = sql.connect(self.testDB)
        cur = con.cursor()
        cur.execute("SELECT * FROM song")
        songs = set(cur.fetchall())
        cur.execute("SELECT * FROM tag")
        tags = set(cur.fetchall())
        cur.execute("SELECT * from link")
        links = set(cur.fetchall())
        con.close()
        if path.isfile(self.testDB):
            remove(self.testDB)
        
        self.assertSetEqual(songs, {
            (1, '.' + sep, 'sample.mp3'),
            (2, '.' + sep, 'sample2.mp3')
        }, 'DB not saved properly')
        self.assertSetEqual(tags, {
            (1, 'happy'),
            (2, 'crazy'),
            (3, 'sad')
        }, 'DB not saved properly')
        self.assertSetEqual(links, {
            (1, 1),
            (2, 3)
        }, 'DB not saved properly')

    def test_saveDB3(self):
        if path.isfile(self.testDB):
            remove(self.testDB)
        filer:BabyFileManager = FileManager.getInstance(DummyCLIController(), self.testDB, BabyFileManager)
        filer.saveDB({
            sep.join(['.', 'sample.mp3']): {'happy',},
            sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'}
        })
        filer.saveDB({
            sep.join(['.', 'sample.mp3']): {'happy',}
        })

        con = sql.connect(self.testDB)
        cur = con.cursor()
        cur.execute("SELECT * FROM song")
        songs = set(cur.fetchall())
        cur.execute("SELECT * FROM tag")
        tags = set(cur.fetchall())
        cur.execute("SELECT * from link")
        links = set(cur.fetchall())
        con.close()
        if path.isfile(self.testDB):
            remove(self.testDB)
        
        self.assertSetEqual(songs, {
            (1, '.' + sep, 'sample.mp3'),
        }, 'DB not saved properly')
        self.assertSetEqual(tags, {
            (1, 'happy'),
            (2, 'crazy') # TODO: remove unused tags in saveDB()
        }, 'DB not saved properly')
        self.assertSetEqual(links, {
            (1, 1),
        }, 'DB not saved properly')
