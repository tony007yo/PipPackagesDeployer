import sys
import re
import os
import argparse
import logging
from subprocess import Popen, TimeoutExpired
from distutils import util

MODULE_NAME             = "UMCommonUtils"
WORK_DIR                = os.path.dirname(os.getcwd())
VERSION_INFO_FILE_PATH  = os.path.join(WORK_DIR, f"{MODULE_NAME}.cfg")
FINAL_VERSION_FILE_PATH = os.path.join(WORK_DIR, "JenkinsTestAndDeployModule", "final_version.cfg")
MAIN_BRANCH             = "master"
LOG_LEVEL               = logging.INFO
DATE_FMT                = '%Y-%m-%d %H:%M:%S'
STANDARD_FMT            = '[%(asctime)s.%(msecs)-3d] %(levelname)-8s [%(name)s:%(lineno)s] %(message)s'

logging.basicConfig(
   level=LOG_LEVEL,
   format=STANDARD_FMT,
   datefmt=DATE_FMT)

logger = logging.getLogger("pip_deploy")


def proccess_communicate(params):
   returncode = 1
   try:
      proc = Popen(params)
      proc.communicate(timeout = 120)
      returncode = proc.returncode
      if returncode != 0:
         logger.error(f"Error returncode {returncode}!")
         exit(returncode)
   except TimeoutExpired as e:
      logger.exception("Timeout Expired!")
      proc.kill()
      proc.communicate()
      exit(returncode)


def change_work_dir():
   logger.info(f"Work dir changed to {WORK_DIR}")
   os.chdir(WORK_DIR)


def __get_version(parsed_version_info):
   version = f"{parsed_version_info['VER_PRODUCTMAJOR']}.{parsed_version_info['VER_PRODUCTMINOR']}"
   if parsed_version_info.get('VER_STAGE'):
      version += f".{parsed_version_info.get('VER_STAGE')}"
   return version


def __from_version_info_to_dict(list_str):
   parsed_version_info = dict()
   for str in list_str:
      parsed = re.search(r"(\D+)=(.+)", str)
      parsed_version_info[parsed.group(1)] = parsed.group(2)

   return parsed_version_info


def __from_dict_to_version_info(dict):
   list_str = list()
   for item in dict.items():
      list_str.append(f"{item[0]}={item[1]}\n")

   return list_str


def get_version_info_from_file():
   try:
      with open(VERSION_INFO_FILE_PATH, "r") as f:
         return __from_version_info_to_dict(f.readlines())
   except Exception:
      logger.exception(f"Failed to load version from {VERSION_INFO_FILE_PATH}!")
      return None


def write_version_info_to_file(version_file: dict):
   try:
      with open(VERSION_INFO_FILE_PATH, "w") as f:
         f.writelines(__from_dict_to_version_info(version_file))
   except Exception:
      logger.exception(f"Failed to write version to {VERSION_INFO_FILE_PATH}!")
      return None


def __update_version_in_version_info(version_info, is_prod):
   if is_prod:
      version_info.pop('VER_STAGE', None)
   else:
      ver_stage = version_info.get('VER_STAGE')
      if ver_stage:
         parsed = re.search(r"(\D+)(\d+)", ver_stage)
         version_info['VER_STAGE'] = f"{parsed.group(1)}{int(parsed.group(2)) + 1}"
      else:
         version_info['VER_PRODUCTMINOR'] = f"{int(version_info['VER_PRODUCTMINOR']) + 1}"
         version_info['VER_STAGE'] = "dev0"

   return version_info


def __update_version(version_info, is_prod = False):
   try:
      new_version_info = __update_version_in_version_info(version_info, is_prod)
      write_version_info_to_file(new_version_info)
      return __get_version(new_version_info)
   except Exception:
      logger.exception(f"Failed to update version!")
      return None


def write_final_version_to_file(version):
   try:
      with open(FINAL_VERSION_FILE_PATH, "w") as f:
         f.write(f"VERSION={MODULE_NAME}-{version}")
      logger.info(f"Final version={version} written to {VERSION_INFO_FILE_PATH}!")
   except Exception:
      logger.exception(f"Failed to write final version to {VERSION_INFO_FILE_PATH}!")
      return None


def release_prod(old_version_info, artifactory_user, artifactory_password):
   logger.info("Releasing prod...")

   new_version = __update_version(old_version_info, True)

   if new_version:
      logger.info(f"New prod version is {new_version}")

      branch_name = f'{MODULE_NAME}-{new_version}'

      proccess_communicate(['git', 'fetch'])

      proccess_communicate(['git', 'checkout', '-b', branch_name])
      logger.info(f"New branch name is {branch_name}!")

      proccess_communicate(['py', 'JenkinsTestAndDeployModule\pip_deploy.py', f'{artifactory_user}', f'{artifactory_password}'])

      proccess_communicate(['git', 'add', f'{MODULE_NAME}.cfg'])

      proccess_communicate(['git', 'commit', '-m', f'First package version is {new_version}!'])

      proccess_communicate(['git', 'push', '-u', 'origin', branch_name])

      proccess_communicate(['git', 'checkout', MAIN_BRANCH])

      tag_name = f"{branch_name}-tag"
      proccess_communicate(['git', 'tag', tag_name])
      proccess_communicate(['git', 'push', 'origin', tag_name])
      logger.info(f"New tag {tag_name} added!")

      write_final_version_to_file(new_version)

      return True
   return False


def release_stage(old_version_info, artifactory_user, artifactory_password, is_part_of_prod):
   if is_part_of_prod:
      logger.info("Releasing stage as part of prod...")
   else:
      logger.info("Releasing stage...")

   new_version = __update_version(old_version_info)

   if new_version:
      logger.info(f"New stage version is {new_version}")

      proccess_communicate(['py', 'JenkinsTestAndDeployModule\pip_deploy.py', f'{artifactory_user}', f'{artifactory_password}'])

      proccess_communicate(['git', 'add', f'{MODULE_NAME}.cfg'])

      proccess_communicate(['git', 'commit', '-m', f'Version updated to {new_version}!'])

      proccess_communicate(['git', 'push', 'origin', f"HEAD:{MAIN_BRANCH}"])

      if not is_part_of_prod:
         write_final_version_to_file(new_version)

      return True
   return False


def prod_stage_release(is_prod, artifactory_user, artifactory_password):
   is_prod = util.strtobool(is_prod)   
   old_version_info = get_version_info_from_file()
   res_prod = True
   if is_prod:
      res_prod = release_prod(old_version_info, artifactory_user, artifactory_password)
   res_stage = release_stage(old_version_info, artifactory_user, artifactory_password, is_prod)

   return res_prod&res_stage


def create_parser():
   parser = argparse.ArgumentParser()
   parser.add_argument('IS_PROD', type = str)
   parser.add_argument('ARTIFACTORY_USER', type = str)
   parser.add_argument('ARTIFACTORY_PASS', type = str)

   return parser


if __name__ == '__main__':
   countArgs = len(sys.argv)

   if (countArgs >= 3):
      parsedArgs = create_parser().parse_args()
      change_work_dir()
      if not prod_stage_release(parsedArgs.IS_PROD, parsedArgs.ARTIFACTORY_USER, parsedArgs.ARTIFACTORY_PASS):
         exit(1)
   else:
      logger.error(f"There are low arguments, expected 3+! Got {countArgs}!")