import os
import subprocess
import sys
from distutils import dir_util, file_util


def copy_directory(src, dst):
    print('    - [' + src + '] -> [' + dst + ']')
    if not os.path.isdir(src):
        exit(1)
    dir_util.copy_tree(src, dst)


def copy_file(src, dst):
    print('    - [' + src + '] -> [' + dst + ']')
    if os.path.isfile(src):
        file_util.copy_file(src, dst)


api = int(os.getenv('ANDROID_PLATFORM', '21'))
ndk = os.getenv('ANDROID_NDK', 'android-ndk')
if not os.path.isdir(ndk):
    ndk = os.path.join(os.getenv('ANDROID_SDK_ROOT', 'android-sdk'), 'ndk-bundle')

if not os.path.isdir(ndk):
    ndk = os.path.join(os.getenv('ANDROID_HOME', 'android-sdk'), 'ndk-bundle')

print('ndk: ' + ndk)

system = sys.platform

if system.startswith('linux'):
    system = 'linux'
if system == 'win32' or system == 'cygwin':
    system = 'windows'

print('system: ' + system)

output = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sysroot')
output = os.getenv('WIMAL_SYSROOT', output)

sysroots = ('arm', 'a64', 'x86', 'x64')

architectures = {
    'arm': 'arm',
    'a64': 'arm64',
    'x86': 'x86',
    'x64': 'x86_64'
}
prefixes = {
    'arm': 'arm-linux-androideabi-4.9',
    'a64': 'aarch64-linux-android-4.9',
    'x86': 'x86-4.9',
    'x64': 'x86_64-4.9'
}
abis = {
    'arm': 'armeabi-v7a',
    'a64': 'arm64-v8a',
    'x86': 'x86',
    'x64': 'x86_64'
}

for sysroot in sysroots:
    level = api

    if sysroot == 'a64' or sysroot == 'x64':
        if level < 21:
            level = 21

    print('+ [' + sysroot + '-android]:')

    root = os.path.join(output, sysroot + '-android', 'usr')

    platform = os.path.join(ndk, 'platforms', 'android-' + str(level))

    arch = architectures[sysroot]
    copy_directory(os.path.join(platform, 'arch-' + arch, 'usr', 'lib'), os.path.join(root, 'lib'))

    copy_directory(os.path.join(ndk, 'sysroot', 'usr', 'include'), os.path.join(root, 'include'))

    if level < 21:
        copy_directory(
            os.path.join(ndk, 'sources', 'android', 'support', 'include'),
            os.path.join(root, 'local', 'include')
        )

    copy_directory(
        os.path.join(ndk, 'sources', 'cxx-stl', 'llvm-libc++', 'include'),
        os.path.join(root, 'include', 'c++', 'v1')
    )
    copy_directory(
        os.path.join(ndk, 'sources', 'cxx-stl', 'llvm-libc++abi', 'include'),
        os.path.join(root, 'include', 'c++', 'v1')
    )

    prefix = prefixes[sysroot]
    copy_directory(
        os.path.join(ndk, 'toolchains', prefix, 'prebuilt', system + '-x86_64', 'lib', 'gcc'),
        os.path.join(root, 'lib', 'gcc')
    )

    abi = abis[sysroot]

    copy_file(
        os.path.join(ndk, 'sources', 'cxx-stl', 'llvm-libc++', 'libs', abi, 'libc++abi.a'),
        os.path.join(root, 'lib', 'libc++abi.a')
    )

    copy_file(
        os.path.join(ndk, 'sources', 'cxx-stl', 'llvm-libc++', 'libs', abi, 'libc++_shared.so'),
        os.path.join(root, 'lib', 'libc++_shared.so')
    )

    copy_file(
        os.path.join(ndk, 'sources', 'cxx-stl', 'llvm-libc++', 'libs', abi, 'libunwind.a'),
        os.path.join(root, 'lib', 'libunwind.a')
    )

    if level < 21:
        copy_file(
            os.path.join(
                ndk, 'sources', 'cxx-stl', 'llvm-libc++', 'libs', abi, 'libandroid_support.a'
            ),
            os.path.join(root, 'lib', 'libandroid_support.a')
        )

    copy_file(
        os.path.join(
            ndk, 'sources', 'cxx-stl', 'llvm-libc++', 'libs', abi, 'libc++.so.' + str(level)
        ),
        os.path.join(root, 'lib', 'libc++.so')
    )

    subprocess.call([
        os.path.join(
            ndk, 'toolchains', 'llvm', 'prebuilt', system + '-x86_64', 'bin', 'llvm-objcopy'
        ),
        '--strip-all',
        os.path.join(root, 'lib', 'libc++_shared.so')
    ])
