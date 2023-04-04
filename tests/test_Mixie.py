from unittest import main, TestCase
from Mixie import Mixie
from FileManager import FileManager, BabyFileManager
from Controllers import BaseController, CLIController
import os

class DummyCLIController(CLIController):
    def getLibrary(self) -> str:
        return '.'

class DummyFiler(BabyFileManager):

    def theinit(self, loadDB:dict, filesInLibrary:set):
        self.db = loadDB
        self.files = filesInLibrary

    @staticmethod
    def filerID():
        return 'DummyFiler'

    def loadDB(self) -> dict:
        return self.db
    
    def saveDB(self, tagDict:dict):
        pass
    
    def getFilesInLibrary(self, avoidNonMusic=True) -> set:
        return self.files

FileManager.filers.append(DummyFiler)

class MixieTests(TestCase):
    testDB = 'test_Testdb_095465.db'
    testLib = '.' # TODO: change to nested folder: tests don't affect project, only delete a single folder

    @classmethod
    def tearDownClass(self) -> None:
        if os.path.isfile(self.testDB):
            os.remove(self.testDB)
        return super().tearDown()

    def test_InitSavesSelfInController(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        self.filer.theinit(set(), set())
        self.mixie:Mixie = Mixie(self.controller, self.filer)
        self.assertEqual(self.mixie.fileManager, self.filer, 'Filer instance of Mixie don\'t match global instance')

    def test_InitLoadsDB(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)
        self.assertDictEqual(self.mixie.dbCache, cache, 'Mixie DbCache don\'t match the expected value')
    
    def test_mixAdd(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.mix({'happy',})
        self.assertSetEqual(playlist, files, 'Wrong playlist with add tags alone')
    
    def test_mixAddAndSub(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.mix({'happy',}, {'sad',})
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
        }, 'Wrong Playlist with add and sub tags')
    
    def test_mixAddMultiple(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.mix({'crazy', 'sad'})
        self.assertSetEqual(playlist, {
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        }, 'Wrong Playlist with Multiple add tags')
    
    def test_mixAddMultipleSubtract(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.mix({'crazy', 'sad'}, {'happy'})
        self.assertSetEqual(playlist, set(), 'Wrong playlist with Mulitiple add and a sub tag')
    
    def test_selectSpecific1(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.selectSpecific('sample')
        self.assertSetEqual(playlist, {
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        }, 'Wrong set of songs on playing specific songs')
    
    def test_selectSpecific2(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.selectSpecific('2')
        self.assertSetEqual(playlist, {
            '.%ssample2.mp3'%os.sep,
        }, 'Wrong set of songs on playing specific songs')
    
    def test_findTracks1(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.findTracks('sample')
        self.assertListEqual(playlist, [
            '.%ssample1.mp3'%os.sep,
            '.%ssample2.mp3'%os.sep,
            '.%ssample3.mp3'%os.sep,
        ], 'Wrong playlist when trying to find songs')
    
    def test_findTracks2(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        playlist = self.mixie.findTracks('2')
        self.assertListEqual(playlist, [
            '.%ssample2.mp3'%os.sep,
        ], 'Wrong playlist when trying to find songs')
    
    def test_allTags(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        tags = sorted(['happy', 'crazy', 'sad'])
        self.assertListEqual(tags, self.mixie.allTags(), 'Alltags fetched wrong result')
    
    def test_tagsOfTrack(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        tags = sorted(['happy', 'crazy'])
        self.assertListEqual(tags, self.mixie.tagsOfTrack('.%ssample2.mp3'%os.sep), 'Tags of Track resulted wrong')
    
    def test_scanFindsUntaggedFiles(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample0.mp3']),
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        for x in range(3):
            open('.%ssample%d.mp3'%(os.sep, x), 'w').close()
        untaggedFiles, _ = self.mixie.scan()
        for x in range(3):
            os.remove('.%ssample%d.mp3'%(os.sep, x))
        self.assertListEqual(untaggedFiles, ['.%ssample0.mp3'%os.sep], 'Scan returned wrong result')

    def test_scanFindsBadFiles(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        for x in range(2):
            open('.%ssample%d.mp3'%(os.sep, x+1), 'w').close()
        _, badFiles = self.mixie.scan()
        for x in range(2):
            os.remove('.%ssample%d.mp3'%(os.sep, x+1))
        self.assertListEqual(badFiles, ['.%ssample3.mp3'%os.sep], 'Scan returned wrong result')
    
    def test_tag(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'a',},
            os.sep.join(['.', 'sample2.mp3']): {'a', 'b'},
            os.sep.join(['.', 'sample3.mp3']): {'b', 'c'},
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        self.mixie.tag(os.path.join('.', 'sample2.mp3'), {'x', 'y'})
        self.assertDictEqual(self.mixie.dbCache, {
            os.sep.join(['.', 'sample1.mp3']): {'a',},
            os.sep.join(['.', 'sample2.mp3']): {'x', 'y'},
            os.sep.join(['.', 'sample3.mp3']): {'b', 'c'},
        })
    
    def test_tagKeepOld(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'a',},
            os.sep.join(['.', 'sample2.mp3']): {'a', 'b'},
            os.sep.join(['.', 'sample3.mp3']): {'b', 'c'},
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        self.mixie.tag(os.path.join('.', 'sample2.mp3'), {'x', 'y'}, keepOldTag=True)
        self.assertDictEqual(self.mixie.dbCache, {
            os.sep.join(['.', 'sample1.mp3']): {'a',},
            os.sep.join(['.', 'sample2.mp3']): {'a', 'b', 'x', 'y'},
            os.sep.join(['.', 'sample3.mp3']): {'b', 'c'},
        })

    def test_replaceTrack(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        self.mixie.replaceTrack(os.path.join('.', 'sample2.mp3'), '.%ssample9.mp3'%os.sep)
        self.assertDictEqual(self.mixie.dbCache, {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample9.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        })
    
    def test_forgetTrack(self):
        self.controller:BaseController = DummyCLIController()
        self.filer:DummyFiler = FileManager.getInstance(self.controller, self.testDB, DummyFiler)
        cache, files = {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample2.mp3']): {'happy', 'crazy'},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        }, {
            os.sep.join(['.', 'sample1.mp3']),
            os.sep.join(['.', 'sample2.mp3']),
            os.sep.join(['.', 'sample3.mp3']),
        }
        self.filer.theinit(cache, files)
        self.mixie:Mixie = Mixie(self.controller, self.filer)

        self.mixie.forgetTrack(os.path.join('.', 'sample2.mp3'))
        self.assertDictEqual(self.mixie.dbCache, {
            os.sep.join(['.', 'sample1.mp3']): {'happy',},
            os.sep.join(['.', 'sample3.mp3']): {'happy', 'sad'}
        })

if __name__ == '__main__':
    main()