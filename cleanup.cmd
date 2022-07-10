@echo off
python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
rmdir env /s /q
rmdir build /s /q
rmdir dist /s /q
for /d %%G in ("*.egg-info") do rmdir "%%~G" /s /q
rmdir .pytest_cache /s /q
del /f /q *.log