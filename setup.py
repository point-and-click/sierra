import subprocess
import sys
from glob import glob
from os.path import isdir, isfile, join
from shutil import copy

from yaml import safe_load


def clone(repository, path):
    """
    `gather` function to clone repositories to a specific path.
    :param repository: string
    :param path: string    """

    destination = f"{path}/{repository.split('/')[-1].split('.')[0]}"
    try:
        subprocess.check_call(
            [
                "git",
                "clone",
                repository,
                destination
            ]
        )
    except subprocess.CalledProcessError:
        print(f'{repository} already exists. Skipping...')


def install(requirements):
    """
    `install` function to install requirements from a file.
    :param requirements: TextIO
    """
    for package in [package for package in requirements.readlines() if package.strip()]:
        if package.startswith('#'):
            continue
        package = package.strip()
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package
            ]
        )


if __name__ == '__main__':
    args = sys.argv[1:]

    with open("config/modules.yaml") as modules_file:
        modules_yaml = safe_load(modules_file)

    if 'clone' in args:
        with open("config/modules.yaml") as modules_file:
            modules_yaml = safe_load(modules_file)

        for module_type, repositories in modules_yaml.items():
            for repository in repositories:
                clone(repository, module_type)


    if 'install' in args:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip"
            ]
        )

        # Install requirements for Sierra
        with open('requirements.txt') as requirements_file:
            install(requirements_file)

        for module_type, _ in modules_yaml.items():
            for module_glob in glob(join(module_type, '*')):
                if isdir(module_glob) and isfile(join(module_glob, 'requirements.txt')):
                    with open(join(module_glob, 'requirements.txt')) as requirements_file:
                        install(requirements_file)

    if 'copy' in args:
        for module_type, _ in modules_yaml.items():
            for module_glob in glob(join(module_type, '*')):
                if isdir(module_glob) and isfile(join(module_glob, 'secrets.yaml.example')):
                    copy(join(module_glob, 'secrets.yaml.example'), join(module_glob, 'secrets.yaml'))