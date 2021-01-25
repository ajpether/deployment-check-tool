# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['C:\\Users\\ajp\\dist\\ur_deployment_check_tool.py'],
             pathex=['C:\\Users\\ajp\\dist\\dist'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
a.datas += [('urlogo.png', 'C:\\Users\\ajp\\dist\\urlogo.png', 'DATA')]
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ur_deployment_check_tool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
