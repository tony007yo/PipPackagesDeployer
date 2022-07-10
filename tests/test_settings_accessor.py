import UMCommonUtils.Accessors.SettingsAccessor as SettingsAccessor
from unittest import TestCase
import pytest
import os
from . import TEST_DATA

TEST_DATA_PATH = os.path.join(TEST_DATA, "SettingsAccessor")

@pytest.mark.unit
class SettingsAcccesorTest(TestCase):
   def setUp(self):
      SettingsAccessor.reset_settings()


   def test_for_single_setting(self):
      self.assertEqual(SettingsAccessor.get('git_repo|def_branch'), 'master')


   def test_get_path(self):
      self.assertEqual(SettingsAccessor.get_path('deploy|exe', isExist = False), "C:\\Program Files (x86)\\IIS\Microsoft Web Deploy V3\\msdeploy.exe")
      self.assertIsNone(SettingsAccessor.get_path('git_repo|def_branch', isExist = False))


   def test_get_str(self):
      self.assertEqual(SettingsAccessor.get_str('git_repo|def_branch'), 'master')
      self.assertEqual(SettingsAccessor.get_str('chart_meta|max_lod'), '6')

      self.assertEqual(SettingsAccessor.get_str('wms_cache|root', default = "test"), "test")


   def test_get_int(self):
      self.assertEqual(SettingsAccessor.get_int('chart_meta|max_lod'), 6)
      self.assertEqual(SettingsAccessor.get_int('bathymetry_cache|cache_folder_ttl'), 259200)

      self.assertIsNone(SettingsAccessor.get_int('git_repo|def_branch'))
      self.assertEqual(SettingsAccessor.get_int('wms_cache|root', default = 1), 1)


   def test_for_more_settings(self):
      self.assertEqual(SettingsAccessor.get('git_repo|def_branch'), 'master')

      SettingsAccessor.reload_config(os.path.join(TEST_DATA_PATH,  ".env"))
      SettingsAccessor.append_settings_from_file(os.path.join(TEST_DATA_PATH,  "um_test_settings.json"), force=True)

      self.assertEqual(SettingsAccessor.get('git_repo|def_branch'), 'master')
      self.assertEqual(os.path.abspath(SettingsAccessor.get('git_repo|root')), "C:\\JOB\\UnidataManager\\test_temp\\GitRepo")


   def test_get_env_val(self):
      SettingsAccessor.reload_config(os.path.join(TEST_DATA_PATH,  ".env"))
      SettingsAccessor.append_settings_from_file(os.path.join(TEST_DATA_PATH,  "um_test_settings.json"), force=True)

      self.assertEqual(SettingsAccessor.get("TEST_CONFIG|VAL"), "Test")


   def test_get_env_val_from_env(self):
      os.environ["TEST_CONFIG_VAL"] = "test1"
      self.assertEqual(SettingsAccessor.get("TEST_CONFIG|VAL"), "test1")