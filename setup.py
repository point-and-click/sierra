import subprocess
import sys
from glob import glob
from os.path import isdir, isfile


def install(requirements):
    for package in requirements.readlines():
        package = package.strip()
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == '__main__':
    args = sys.argv[1:]

    if 'install' in args:
        # Install requirements for AI modules
        for ai_glob in glob("ai/*"):
            if isdir(ai_glob):
                if isfile(f'{ai_glob}/requirements.txt'):
                    with open(f'{ai_glob}/requirements.txt', 'r') as requirements_file:
                        install(requirements_file)

        # Install requirements for input modules
        for input_glob in glob("input/*"):
            if isdir(input_glob):
                if isfile(f'{input_glob}/requirements.txt'):
                    with open(f'{input_glob}/requirements.txt', 'r') as requirements_file:
                        install(requirements_file)
