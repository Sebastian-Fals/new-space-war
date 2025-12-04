import PyInstaller.__main__
import os
import shutil

# Define paths
base_path = os.getcwd()
dist_path = os.path.join(base_path, 'dist')
release_path = os.path.join(base_path, 'releases', 'v2')

# Clean previous builds
def remove_readonly(func, path, excinfo):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

if os.path.exists(dist_path):
    shutil.rmtree(dist_path, onerror=remove_readonly)
    
if os.path.exists('build'):
    shutil.rmtree('build', onerror=remove_readonly)

# Run PyInstaller
PyInstaller.__main__.run([
    'main.py',
    '--name=Danmaku Space War v2',
    '--onefile',
    '--noconsole',
    '--clean',
    '--add-data=assets;assets',
    '--collect-all=pygame_ce',
    '--collect-all=OpenGL',
    '--noupx', # Disable UPX to prevent virus false positives
    '--version-file=version_info.txt',
    # '--icon=assets/icon.ico', # Uncomment if icon exists
])

# Move to release folder
if not os.path.exists(release_path):
    os.makedirs(release_path)

exe_name = "Danmaku Space War v2.exe"
src_exe = os.path.join(dist_path, exe_name)
dst_exe = os.path.join(release_path, exe_name)

if os.path.exists(src_exe):
    if os.path.exists(dst_exe):
        os.remove(dst_exe)
    shutil.move(src_exe, dst_exe)
    print(f"Build successful! Executable moved to: {dst_exe}")
else:
    print("Build failed: Executable not found in dist/")
