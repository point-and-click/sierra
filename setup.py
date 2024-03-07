import subprocess
import sys
from glob import glob
from os import path
from os.path import isdir, isfile


def install(requirements):
    """
    `install` function to install requirements from a file.
    :param requirements: TextIO
    """
    for package in [package for package in requirements.readlines() if package.strip()]:
        if package.startswith('#'):
            continue
        package = package.strip()
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == '__main__':
    args = sys.argv[1:]

    if 'install' in args:
        # Install requirements for Sierra
        with open('requirements.txt') as requirements_file:
            install(requirements_file)

        # Install requirements for AI modules
        for ai_glob in glob(path.join('ai', '*')):
            if isdir(ai_glob) and isfile(path.join(ai_glob, 'requirements.txt')):
                with open(path.join(ai_glob, 'requirements.txt')) as requirements_file:
                    install(requirements_file)

        # Install requirements for input modules
        for input_glob in glob(path.join('input', '*')):
            if isdir(input_glob) and isfile(path.join(input_glob, 'requirements.txt')):
                with open(path.join(input_glob, 'requirements.txt')) as requirements_file:
                    install(requirements_file)

        # Install requirements for plugins
        for input_glob in glob(path.join('plugins', '*')):
            if isdir(input_glob) and isfile(path.join(input_glob, 'requirements.txt')):
                with open(path.join(input_glob, 'requirements.txt')) as requirements_file:
                    install(requirements_file)
