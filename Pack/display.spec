# -*- mode: python ; coding: utf-8 -*-

# 排除標準庫和第三方庫
excludes = [
    # 標準庫，常見的測試和文檔相關功能
    'unittest', 'pydoc', 'doctest', 'test', 'pydoc_data', 'lib2to3', 'argparse', 'pickle',
    'calendar', 'pytz', 'pdb', 'sqlite3', 'distutils', 'setuptools', 'pip', '_distutils_hack',
    'pkg_resources.py2_warn', 'lib2to3', '_pytest', 'pytest',
    # 網絡和文件處理相關庫
    'email', 'html', 'http', 'urllib.request', 'xml', 'ftplib', 'smtplib', 'telnetlib',
    # 更多不需要的標準庫
    'asyncio', 'concurrent', 'curses', 'dbm', 'ensurepip', 'idlelib', 'multiprocessing',
    'turtledemo', 'venv', 'zipapp', 'webbrowser',
    # PyInstaller 相關工具和包
    'altgraph', 'pyinstaller_hooks_contrib', '_pyinstaller_hooks_contrib', 
    'pyinstaller_hooks_contrib',
    # 其他可能包含但不需要的第三方庫
    'win32ctypes', 'packaging', 'pefile',
]

# 排除二進制包
excluded_packages = [
    'PyInstaller', '_pyinstaller_hooks_contrib', 'pyinstaller_hooks_contrib',
    'pip', 'setuptools', 'pkg_resources', 'altgraph', 'win32ctypes', 'packaging', 'pefile'
]

# 排除不需要的文件類型
excluded_file_types = ['.pdb', '.lib', '.a', '.ilk']

a = Analysis(
    ['../WallpaperDownloader.pyw'],
    pathex=[],
    binaries=[],
    datas=[('../Icon/DepotDownloader.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

a.binaries = [
    binary for binary in a.binaries
    if not any(binary[0].startswith(prefix) for prefix in excluded_packages)
    and not any(binary[1].lower().endswith(ext) for ext in excluded_file_types)
]

pyz = PYZ(a.pure, a.zipped_data, compress=True)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WallpaperDownloader',
    version='version_info.txt',
    icon=['../Icon/DepotDownloader.ico'],
    debug=False,
    bootloader_ignore_signals=True,
    strip=False, # GitHub Actions 的環境啟用, 可能會無法運行
    upx=True,
    upx_exclude=['python3.dll', 'libcrypto-3.dll'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)