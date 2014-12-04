from django.core.management.base import BaseCommand

from cli import console


class Command(BaseCommand):
    def handle(self, *args, **options):
        console.stage_print('Updating Python dependencies...')
        console.call(['pip', 'install', '-r', 'requirements.txt'])

        console.stage_print('Updating Node dependencies...')
        console.call(['npm', 'install'], shell=True)

        console.stage_print('Migrating database...')
        console.call(['python', 'manage.py', 'migrate'])

        console.stage_print('Compiling front-end assets...')
        console.call(['grunt'], shell=True)
