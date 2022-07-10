import os
import sys
import logging
# Disabled, before init
logging.disable()

from concurrent_log_handler import ConcurrentRotatingFileHandler

from UMCommonUtils import SettingsAccessor

LOG_LEVEL         = SettingsAccessor.get('LOG_LEVEL', 'INFO')
UNIDATA_LOG_LEVEL = SettingsAccessor.get('UNIDATA_LOG_LEVEL', LOG_LEVEL)
LOG_FILE_PATH     = SettingsAccessor.get('UNIDATA_LOG_FILE_PATH', None)
LOG_FILE_SIZE     = SettingsAccessor.get_int('UNIDATA_LOG_FILE_SIZE', 10)

STANDARD_FMT  = '[%(asctime)s.%(msecs)-3d] %(levelname)-8s [%(name)s:%(lineno)s] %(message)s'
DATE_FMT      = '%Y-%m-%d %H:%M:%S'


standard_formatter = logging.Formatter(STANDARD_FMT, DATE_FMT)


def configHandlers(level = LOG_LEVEL, formatter = standard_formatter):
   return filter(None, 
      [__configConsoleHandler(level, formatter),
       __configFileHandler(level, formatter),
       __configAzureHandler(level)])


def config_unidata_loggers(level = LOG_LEVEL):
   __config_root_logger("unidata", level)


def __config_root_logger(root_name, level):
   root_logger = logging.getLogger(root_name)
   root_logger.handlers = configHandlers(level)
   root_logger.parent.setLevel(level)


def __configConsoleHandler(level, formatter = standard_formatter):
   stdout_handler = logging.StreamHandler(sys.stdout)
   stdout_handler.setFormatter(formatter)
   stdout_handler.setLevel(level)
   return stdout_handler


def __configFileHandler(level, formatter = standard_formatter):
   if not LOG_FILE_PATH: return None
   try:
      file_handler = ConcurrentRotatingFileHandler(LOG_FILE_PATH, 'a', 1024*1024*LOG_FILE_SIZE, 5)
      file_handler.setFormatter(formatter)
      file_handler.setLevel(level)
      return file_handler
   except Exception:
      return None


def __configAzureHandler(level, formatter = logging.Formatter('%(levelname)s [%(name)s:%(lineno)s] %(message)s', DATE_FMT)):
   try:
      from opencensus.ext.azure.log_exporter import AzureLogHandler
        
      opencensus_key = os.environ.get('OPENCENSUS_KEY', None)
      if opencensus_key:
         azure_handler = AzureLogHandler(connection_string=f'InstrumentationKey={opencensus_key}')
         azure_handler.setFormatter(formatter)
         azure_handler.setLevel(level)
         return azure_handler
   except ImportError:
      return None


def initBasicConfig():
   # Logging enabling
   logging.disable(logging.NOTSET)
   logging.basicConfig(level=LOG_LEVEL, handlers=configHandlers())
   config_unidata_loggers(UNIDATA_LOG_LEVEL)