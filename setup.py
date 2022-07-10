import re
from setuptools import setup, find_packages

PACKAGE_NAME = "UMCommonUtils"

def __load_long_descr():
   try:
      with open("README.md", "r") as f:
         return f.read()
   except Exception as e:
      print(f"Failed to load 'README.md'! Exception: {e}")
      return None


def __get_version(list_str):
   parsed_version_info = __parse_version_info(list_str)
   version = f"{parsed_version_info['VER_PRODUCTMAJOR']}.{parsed_version_info['VER_PRODUCTMINOR']}"
   if parsed_version_info.get('VER_STAGE'):
      version += f".{parsed_version_info.get('VER_STAGE')}"
   return version


def __parse_version_info(list_str):
   parsed_version_info = dict()
   for str in list_str:
      parsed = re.search(r"(\D+)=(.+)", str)
      parsed_version_info[parsed.group(1)] = parsed.group(2)

   return parsed_version_info


def __load_version():
   try:
      with open(f"{PACKAGE_NAME}.cfg", "r") as f:
         return __get_version(f.readlines())
   except Exception as e:
      print(f"Failed to load version file '{PACKAGE_NAME}.cfg'! Exception: {e}")
      return None

def __parse_requirements(filename):
   lineiter = (line.strip() for line in open(filename))
   return [str(line) for line in lineiter if line and not line.startswith("#")]


setup(
   name=PACKAGE_NAME,
   version=__load_version(),
   author="Anton Kabin",
   author_email="anton.kabin@wartsila.com",
   description="Transas Unidata Manager common utils",
   long_description=__load_long_descr(),
   long_description_content_type="text/markdown",
   url="https://artifactory.transas.com/artifactory/api/pypi/planar-pypi",
   py_modules=[PACKAGE_NAME],
   packages=find_packages(exclude=['tests']),
   test_suite='pytest',
   install_requires=__parse_requirements('requirements.txt'),
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
   zip_safe=False,
   package_data = {PACKAGE_NAME: [ 'Accessors/*', 'TileLoader/*']},
   python_requires=">=3.6"
)
