import os
import pytest

from unittest import TestCase

from . import UmUnitTestDirLock, DIR_PATH
from UMCommonUtils import FileOperationsHelper as FO


@pytest.mark.unit
class FileOperationHelperTests(UmUnitTestDirLock, TestCase):
    dir_path = os.path.join(DIR_PATH, "dir")

    def test_remove_dir(self):
        FO.create_dir(self.dir_path)

        def remove_dir(correct):
            self.assertEqual(FO.remove_dir(self.dir_path), correct)
            self.assertEqual(os.path.exists(self.dir_path), not correct)

        cur_dir = os.getcwd()
        os.chdir(self.dir_path)
        remove_dir(False)
        os.chdir(cur_dir)

        remove_dir(True)


    def test_create_file_dir(self):
        file_dir_path_сorrect = os.path.join(self.dir_path, "filename.test1")

        self.assertTrue(FO.create_file_dir(file_dir_path_сorrect))
        self.assertTrue(os.path.exists(self.dir_path))


    def test_get_file_dir(self):
        file_dir_correct = FO.get_file_dir("C:\\TestDir\\test.py")
        self.assertEqual(file_dir_correct, "C:\\TestDir")

        file_dir_incorrect = FO.get_file_dir("test.py")
        self.assertEqual(file_dir_incorrect, "")


    def test_read_file(self):
        text_for_check = "Text for check"
        file_path = os.path.join(DIR_PATH, "filename.test1")

        FO.write_file(file_path, text_for_check)
        self.assertEqual(FO.read_file(file_path), text_for_check)


    def test_write_file(self):
        text_for_check = "text_for_check"
        incorrect_text_for_check = b'\xff'
        file_path_сorrect = os.path.join(DIR_PATH, "filename.test1")

        self.assertTrue(FO.write_file(file_path_сorrect, text_for_check))
        self.assertEqual(FO.read_file(file_path_сorrect), text_for_check)

        self.assertFalse(FO.write_file(file_path_сorrect, incorrect_text_for_check))


    def test_remove_file(self):
        file_path = os.path.join(DIR_PATH, "filename.test1")

        FO.write_file(file_path, "text")
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(FO.remove_file(file_path))
        self.assertFalse(os.path.exists(file_path))


    def test_recreate_dir(self):
        long_dir_path = os.path.join(self.dir_path, "second_dir")

        FO.create_dir(long_dir_path)
        self.assertTrue(os.path.exists(long_dir_path))
        self.assertTrue(FO.recreate_dir(self.dir_path))
        self.assertFalse(os.path.exists(long_dir_path))


    def test_create_dir(self):
        test_dir_path = os.path.join(self.dir_path, "test_dir_path")
        self.assertFalse(os.path.exists(test_dir_path))
        FO.create_dir(test_dir_path)
        self.assertTrue(os.path.exists(test_dir_path))


    def test_copy_dir(self):
        src_dir_path = os.path.join(self.dir_path, "src_dir")
        dst_dir_path = os.path.join(self.dir_path, "dst_dir")
        part_of_dst_path = os.path.join(dst_dir_path, "src_dir")

        FO.create_dir(src_dir_path)
        self.assertTrue(os.path.exists(src_dir_path))

        self.assertTrue(FO.copy_dir(self.dir_path, dst_dir_path))
        self.assertTrue(os.path.exists(dst_dir_path))
        self.assertTrue(os.path.exists(part_of_dst_path))


    def test_copy_file(self):
        text_for_check = "text_for_check"
        file_path_src = os.path.join(DIR_PATH, "filename.test1")
        file_path_dst = os.path.join(self.dir_path, "filename.test2")

        FO.write_file(file_path_src, text_for_check)
        self.assertTrue(os.path.exists(file_path_src))

        self.assertTrue(FO.copy_file(file_path_src, file_path_dst))
        self.assertTrue(os.path.exists(file_path_dst))
        self.assertEqual(FO.read_file(file_path_dst), text_for_check)


    def test_move_dir(self):
        src_dir_path = os.path.join(self.dir_path, "src_dir")
        dst_dir_path = os.path.join(self.dir_path, "dst_dir_test")
        part_of_src_dir_path = os.path.join(src_dir_path, "part_dst_dir")

        FO.create_dir(part_of_src_dir_path)
        self.assertTrue(os.path.exists(part_of_src_dir_path))

        def move_dir(correct):
            self.assertEqual(FO.move_dir(part_of_src_dir_path, dst_dir_path), correct)
            self.assertEqual(os.path.exists(part_of_src_dir_path), not correct)

        cur_dir = os.getcwd()
        os.chdir(part_of_src_dir_path)
        move_dir(False)
        os.chdir(cur_dir)

        move_dir(True)


@pytest.mark.unit
class FileOperationSubdirTests(UmUnitTestDirLock, TestCase):
    dir_path = os.path.join(DIR_PATH, "dir")
    dir_pathes_list = None
    files_pathes_list = None


    def setUp(self):
        self.dir_pathes_list = []
        self.files_pathes_list = []

        for i in range(0,5):
            new_parent_dir = os.path.join(self.dir_path, f"parent_dir{i}")
            FO.create_dir(new_parent_dir)
            self.dir_pathes_list.append(new_parent_dir)

            for j in range(i, 4):
                new_child_dir = os.path.join(new_parent_dir, f"child_dir_file{i}{j}.test")
                FO.write_file(new_child_dir, new_child_dir)
                self.files_pathes_list.append(new_child_dir)


    def tearDown(self):
        self.dir_pathes_list = None
        self.files_pathes_list = None


    def test_get_subdirs_entries(self):
        subdirs_entries = FO.get_subdirs_entries(self.dir_path)

        self.assertEqual(len(subdirs_entries), 5)
        self.assertEqual([ os.path.basename(dir) for dir in self.dir_pathes_list ], [ dir.name for dir in subdirs_entries ])
        self.assertEqual(self.dir_pathes_list, [ dir.path for dir in subdirs_entries ])


    def test_get_subdir_names(self):
        subdir_names = FO.get_subdir_names(self.dir_path)

        self.assertEqual(len(subdir_names), 5)
        self.assertEqual([ os.path.basename(dir) for dir in self.dir_pathes_list ], subdir_names)


    def test_get_subdirs(self):
        subdirs = FO.get_subdirs(self.dir_path)

        self.assertEqual(len(subdirs), 5)
        self.assertEqual(self.dir_pathes_list, subdirs)


    def test_get_dir_file_names(self):
        dir_file_names = FO.get_dir_file_names(self.dir_path)

        self.assertEqual(len(dir_file_names), 10)
        self.assertEqual([ os.path.basename(dir) for dir in self.files_pathes_list ], dir_file_names)


    def test_get_dir_files(self):
        dir_files = FO.get_dir_files(self.dir_path)

        self.assertEqual(len(dir_files), 10)
        self.assertEqual(self.files_pathes_list, dir_files)