import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_DIR / "app.py"


def load_app_module():
    spec = importlib.util.spec_from_file_location("file_reviewer_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.app = load_app_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tempdir.name)
        self.app.DEFAULT_APP_DIR = self.tmp / "default"
        self.app.PROFILE_POINTER_PATH = self.app.DEFAULT_APP_DIR / "profile_location.json"
        self.app.set_app_dir(self.tmp / "data")
        self.app.ensure_app_dirs()
        self.app.save_config(self.app.DEFAULT_CONFIG)
        self.app.init_db()

    def tearDown(self):
        try:
            self.tempdir.cleanup()
        except OSError:
            shutil.rmtree(self.app.fs_path(self.tmp), ignore_errors=True)

    def test_config_roundtrip(self):
        config = self.app.load_config()
        config["scheduler"]["algorithm"] = "SM-2"
        self.app.save_config(config)
        loaded = self.app.load_config()
        self.assertEqual(loaded["scheduler"]["algorithm"], "SM-2")
        self.assertTrue(self.app.CONFIG_PATH.exists())

    def test_legacy_config_disables_external_auto_open(self):
        legacy = self.app.load_config()
        legacy["version"] = "2.3.0"
        legacy["review"]["auto_open_file"] = True
        self.app.CONFIG_PATH.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")
        loaded = self.app.load_config()
        self.assertFalse(loaded["review"]["auto_open_file"])
        self.assertEqual(loaded["version"], self.app.APP_VERSION)

    def test_scan_library_adds_supported_files(self):
        library = self.tmp / "library"
        library.mkdir()
        (library / "note.md").write_text("# note", encoding="utf-8")
        (library / "ignore.tmp").write_text("tmp", encoding="utf-8")
        result = self.app.scan_library(str(library), self.app.load_config())
        self.assertEqual(result["added"], 1)
        overview = self.app.get_overview()
        self.assertEqual(overview["stats"]["total"], 1)
        self.assertEqual(overview["due_items"][0]["file_name"], "note.md")

    def test_review_flow_updates_schedule_and_history(self):
        library = self.tmp / "library"
        library.mkdir()
        (library / "note.md").write_text("# note", encoding="utf-8")
        self.app.scan_library(str(library), self.app.load_config())
        opened = []
        self.app.open_path = lambda path: opened.append(path)
        started = self.app.start_review()
        self.assertIsNotNone(started["item"])
        self.assertEqual(opened, [])
        result = self.app.finish_review(
            {
                "item_id": started["item"]["id"],
                "session_id": started["session_id"],
                "rating": 2,
                "duration_seconds": 9,
            }
        )
        self.assertGreater(result["item"]["review_count"], 0)
        with self.app.get_conn() as conn:
            history_count = conn.execute("SELECT COUNT(*) AS c FROM review_history").fetchone()["c"]
        self.assertEqual(history_count, 1)

    def test_backup_database(self):
        self.app.backup_database()
        backups = list(self.app.BACKUP_DIR.glob("*.sqlite"))
        self.assertEqual(len(backups), 1)

    def test_backup_database_to_custom_export_dir(self):
        export_dir = self.tmp / "custom-exports"
        result = self.app.backup_database(export_dir)
        self.assertTrue(Path(result["backup_path"]).exists())
        self.assertEqual(Path(result["backup_path"]).parent, export_dir.resolve())

    def test_schema_version_and_migration_record(self):
        with self.app.get_conn() as conn:
            self.assertEqual(self.app.db_user_version(conn), self.app.SCHEMA_VERSION)
            count = conn.execute("SELECT COUNT(*) AS c FROM schema_migrations").fetchone()["c"]
        self.assertGreaterEqual(count, 1)

    def test_health_check_and_portable_export(self):
        library = self.tmp / "library"
        library.mkdir()
        (library / "note.md").write_text("# note", encoding="utf-8")
        self.app.scan_library(str(library), self.app.load_config())
        health = self.app.health_check()
        self.assertTrue(health["ok"])
        self.assertTrue((self.app.APP_DIR / "last_health_check.json").exists())
        exported = self.app.export_portable_json()
        self.assertTrue(exported.exists())
        payload = json.loads(exported.read_text(encoding="utf-8"))
        self.assertEqual(payload["format"], "LiFileReviewerPortable")
        self.assertEqual(len(payload["items"]), 1)

    def test_exports_use_custom_target_dir(self):
        export_dir = self.tmp / "exports"
        csv_path = self.app.export_csv(export_dir)
        json_path = self.app.export_portable_json(export_dir)
        profile_path = self.app.export_profile_package(export_dir)
        self.assertTrue(csv_path.exists())
        self.assertTrue(json_path.exists())
        self.assertTrue(profile_path.exists())
        self.assertEqual(csv_path.parent, export_dir.resolve())
        self.assertEqual(json_path.parent, export_dir.resolve())
        self.assertEqual(profile_path.parent, export_dir.resolve())

    def test_choose_folder_dialog_uses_webview_folder_dialog(self):
        class FakeWindow:
            def __init__(self):
                self.dialog_type = None

            def create_file_dialog(self, dialog_type=None, directory="", allow_multiple=False, **kwargs):
                self.dialog_type = dialog_type
                self.directory = directory
                self.allow_multiple = allow_multiple
                return [str(self.tmp_path)]

        fake = FakeWindow()
        fake.tmp_path = self.tmp / "library"
        fake.tmp_path.mkdir()
        self.app.WEBVIEW_WINDOW = fake
        selected = self.app.choose_folder_dialog()
        import webview

        self.assertEqual(Path(selected), fake.tmp_path)
        self.assertEqual(fake.dialog_type, webview.FileDialog.FOLDER)
        self.assertFalse(fake.allow_multiple)

    def test_profile_package_and_move_profile(self):
        library = self.tmp / "library"
        library.mkdir()
        (library / "note.md").write_text("# note", encoding="utf-8")
        self.app.scan_library(str(library), self.app.load_config())
        package = self.app.export_profile_package()
        self.assertTrue(package.exists())
        moved_dir = self.tmp / "moved-profile"
        result = self.app.move_profile_dir(str(moved_dir))
        self.assertTrue(result["moved"])
        self.assertEqual(Path(result["app"]["app_dir"]), moved_dir.resolve())
        self.assertTrue((moved_dir / "config.json").exists())
        self.assertTrue((moved_dir / "review_data.sqlite").exists())
        self.assertTrue(self.app.PROFILE_POINTER_PATH.exists())
        import_package = moved_dir / "exports" / package.name
        imported = self.app.import_profile_package(str(import_package))
        self.assertTrue(Path(imported["backup_before_import"]).exists())

    def test_move_profile_to_non_empty_parent_creates_dedicated_subdir(self):
        target_parent = self.tmp / "chosen-folder"
        target_parent.mkdir()
        (target_parent / "keep.txt").write_text("user file", encoding="utf-8")
        result = self.app.move_profile_dir(str(target_parent))
        expected = target_parent / "LiFileReviewer2"
        self.assertTrue(result["moved"])
        self.assertEqual(Path(result["app"]["app_dir"]), expected.resolve())
        self.assertTrue((expected / "config.json").exists())
        self.assertTrue((expected / "review_data.sqlite").exists())
        self.assertTrue((target_parent / "keep.txt").exists())

    def test_plugins_directory_listing(self):
        plugin = self.app.PLUGINS_DIR / "sample"
        plugin.mkdir(parents=True)
        (plugin / "plugin.json").write_text(
            json.dumps({"id": "sample", "name": "Sample Plugin", "version": "0.1.0"}),
            encoding="utf-8",
        )
        result = self.app.list_plugins()
        self.assertEqual(result["plugins"][0]["name"], "Sample Plugin")

    def test_markdown_notes_are_real_files_and_saved(self):
        library = self.tmp / "library"
        library.mkdir()
        (library / "source.md").write_text("# source", encoding="utf-8")
        self.app.scan_library(str(library), self.app.load_config())
        started = self.app.start_review()
        created = self.app.create_note({"item_id": started["item"]["id"], "title": "复习笔记"})
        note_path = Path(created["note"]["file_path"])
        self.assertTrue(note_path.exists())
        self.assertEqual(note_path.suffix, ".md")
        saved = self.app.save_note({"id": created["note"]["id"], "title": "更新笔记", "content": "# updated"})
        self.assertEqual(note_path.read_text(encoding="utf-8"), "# updated")
        self.assertEqual(saved["note"]["title"], "更新笔记")
        notes = self.app.list_notes(started["item"]["id"])
        self.assertEqual(len(notes["notes"]), 1)

    def test_linked_note_works_with_deep_profile_and_long_file_name(self):
        deep_profile = self.tmp / ("deep_" + "x" * 40) / ("profile_" + "y" * 40)
        self.app.set_app_dir(deep_profile)
        self.app.ensure_app_dirs()
        self.app.save_config(self.app.DEFAULT_CONFIG)
        self.app.init_db()
        library = self.tmp / ("library_" + "z" * 40)
        library.mkdir(parents=True)
        long_name = "20250915_REF5_How I Study Consistently While Working a 9-5 Full-Time Job " + ("very long " * 8) + ".pdf"
        source = library / long_name
        source.write_text("pdf placeholder", encoding="utf-8")
        self.app.scan_library(str(library), self.app.load_config())
        started = self.app.start_review()
        created = self.app.create_note({"item_id": started["item"]["id"], "title": f"{started['item']['file_name']} 复习笔记"})
        note_path = Path(created["note"]["file_path"])
        self.assertTrue(self.app.path_exists(note_path))
        self.assertIn("复习笔记", self.app.read_note(created["note"]["id"])["note"]["content"])
        self.assertIn("复习笔记", created["note"]["title"])

    def test_notes_can_be_exported_and_deleted_in_batches(self):
        first = self.app.create_note({"title": "第一篇", "content": "# one"})["note"]
        second = self.app.create_note({"title": "第二篇", "content": "# two"})["note"]
        export_dir = self.tmp / "note-exports"
        exported = self.app.export_notes({"ids": [first["id"], second["id"]], "target_dir": str(export_dir)})
        self.assertEqual(exported["exported"], 2)
        self.assertTrue((export_dir / "第一篇.md").exists())
        self.assertTrue((export_dir / "第二篇.md").exists())
        deleted = self.app.delete_notes({"ids": [first["id"], second["id"]], "delete_files": True})
        self.assertEqual(deleted["deleted"], 2)
        self.assertFalse(Path(first["file_path"]).exists())
        self.assertFalse(Path(second["file_path"]).exists())
        self.assertEqual(len(self.app.list_notes()["notes"]), 0)

    def test_profile_package_contains_notes_folder(self):
        created = self.app.create_note({"title": "迁移笔记", "content": "# portable"})
        package = self.app.export_profile_package()
        import zipfile

        with zipfile.ZipFile(package, "r") as archive:
            names = archive.namelist()
        self.assertIn("notes/迁移笔记.md", names)

    def test_import_profile_package_repairs_note_paths(self):
        created = self.app.create_note({"title": "导入笔记", "content": "# portable"})["note"]
        package = self.app.export_profile_package()
        destination = self.tmp / "fresh-profile"
        self.app.set_app_dir(destination)
        self.app.ensure_app_dirs()
        self.app.init_db()
        imported = self.app.import_profile_package(str(package))
        self.assertTrue(Path(imported["backup_before_import"]).exists())
        notes = self.app.list_notes()["notes"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(Path(notes[0]["file_path"]).parent, self.app.DEFAULT_NOTES_DIR)
        self.assertTrue(Path(notes[0]["file_path"]).exists())
        self.assertNotEqual(Path(notes[0]["file_path"]), Path(created["file_path"]))


if __name__ == "__main__":
    unittest.main()
