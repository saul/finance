import sys
import inspect
from optparse import make_option

from colorama import Style, Fore

from django import db
from django.core.management.base import BaseCommand

from statementimport.importer import BaseImporter
from cli import console


class Command(BaseCommand):
    args = '<importer> <input_path>'
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry-run', action='store_true', help='Do not commit to database, dry run only'),
    )

    def handle(self, importer, input_path, **options):
        # Attempt to import the module
        module_name, importer_name = importer.split('.', 1)
        module = getattr(__import__('statementimport', fromlist=[module_name]), module_name)

        # Iterate all members of the module
        console.stage_print('Available importers in the', module_name, 'module:')
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

        console.stage_print('Using importer', importer_name, '...')

        # Begin import
        sid = db.transaction.savepoint()

        for transaction in importer.process(input_path):
            transaction.save()

        if options['dry_run']:
            print(Fore.YELLOW + 'Not committing to database', '(--dry-run specified)')
            db.transaction.savepoint_rollback(sid)
        else:
            print('Committing... ', end='')
            db.transaction.savepoint_commit(sid)
            print(Fore.GREEN + 'done')
