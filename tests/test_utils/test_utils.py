import os

from UMCommonUtils import FileOperationsHelper as FO

DIR_PATH = os.path.join(os.path.dirname(os.path.dirname((__file__))), 'test_dir')

class UmUnitTestDirLock:
   _current_work_dir = None

   @classmethod
   def _setUpLockedDir(self):
      self._current_work_dir = os.getcwd()
      FO.recreate_dir(DIR_PATH)
      os.chdir(DIR_PATH)

   @classmethod
   def _tearDownLockedDir(self):
      os.chdir(self._current_work_dir)
      FO.remove_dir(DIR_PATH, force=True)

   @classmethod
   def setUpClass(self):
     self._setUpLockedDir()

   @classmethod
   def tearDownClass(self):
      self._tearDownLockedDir()