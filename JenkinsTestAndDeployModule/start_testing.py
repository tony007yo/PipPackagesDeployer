import logging
import os
from subprocess import Popen, TimeoutExpired

CUR_DIR           = os.getcwd()
REQUIREMENTS_FILE = "requirements.txt"
MODULE_NAME       = "UMCommonUtils"
LOG_LEVEL         = logging.INFO
DATE_FMT          = '%Y-%m-%d %H:%M:%S'
STANDARD_FMT      = '[%(asctime)s.%(msecs)-3d] %(levelname)-8s [%(name)s:%(lineno)s] %(message)s'

logging.basicConfig(
   level=LOG_LEVEL,
   format=STANDARD_FMT,
   datefmt=DATE_FMT)

logger = logging.getLogger("upload_req_and_testing")


def proccess_communicate(params):
   returncode = 1
   try:
      proc = Popen(params)
      proc.communicate(timeout = 60)
      returncode = proc.returncode
      if returncode != 0:
         logger.error(f"Error returncode {returncode}!")
         exit(returncode)
   except TimeoutExpired as e:
      logger.exception(f"Timeout Expired!")
      proc.kill()
      proc.communicate()
      exit(returncode)
      

def change_work_dir():
   logger.info(f"Work dir changed to {CUR_DIR}")
   os.chdir(os.path.dirname(CUR_DIR))

   
def upload_requirements():
   logger.info(f"Upload requirements from {REQUIREMENTS_FILE} for {MODULE_NAME}...")

   proccess_communicate(['py', '-m', 'pip', 'install', '--upgrade', '--force-reinstall','-r', REQUIREMENTS_FILE])


def start_test():
   logger.info(f"Testing {MODULE_NAME}...")
   proccess_communicate(['py', '-m', 'pytest', '-s', '-v'])


if __name__ == '__main__':
   change_work_dir()
   upload_requirements()
   start_test()