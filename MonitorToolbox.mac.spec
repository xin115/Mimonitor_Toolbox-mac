# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["monitor_controller.py"],
    pathex=[],
    binaries=[
        ("assets/runtime/adb", "assets/runtime"),
        ("assets/runtime/MtkDirectTool.jar", "assets/runtime"),
        ("assets/runtime/ColorfulLedTool.jar", "assets/runtime"),
        ("assets/adb_guardian/adbguardian-signed.apk", "assets/adb_guardian"),
    ],
    datas=[],
    hiddenimports=["qfluentwidgets"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MonitorToolbox",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MonitorToolbox",
)

app = BUNDLE(
    coll,
    name="MonitorToolbox.app",
    icon="assets/app/icon.icns",
    bundle_identifier="com.mimonitor.toolbox",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": "2.5.5",
    },
)
