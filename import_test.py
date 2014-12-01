import html
from datetime import datetime
import os
import argparse

import django
from django import db


os.environ['DJANGO_SETTINGS_MODULE'] = 'finance.settings'
django.setup()

from statementimport.importer import parse_currency
from statementimport import santander


class StatementImportError(Exception):
    pass


def parse_lines(importer, lines):
    raw_transactions = []

    passed_header = False
    parsing = {}

    # cleanup lines
    lines = map(lambda line: html.unescape(line.replace('\xa0', ' ').strip()), lines)

    for line in lines:
        if not passed_header:
            if not line.startswith('Account:'):
                continue

            passed_header = True
            continue

        if not line:
            if parsing:
                raw_transactions.append(parsing)
                parsing = {}
            continue

        key, value = line.split(': ')

        if key == 'Date':
            value = datetime.strptime(value, '%d/%m/%Y')
        elif key in ('Amount', 'Balance'):
            value = parse_currency(value)

        parsing[key] = value

    raw_transactions.append(parsing)

    for transaction_info in raw_transactions:
        desc = transaction_info['Description']

        if desc.endswith('FEE'):
            # TODO: fee handling
            continue

        processed = importer.process(desc, amount=transaction_info['Amount'], cleared_date=transaction_info['Date'])
        if not processed:
            raise StatementImportError('unmatched transaction {!r}'.format(desc))
            continue

        if not processed.transaction.date:
            processed.transaction.date = processed.transaction.cleared_date

        processed.transaction.week = processed.transaction.date.isocalendar()[1]

        yield processed.transaction


@db.transaction.atomic
def main():
    parser = argparse.ArgumentParser(description='Imports Santander TXT statement.')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Do not commit to database, dry run only')
    parser.add_argument('statement_filepath', help='.txt statement file path')
    args = parser.parse_args()

    sid = db.transaction.savepoint()
    importer = santander.SantanderImporter()

    with open(args.statement_filepath, 'r', encoding='cp1252') as f:
        for transaction in parse_lines(importer, f.readlines()):
            transaction.save()

    if args.dry_run:
        print('--dry-run specified: not committing')
        db.transaction.savepoint_rollback(sid)
    else:
        db.transaction.savepoint_commit(sid)


if __name__ == '__main__':
    main()
