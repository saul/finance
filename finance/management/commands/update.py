from django.core.management.base import BaseCommand

from cli import console


class Command(BaseCommand):
    def handle(self, *args, **options):
        console.stage_print('Migrating database...')
        console.call(['pip', 'install', '-r', 'requirements.txt'])

        console.stage_print('Migrating database...')
        console.call(['python', 'manage.py', 'migrate'])

        console.stage_print('Compiling front-end assets...')
        console.call(['grunt'], shell=True)
