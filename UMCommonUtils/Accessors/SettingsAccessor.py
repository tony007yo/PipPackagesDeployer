import jsonmerge
import logging
import os.path as path
import json
import re
import time
from distutils import util

from starlette.config import Config
from functools import lru_cache

MODULES_SETTINGS_PATH = path.abspath(path.join(path.dirname(__file__), 'settings.json'))
SETTINGS_PATHS = [MODULES_SETTINGS_PATH]

CACHE_REFRESH_INTERVAL = 1
CONFIG_PATH = '../.env'

env_config = Config(CONFIG_PATH)

KEY_TAG = 'key'
DEF_TAG = 'def'
ENV_TAG = 'env'

EMPLACED_VARS_TAG = 'emplaced_vars'


logger = logging.getLogger('unidata.settings_accessor')


class RequiredSettingException(Exception):
   def __init__(self, descr, key, env_name):
      self.descr = descr
      self.key = key
      self.env_name = env_name


   def __str__(self):
      return f"Required setting {self.descr} missed!\n" + \
             f"It must be set by env variable '{self.env_name}' on server.\n" + \
             f"It must be set in 'um_settings_dev.json' by key '{self.key}' if local debugging.\n" + \
             f"It must be set in 'um_test_settings.json' by key '{self.key}' on tests running."


def raise_required_setting_exception(descr, key, env_name):
   exc = RequiredSettingException(descr, key, env_name)
   logger.exception(str(exc))
   raise exc


def reload_config(config_path = None):
   global env_config
   global CONFIG_PATH
   if config_path is not None:
      CONFIG_PATH = config_path
   env_config = Config(CONFIG_PATH)


# TO DO: Improve functionality
def get_path(key, default = None, isExist = True, force = False, force_env_value = False):
   filePath = __get_type(str, key, default, force, force_env_value)
   if (path.isabs(filePath) and (not isExist or path.exists(filePath))):
      return path.abspath(filePath)
   else:
      logger.error(f"Path '{filePath}' from '{key}' not correct!")

   return None


def get_str(key, default = None, force = False, force_env_value = False):
   return __get_type(str, key, default, force, force_env_value)


def get_int(key, default = None, force = False, force_env_value = False):
   return __get_type(int, key, default, force, force_env_value)


def get_float(key, default = None, force = False, force_env_value = False):
   return __get_type(float, key, default, force, force_env_value)


def get_bool(key, default = None, force = False, force_env_value = False):
   try:
      boolVal = __get_type(str, key, default, force, force_env_value)

      return bool(util.strtobool(boolVal))
   except Exception:
      logger.error(f"Failed to load settings from '{key}', expected bool, get {boolVal}")
   
   return None


def __get_type(typeOf:type, key, default, force, force_env_value):
   try:
      val = get(key, default, force, force_env_value)

      if (val == '' or val is None):
         return typeOf(default)

      return typeOf(val)
   except Exception:
      logger.error(f"Failed to load settings from '{key}', expected '{typeOf}', get '{val}' as '{type(val)}'")

   return None


def get(key, default = None, force = False, force_env_value = False):
   """ Path - setting node key separated by '|' """
   settings = __load_settings(force)
   node = __find(settings, key)

   if force_env_value or not node:
      env_value = env_config.get(get_auto_env_name(key), default=None)
      if env_value:
         return env_value
      if not node:
         logger.error(f"Node '{key}' doesn't exist")
         return default

   if not DEF_TAG in node:
      logger.error(f"Node '{key}' default value doesn't exist")
      return default

   __apply_config_vars_to_node(node, key, default)
   def_var = node.get(DEF_TAG)
   env_var = node.get(ENV_TAG)
   return env_config.get(env_var, default = def_var) if env_var else def_var


def get_env_name(key, force=False):
   """ Path - setting node key separated by '|' """
   settings = __load_settings(force)
   node = __find(settings, key)
   return None if node is None else node.get(ENV_TAG)


def get_auto_env_name(path:str):
   """ Path - setting node path separated by '|' """
   return path.replace('|', '_')


def reset_settings():
   global SETTINGS_PATHS
   global result

   SETTINGS_PATHS = [MODULES_SETTINGS_PATH]
   result = None

   __load_settings(True)


def append_settings_from_file(filePaths, force=False):
   if (filePaths not in SETTINGS_PATHS):
      SETTINGS_PATHS.append(filePaths)

   if force:
      __load_settings(force)


def is_feature_enabled(feature, default=False):
   val = get('features|' + feature)
   return default if not val else bool(util.strtobool(str(val)))


cache_refresh = 0
last_get_time = 0
def __load_settings(force)->dict:
   global cache_refresh
   global last_get_time

   t = time.time()
   REFRESH_PERIOD = 5
   need_refresh = t - last_get_time > REFRESH_PERIOD

   if need_refresh or force:
      cache_refresh = cache_refresh + 1

   result = __load_cached_settings(cache_refresh, force)
   
   if need_refresh:
      last_get_time = time.time()

   return result


def __load(settingsPath):
   try:
      with open(settingsPath, 'r') as settingsFile:
         return json.load(settingsFile)
   except Exception:
      logger.exception(f"Failed to load settings file '{settingsPath}'")
   return {}


result = None
cur_hash = None
@lru_cache(maxsize=2)
def __load_cached_settings(cacheRefreshVal:int, force)->dict:
   global cur_hash
   global result
   logger.debug(f"Load settings {cacheRefreshVal}")

   new_hash = hash(tuple(SETTINGS_PATHS))
   if (cur_hash != new_hash or force):
      for settingPath in SETTINGS_PATHS:
         if path.exists(settingPath if settingPath else ""):
            result = jsonmerge.merge(result, __load(settingPath))
         else:
            logger.warning(f"Settings path '{settingPath}' is not correct!")
      cur_hash = new_hash

   logger.debug(f"Settings paths list is {SETTINGS_PATHS}")
   logger.debug(f"Full set of settings is {result}")
   return result


def __find(settings, key):
   node = settings
   for key in key.split('|'):
      if not key in node:
         return None
      node = node[key]
   return node


# replaces %VARNAME% to value from env config
def __apply_config_vars_to_node(node:dict, node_path:str, default_val)->None:
   def_val = node.get(DEF_TAG)
   if def_val and isinstance(def_val, str) and len(def_val) > 2:
      var_values = re.findall(r'\%.*?\%', def_val)
      for var_value in var_values:
         real_var_name = var_value[1:-1] # trim %  
         env_val = env_config.get(real_var_name, default = None) 
         if env_val is not None:
            logger.debug(f"Replace in {def_val} with {env_val}")
            node[DEF_TAG] = def_val.replace(var_value, env_val)
         else:
            err = f"Can't find '{real_var_name}' in '.env' file nor environment for {node_path}. Settings are: SETTINGS_PATH='{SETTINGS_PATHS}', MODULES_SETTINGS_PATH='{MODULES_SETTINGS_PATH}'"
            if default_val is not None:
               logger.warning(err)
               return default_val
            exc = KeyError(err)
            logger.exception(str(exc))
            raise exc