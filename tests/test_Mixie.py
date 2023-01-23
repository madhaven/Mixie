from unittest import main, TestCase
from Mixie import Mixie
from FileManager import FileManager
from Controllers import BaseController, CLIController
import os

class DummyCLIController(CLIController):
    def getLibrary(self) -> str:
        return '.'

class MixieTests(TestCase):
    testDB = 'test_Testdb_095465.db'
    testLib = '.'

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
        self.assertEqual(self.mixie.fileManager, self.filer)

    def test_InitLoadsDB(self):
        self.assertDictEqual(self.mixie.dbCache, self.cache)
    
    def test_mixAdd(self):
        playlist = self.mixie.mix({'happy',})
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        })
    
    def test_mixAddAndSub(self):
        playlist = self.mixie.mix({'happy',}, {'sad',})
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
        })
    
    def test_mixAddMultiple(self):
        playlist = self.mixie.mix({'crazy', 'sad'})
        self.assertSetEqual(playlist, {
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        })
    
    def test_mixAddMultipleSubtract(self):
        playlist = self.mixie.mix({'crazy', 'sad'}, {'happy'})
        self.assertSetEqual(playlist, set())