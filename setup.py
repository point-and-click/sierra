import subprocess
import sys
from glob import glob
from os.path import isdir


def install(requirements):
    for package in requirements.readlines():
        package = package.strip()
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == '__main__':

    # Install requirements for AI modules
    for ai_glob in glob("ai/*"):
        if isdir(ai_glob):
            with open(f'{ai_glob}/requirements.txt', 'r') as requirements_file:
                install(requirements_file)

    # Install requirements for input modules
    for input_glob in glob("input/*"):
        if isdir(input_glob):
            with open(f'{input_glob}/requirements.txt', 'r') as requirements_file:
                install(requirements_file)
