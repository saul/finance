import decimal
import re
import html
from datetime import datetime

from transactions.models import *
from .importer import BaseImporter, BaseProcessor, StatementImportError
from .util import parse_currency, get_or_create_alias


class SantanderImporter(BaseImporter):
    name = 'text'
    description = 'Imports Santander UK statements from .txt files'

    def process(self, path):
        with open(path, 'r', encoding='cp1252') as f:
            yield from self.process_file(f.readlines())


    def process_file(self, lines):
        raw_transactions = []

        passed_header = False
        parsing = {}

        # cleanup lines
        lines = map(lambda l: html.unescape(l.replace('\xa0', ' ').strip()), lines)

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

            processed = self.process_line(desc, amount=transaction_info['Amount'],
                                          cleared_date=transaction_info['Date'])
            if not processed:
                raise StatementImportError('unmatched transaction {!r}'.format(desc))

            if not processed.transaction.date:
                processed.transaction.date = processed.transaction.cleared_date

            processed.transaction.week = processed.transaction.date.isocalendar()[1]

            processed.transaction.full_clean()
            yield processed.transaction


@SantanderImporter.processor
class CashWithdrawalProcessor(BaseProcessor):
    transaction_class = CashWithdrawalTransaction
    pattern = re.compile(
        r'CASH WITHDRAWAL AT (?P<atm>.+), (?P<area>.+),(?P<requested_amount>\d+\.\d{2}) (?P<currency>.{3}) , (ON (?P<date>\d{2}-\d{2}-\d{4}))?')

    def clean_fields(self, fields):
        fields['requested_amount'] = parse_currency(fields['requested_amount'])
        return fields


@SantanderImporter.processor
class BillPaymentCreditProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'BILL PAYMENT FROM (?P<sender>.+), REFERENCE (?P<ref>.+)')

    def clean_fields(self, fields):
        alias = get_or_create_alias(fields['sender'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'ref': fields['ref'],
            'type': CreditTransaction.CreditType.CREDIT
        }


@SantanderImporter.processor
class BillPaymentDebitProcessor(BaseProcessor):
    transaction_class = PaymentTransaction
    pattern = re.compile(
        r'BILL PAYMENT (VIA FASTER PAYMENT )?TO (?P<recipient>.+?) (REFERENCE (?P<ref>.+?))? ?(, MANDATE NO (?P<mandate>\d+))?$')

    def clean_fields(self, fields):
        alias = get_or_create_alias(fields['recipient'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'ref': fields['ref'],
            'mandate': fields['mandate'] or 0,
            'type': PaymentTransaction.PaymentType.BILL_PAYMENT
        }


@SantanderImporter.processor
class CardPaymentProcessor(BaseProcessor):
    transaction_class = CardPaymentTransaction
    pattern = re.compile(
        r'CARD PAYMENT TO (?P<recipient>.+)(,(?P<requested_amount>\d+\.\d{2}) (?P<currency>.{3}), RATE (?P<rate>\d+.\d{2})/GBP ON (?P<date>\d{2}-\d{2}-\d{4})( NON-STERLING (.+))?| ON (?P<date2>\d{4}-\d{2}-\d{2}))')

    def clean_fields(self, fields):
        recipient = get_or_create_alias(fields['recipient'])
        return {
            'counterparty_alias': recipient,
            'category': recipient.counterparty.auto_categorise,
            'currency': fields['currency'] or 'GBP',
            'rate': decimal.Decimal(fields['rate'] or '1.00'),
            'requested_amount': fields['requested_amount'] or fields['amount'],
            'date': fields['date'] or fields['date2']
        }


@SantanderImporter.processor
class BankGiroCreditProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'BANK GIRO CREDIT REF (?P<sender>.+), (?P<ref>.+)')

    def clean_fields(self, fields):
        alias = get_or_create_alias(fields['sender'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'ref': fields['ref'],
            'type': CreditTransaction.CreditType.GIRO
        }


@SantanderImporter.processor
class FasterPaymentProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'FASTER PAYMENTS RECEIPT REF.(?P<ref>.+) FROM (?P<sender>.+)')

    def clean_fields(self, fields):
        alias = get_or_create_alias(fields['sender'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'ref': fields['ref'],
            'type': CreditTransaction.CreditType.FASTER_PAYMENT
        }


@SantanderImporter.processor
class CreditProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'CREDIT FROM (?P<sender>.+) ON (?P<date>\d{4}-\d{2}-\d{2})')

    def clean_fields(self, fields):
        alias = get_or_create_alias(fields['sender'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'type': CreditTransaction.CreditType.CREDIT
        }


@SantanderImporter.processor
class DirectDebitProcessor(BaseProcessor):
    transaction_class = PaymentTransaction
    pattern = re.compile(
        r'(PAID TRANSACTION )?DIRECT DEBIT PAYMENT TO (?P<recipient>.+) REF (?P<ref>.+?)(, MANDATE NO (?P<mandate>\d+))?$')

    def clean_fields(self, fields):
        assert fields['amount'] < 0
        alias = get_or_create_alias(fields['recipient'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'ref': fields['ref'],
            'mandate': fields['mandate'] or 0,
            'type': PaymentTransaction.PaymentType.DIRECT_DEBIT
        }


@SantanderImporter.processor
class TransferProcessor(BaseProcessor):
    transaction_class = TransferTransaction
    pattern = re.compile(r'TRANSFER (TO|FROM) (?P<counterparty>.+)')

    def clean_fields(self, fields):
        alias = get_or_create_alias(fields['counterparty'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise
        }


@SantanderImporter.processor
class RegularTransferProcessor(BaseProcessor):
    transaction_class = RegularTransferTransaction
    pattern = re.compile(
        r'REGULAR TRANSFER PAYMENT TO ACCOUNT (?P<sortcode>\d{6}) (?P<account>\d{8}), MANDATE NO (?P<mandate>\d+)')


@SantanderImporter.processor
class CashPaidProcessor(BaseProcessor):
    transaction_class = CashPaidTransaction
    pattern = re.compile(r'CASH PAID IN AT (?P<branch>.+)')


@SantanderImporter.processor
class InterestProcessor(BaseProcessor):
    transaction_class = InterestTransaction
    pattern = re.compile(r'INTEREST PAID AFTER TAX (?P<tax>\d+\.\d{2}) DEDUCTED')

    def clean_fields(self, fields):
        fields['tax'] = decimal.Decimal(fields['tax'])
        return fields


@SantanderImporter.processor
class StandingOrderProcessor(BaseProcessor):
    transaction_class = PaymentTransaction
    pattern = re.compile(
        r'STANDING ORDER (VIA FASTER PAYMENT )?TO (?P<recipient>.+) REFERENCE (?P<ref>.+) , MANDATE NO (?P<mandate>\d+)')

    def clean_fields(self, fields):
        assert fields['amount'] < 0
        alias = get_or_create_alias(fields['recipient'])
        return {
            'counterparty_alias': alias,
            'category': alias.counterparty.auto_categorise,
            'ref': fields['ref'],
            'mandate': fields['mandate'],
            'type': PaymentTransaction.PaymentType.STANDING_ORDER
        }
