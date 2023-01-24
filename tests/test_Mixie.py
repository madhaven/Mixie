from unittest import main, TestCase
from Mixie import Mixie
from FileManager import FileManager, BabyFileManager
from Controllers import BaseController, CLIController
import os

class DummyCLIController(CLIController):
    def getLibrary(self) -> str:
        return '.'

class MixieTests(TestCase):
    testDB = 'test_Testdb_095465.db'
    testLib = '.' # TODO: change to nested folder: tests don't affect project, only delete a single folder

    def setUp(self) -> None:
        self.controller:BaseController = DummyCLIController() # TODO remove db logic in mixie tests
        self.filer:FileManager = FileManager.getInstance(self.controller, self.testDB)
        self.cache = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }
        self.filer.saveDB(self.cache)
        self.mixie:Mixie = Mixie(self.filer)
        return super().setUp()
    
    def tearDown(self) -> None:
        self.filer.clearInstance()
        return super().tearDown()

    @classmethod
    def tearDownClass(self) -> None:
        if os.path.isfile(self.testDB):
            os.remove(self.testDB)
        return super().tearDown()

    def test_InitSavesSelfInController(self):
        self.assertEqual(self.mixie.fileManager, self.filer, 'Filer instance of Mixie don\'t match global instance')

    def test_InitLoadsDB(self):
        self.assertDictEqual(self.mixie.dbCache, self.cache, 'Mixie DbCache don\'t match the expected value')
    
    def test_mixAdd(self):
        playlist = self.mixie.mix({'happy',})
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        }, 'Wrong playlist with add tags alone')
    
    def test_mixAddAndSub(self):
        playlist = self.mixie.mix({'happy',}, {'sad',})
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
        }, 'Wrong Playlist with add and sub tags')
    
    def test_mixAddMultiple(self):
        playlist = self.mixie.mix({'crazy', 'sad'})
        self.assertSetEqual(playlist, {
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        }, 'Wrong Playlist with Multiple add tags')
    
    def test_mixAddMultipleSubtract(self):
        playlist = self.mixie.mix({'crazy', 'sad'}, {'happy'})
        self.assertSetEqual(playlist, set(), 'Wrong playlist with Mulitiple add and a sub tag')
    
    def test_selectSpecific1(self):
        playlist = self.mixie.selectSpecific('sample')
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        }, 'Wrong set of songs on playing specific songs')
    
    def test_selectSpecific2(self):
        playlist = self.mixie.selectSpecific('2')
        self.assertSetEqual(playlist, {
            '.%ssample2.mp3'%os.sep,
        }, 'Wrong set of songs on playing specific songs')
    
    def test_findTracks1(self):
        playlist = self.mixie.findTracks('sample')
        self.assertListEqual(playlist, [
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        ], 'Wrong playlist when trying to find songs')
    
    def test_findTracks2(self):
        playlist = self.mixie.findTracks('2')
        self.assertListEqual(playlist, [
            '.%ssample2.mp3'%os.sep,
        ], 'Wrong playlist when trying to find songs')
    
    def test_allTags(self):
        tags = sorted(['happy', 'crazy', 'sad'])
        self.assertListEqual(tags, self.mixie.allTags(), 'Alltags fetched wrong result')
    
    def test_tagsOfTrack(self):
        tags = sorted(['happy', 'crazy'])
        self.assertListEqual(tags, self.mixie.tagsOfTrack('.%ssample2.mp3'%os.sep), 'Tags of Track resulted wrong')
    
    def test_scanFindsUntaggedFiles(self):
        for x in range(3):
            open('.%ssample%d.mp3'%(os.sep, x), 'w').close()
        untaggedFiles, _ = self.mixie.scan()
        for x in range(3):
            os.remove('.%ssample%d.mp3'%(os.sep, x))
        self.assertListEqual(untaggedFiles, ['.%ssample0.mp3'%os.sep], 'Scan returned wrong result')

    def test_scanFindsBadFiles(self):
        for x in range(3):
            open('.%ssample%d.mp3'%(os.sep, x), 'w').close()
        _, badFiles = self.mixie.scan()
        for x in range(3):
            os.remove('.%ssample%d.mp3'%(os.sep, x))
        self.assertListEqual(badFiles, ['.%ssample3.mp3'%os.sep], 'Scan returned wrong result')