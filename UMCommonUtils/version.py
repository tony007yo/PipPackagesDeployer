import os
import logging

from importlib_metadata import version 


logger = logging.getLogger('unidata.version')


def dist_version(dist_name:str)->str:
   try:
      return version(dist_name)
   except:
      logging.exception("Failed to get module '%s' metadata.", dist_name)
      return 'unknown'


def __build_version(build_file=None):
   fname = os.path.abspath(build_file or 'version.txt')
   try:
      with open(fname, mode='r', encoding='utf-8') as fp:
         return fp.readline()
   except:
      logging.exception("Failed to read build version from file '%s'!", fname)
      return None

def __minor_version():
   full_version = __build_version()
   return '' if full_version is None else full_version.split('.')[-1:][0]


def build_number(build_file=None):
   full_version = __build_version(build_file)
   return 'unknown' if full_version is None else full_version


def build_info(name:str, version:str, dist_names, build_file=None)->dict:
   return {
      'name': name,
      'version': version,
      'build': __minor_version(),
      'modules': dict(map( lambda x: (x, dist_version(x)), dist_names))
   }