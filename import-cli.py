#!/usr/bin/env python

import os
import argparse
import sys
import inspect

import colorama
from colorama import Style, Fore
import django
from django import db


os.environ['DJANGO_SETTINGS_MODULE'] = 'finance.settings'
django.setup()

from statementimport.importer import BaseImporter

colorama.init(autoreset=True)


@db.transaction.atomic
def main():
    parser = argparse.ArgumentParser(description='Imports bank statements into the finance database.')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Do not commit to database, dry run only')
    parser.add_argument('importer', help='importer (format: <module>.<name>)')
    parser.add_argument('input', help='path to input file')
    args = parser.parse_args()

    # Print CLI header
    print(Fore.CYAN + '{}: {}\n'.format(sys.argv[0], parser.description))

    # Attempt to import the module
    module_name, importer_name = args.importer.split('.', 1)
    module = getattr(__import__('statementimport', fromlist=[module_name]), module_name)

    # Iterate all members of the module
    print('Available importers in the', Style.BRIGHT + module_name, 'module:')
    importer = None

    for name, importer_cls in inspect.getmembers(module):
        if not inspect.isclass(importer_cls):
            continue

        if BaseImporter not in inspect.getmro(importer_cls)[1:]:
            continue

        print(' -', Style.BRIGHT + importer_cls.name, Style.DIM + '({})'.format(importer_cls.__name__))

        if importer_cls.name == importer_name:
            importer = importer_cls()

    if importer is None:
        print(Fore.RED + 'Failed to find importer `{}`'.format(importer_name))
        sys.exit(1)

    print('\nUsing importer', Style.BRIGHT + args.importer, '...\n')

    # Begin import
    sid = db.transaction.savepoint()

    for transaction in importer.process(args.input):
        transaction.save()

    if args.dry_run:
        print(Fore.YELLOW + 'Not committing to database', '(--dry-run specified)')
        db.transaction.savepoint_rollback(sid)
    else:
        db.transaction.savepoint_commit(sid)
        print(Fore.GREEN + 'Import committed to database')


if __name__ == '__main__':
    main()
