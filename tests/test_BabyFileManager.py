from unittest import TestCase, main
from FileManager import BabyFileManager, FileManager
import sqlite3 as sql
from os import sep, path, remove
from Controllers import BaseController, CLIController


class DummyCLIController(CLIController):
    def getLibrary(self) -> str:
        return '.'

class BabyFileManagerTests(TestCase):
    testDB = 'test_testDB_1323.db'
    testLib = '.'

    @classmethod
    def tearDownClass(cls) -> None:
        if path.isfile(cls.testDB):
            remove(cls.testDB)
        return super().tearDownClass()

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

        cur.execute(BabyFileManager.qInsertSong, ('.'+sep, 'sample.mp3'))
        cur.execute(BabyFileManager.qInsertTag, ('happy',))
        cur.execute(BabyFileManager.qFetchSongId, ('.'+sep, 'sample.mp3'))
        songid = cur.fetchone()[0]
        cur.execute(BabyFileManager.qFetchTagId, ('happy',))
        happyTagId = cur.fetchone()[0]
        cur.execute(BabyFileManager.qInsertLink, (songid, happyTagId))

        cur.execute(BabyFileManager.qInsertSong, ('.'+sep, 'sample2.mp3'))
        cur.execute(BabyFileManager.qInsertTag, ('crazy',))
        cur.execute(BabyFileManager.qFetchSongId, ('.'+sep, 'sample2.mp3'))
        songid = cur.fetchone()[0]
        cur.execute(BabyFileManager.qFetchTagId, ('crazy',))
        crazyTagId = cur.fetchone()[0]
        cur.execute(BabyFileManager.qInsertLink, (songid, happyTagId))
        cur.execute(BabyFileManager.qInsertLink, (songid, crazyTagId))

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
        filer = FileManager.getInstance(DummyCLIController(), self.testDB, BabyFileManager)
        con = sql.connect(self.testDB)
        cur = con.cursor()
        cur.execute(filer.qCreateSongTable)
        cur.execute(filer.qCreateLinkTable)
        cur.execute(filer.qCreateTagTable)
        con.commit()
        con.close()

        d = {
            sep.join(['.', 'sample.mp3']): {'happy',},
            sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'}
        }
        filer.saveDB(d)

        con = sql.connect(self.testDB)
        cur = con.cursor()
        cur.execute("SELECT * FROM song")
        dbSongs = set(cur.fetchall())
        cur.execute("SELECT * FROM tag")
        tags = set(cur.fetchall())
        cur.execute("SELECT * from link")
        links = set(cur.fetchall())
        con.close()
        if path.isfile(self.testDB):
            remove(self.testDB)

        self.assertEquals(dbSongs, {
            (1, '.' + sep, 'sample.mp3'),
            (2, '.' + sep, 'sample2.mp3')
        }, 'DB not saved properly')
        self.assertEquals(tags, {
            (1, 'happy'),
            (2, 'crazy')
        }, 'DB not saved properly')
        self.assertEquals(links, {
            (1, 1),
            (2, 1),
            (2, 2)
        }, 'DB not saved properly')