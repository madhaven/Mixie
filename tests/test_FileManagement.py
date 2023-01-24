from unittest import main, TestCase, expectedFailure
from FileManager import FileManager
from Mixie import CLIController
import os
import sqlite3 as sql


class DummyController(CLIController):
    def getLibrary(self) -> str:
        return '.'

class InitializationTest(TestCase):
    testDB = 'test_Testdb_09234.db'
    testLib = '.'
    
    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isfile(cls.testDB):
            os.remove(cls.testDB)
        return super().tearDownClass()

    def test_NewMixieCalled(self):
        FileManager.getInstance(DummyController(), self.testDB)
        self.assertTrue(os.path.isfile(self.testDB), 'Was not able to find the DB in the specified location')
    
    def test_CoreTableCreated(self):
        if os.path.isfile(self.testDB):
            os.remove(self.testDB)
        FileManager.getInstance(DummyController(), self.testDB)
        con = sql.connect(self.testDB)
        cur = con.cursor()
        qre = "SELECT * from core"
        cur.execute(qre)
        res = cur.fetchall()
        con.close()

        filer:FileManager = FileManager.latestFiler
        self.assertEquals(res, [
            ('FileManagerStandard', filer.filerID()),
            ('Library', self.testLib)
        ], 'Core Table is not initialized properly')

    def test_NewMixieCalledWithLatestFiler(self):
        FileManager.getInstance(DummyController(), self.testDB)
        latestFiler:FileManager = FileManager.latestFiler

        con = sql.connect(self.testDB)
        cur = con.cursor()
        qre = "SELECT value FROM core WHERE key=?"
        cur.execute(qre, ('FileManagerStandard',))
        filerInDB = cur.fetchone()
        filerInDB = filerInDB[0]
        con.close()

        self.assertEqual(latestFiler.filerID(), filerInDB, "The latest Filer is not saved in the DB")
    
    def test_filesInLibraryFetched(self):
        testFileName = 'testfileName'
        filer = FileManager.getInstance(DummyController(), self.testDB)
        for x in range(3):
            file = open('%s%d.mp3'%(testFileName, x), 'w')
            file.write('test')
            file.close()
        files = filer.getFilesInLibrary()
        files = {file for file in files if testFileName in file}
        for x in range(3):
            os.remove('%s%d.mp3'%(testFileName, x))

        self.assertEquals(files, {'.%s%s%d.mp3'%(os.sep, testFileName, x) for x in range(3)}, 'Files in library not fetched')

    def test_singletonFiler(self):
        instance1 = FileManager.getInstance(DummyController(), self.testDB)
        instance2 = FileManager.getInstance(DummyController(), self.testDB)
        self.assertEqual(instance1, instance2, 'Singleton Filer not working')

    @expectedFailure # cus Python don't assign new mem spaces for the same object ?
    def test_clearingFilerInstance(self):
        instance1 = FileManager.getInstance(DummyController(), self.testDB)
        instance1.clearInstance()
        instance2 = FileManager.getInstance(DummyController(), self.testDB)
        self.assertNotEqual(instance1, instance2, 'Singleton Instance not cleared')

    def test_filerID(self):
        for filer in FileManager.filers:
            self.assertTrue(filer.filerID(), 'FilerID returned wrong')

if __name__ == "__main__":
    main()