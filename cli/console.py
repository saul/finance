import sys
import subprocess

import colorama

from colorama import Fore, Style


colorama.init(autoreset=True)


def stage_print(*args):
    print(Fore.BLUE + Style.BRIGHT + ' ==>', Style.BRIGHT + ' '.join(args))


def call(cmd, *args, **kwargs):
    stage_print(*cmd)

    returncode = subprocess.call(cmd, *args, **kwargs)
    if not returncode:
        print()
        return

    print(Fore.RED + Style.BRIGHT + 'Error' + Style.RESET_ALL, 'command returned non-zero exit status {}\n'.format(returncode), file=sys.stderr)
    sys.exit(returncode)
