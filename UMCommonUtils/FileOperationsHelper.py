import fnmatch
import logging
import os
import shutil
import stat
from typing import Iterator

logger = logging.getLogger('unidata.file_oper_helper')

UTF_8 = 'utf-8'


def remove_dir(dir, force=False):
   '''
   Remove directory.
   Also works with ReadOnly attribute if force=True.
   https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
   '''

   try:
      if os.path.exists(dir):
         logger.info(f"Removing directory '{dir}'...")
         shutil.rmtree(dir, onerror=__on_rm_error if force else None)
   except (OSError, shutil.Error):
      logger.exception(f"Failed to remove directory '{dir}'")
      return False
   except Exception:
      logger.exception(f"Unexpected error on remove directory '{dir}'")
      return False

   if os.path.exists(dir):
      # Double check, because some process can use dir (like TGitCache.exe on deleting git repo)
      logger.error(f"Failed to remove directory '{dir}'")
      return False
   return True


def create_file_dir(file_path):
   file_dir = get_file_dir(file_path)
   os.makedirs(file_dir, exist_ok=True)
   return os.path.isdir(file_dir)


def get_file_dir(file_path):
   return os.path.dirname(file_path)


def read_file(file_path, mode='r', encoding=UTF_8):
   try:
      assert "r" in mode
      logger.info(f"Reading file '{file_path}'...")
      with open(file_path, mode=mode, encoding=encoding) as f:
         return f.read()
   except Exception:
      logger.exception(f"Failed to read file '{file_path}'")
      return None


def write_file(file_path, file_content, mode='w', encoding=UTF_8):
   try:
      assert "w" in mode
      logger.info(f"Writiing file '{file_path}'...")
      with open(file_path, mode, encoding=encoding) as f:
         if not f.write(file_content):
            logger.warning(f"Nothing was written to {file_path}!")
      return True
   except Exception:
      logger.exception(f"Failed to write file '{file_path}'")
      return False


def remove_file(file_path):
   try:
      if os.path.exists(file_path):
         logger.info(f"Removing file '{file_path}'...")
         os.remove(file_path)
   except Exception:
      logger.exception(f"Failed to remove file '{file_path}'")
      return False

   if os.path.exists(file_path):
      logger.error(f"Failed to remove file '{file_path}'")
      return False
   return True


def recreate_dir(dir):
   try:
      if not remove_dir(dir, force=True):
         return False
      logger.info(f"Creating directory '{dir}'...")
      os.makedirs(dir)
   except Exception:
      logger.exception(f"Failed to recreate directory '{dir}'")
      return False
   return True


def create_dir(dir):
   try:
      if not os.path.exists(dir):
         logger.info(f"Creating directory '{dir}'...")
         os.makedirs(dir)
   except Exception:
      logger.exception(f"Failed to create directory '{dir}'")
      return False
   return True


def copy_dir(src, dst, recreate=False):
   try:
      if recreate and not remove_dir(dst, force=True):
         return False
      logger.info(f"Copying directory '{src}' to '{dst}'...")
      shutil.copytree(src, dst)
   except (OSError, shutil.Error):
      logger.exception(f"Failed to copy directory '{src}' to '{dst}'")
      return False
   except Exception:
      logger.exception(f"Unexpected error on copy directory '{src}' to '{dst}'")
      return False
   return True


def copy_file(src, dst):
   try:
      dir = dst
      if not os.path.isdir(dir):
         dir = get_file_dir(dir)

      if not os.path.exists(dir):
         os.makedirs(dir)

      logger.info(f"Copying file '{src}' to '{dst}'...")
      shutil.copy(src, dst)
   except (OSError, shutil.Error):
      logger.exception(f"Failed to copy file '{src}' to '{dst}'")
      return False
   except Exception:
      logger.exception(f"Unexpected error on copy file '{src}' to '{dst}'")
      return False
   return True


def move_dir(src, dst):
   try:
      if not remove_dir(dst, force=True):
         return False
      logger.info(f"Moving directory '{src}' to '{dst}'...")
      shutil.move(src, dst)
   except (OSError, shutil.Error):
      logger.exception(f"Failed to move directory '{src}' to '{dst}'")
      return False
   except Exception:
      logger.exception(f"Unexpected error on move file '{src}' to '{dst}'")
      return False
   return True


def get_subdirs_entries(dir) -> Iterator[os.DirEntry]:
   return __get_subdirs_entries(dir)

def get_subdir_names(dir) -> Iterator[str]:
   return [ sub.name for sub in __get_subdirs_entries(dir) ] 

def get_subdirs(dir) -> Iterator[str]:
   """ returns full paths to subdirs """
   return [ sub.path for sub in __get_subdirs_entries(dir) ] 


def get_dir_file_names(dir, mask=None, recursive=True):
   return [ f.name for f in __get_subfiles_entries(dir, mask, recursive) ]


def get_dir_files(dir, mask=None, recursive=True):
   return [ f.path for f in __get_subfiles_entries(dir, mask, recursive) ]


def __get_subdirs_entries(dir) -> Iterator[os.DirEntry]:
   try:
      return [ sub for sub in os.scandir(dir) if sub.is_dir() ] 
   except Exception:
      logger.exception(f"Failed get subdir entries '{dir}'")
   return []


def __get_subfiles_entries(baseDir, mask, recursive) -> Iterator[os.DirEntry]:
   try:
      for entry in os.scandir(baseDir):
         if entry.is_file():
            if mask is None or fnmatch.fnmatch(entry.name, mask):
               yield entry
         elif recursive :
            yield from __get_subfiles_entries(entry, mask, True)
   except Exception:
      logger.exception(f"Failed get subfiles entries '{dir}'")
      return []

def __on_rm_error(func, path, exc_info):
   logger.warning("Triggered rm_error!")
   os.chmod(path, stat.S_IWRITE)
   os.unlink(path)
