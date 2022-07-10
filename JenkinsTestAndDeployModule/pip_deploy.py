import sys
import re
import os
import argparse
import logging
from subprocess import Popen, TimeoutExpired
from pathlib import Path

ARTIFACTORY_URL   = ""
WORK_DIR          = os.path.dirname(os.getcwd())
MODULE_NAME       = "UMCommonUtils"
LOG_LEVEL         = logging.INFO
DATE_FMT          = '%Y-%m-%d %H:%M:%S'
STANDARD_FMT      = '[%(asctime)s.%(msecs)-3d] %(levelname)-8s [%(name)s:%(lineno)s] %(message)s'

logging.basicConfig(
   level=LOG_LEVEL,
   format=STANDARD_FMT,
   datefmt=DATE_FMT)

logger = logging.getLogger("pip_deploy")


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
   if "JenkinsTestAndDeployModule" in WORK_DIR:
      logger.info(f"Work dir changed to {WORK_DIR}")
      os.chdir(WORK_DIR)


def deploy(artifactoryUser, artifactoryPass):
   logger.info(f"Building {MODULE_NAME}...")

   proccess_communicate(['py', '-m', 'pip', 'install', '--upgrade', 'pip'])
   proccess_communicate(['py', '-m', 'pip', 'install', '--upgrade', 'setuptools', 'wheel', 'twine'])
   proccess_communicate(['py', 'setup.py', 'sdist', 'bdist_wheel'])

   logger.info(f"Deploying {MODULE_NAME}...")

   cmd = f"py -m twine upload --username {artifactoryUser} --password {artifactoryPass} --repository-url {ARTIFACTORY_URL} dist/*"
   proccess_communicate(cmd)


def create_parser():
   parser = argparse.ArgumentParser()
   parser.add_argument('ARTIFACTORY_USER', type = str)
   parser.add_argument('ARTIFACTORY_PASS', type = str)
   
   return parser


if __name__ == '__main__':
   countArgs = len(sys.argv)

   if (countArgs >= 2):
      parsedArgs = create_parser().parse_args()
      change_work_dir()
      deploy(parsedArgs.ARTIFACTORY_USER, parsedArgs.ARTIFACTORY_PASS)
   else:
      logger.error(f"There are low arguments, expected 2+! Got {countArgs}!")