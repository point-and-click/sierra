import subprocess
import sys
from glob import glob
from os.path import isdir, isfile, join


def gather(modules, module_type):
    """
    `gather` function to clone repositories from a file.
    :param modules: TextIO
    :param module_type: string
    """

    for repository in [repository for repository in modules.readlines() if repository.strip()]:
        repository = repository.strip()
        destination = f"{module_type}/{repository.split('/')[-1].split('.')[0]}"
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

    module_types = ['ai', 'input', 'plugins']

    if 'gather' in args:
        for module_type in module_types:
            with open(join(module_type, 'modules.txt')) as modules_file:
                gather(modules_file, module_type)

    if 'install' in args:
        # Install requirements for Sierra
        with open('requirements.txt') as requirements_file:
            install(requirements_file)

        for module_type in module_types:
            for module_glob in glob(join(module_type, '*')):
                if isdir(module_glob) and isfile(join(module_glob, 'requirements.txt')):
                    with open(join(module_glob, 'requirements.txt')) as requirements_file:
                        install(requirements_file)
