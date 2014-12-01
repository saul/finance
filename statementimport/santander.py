import decimal
import re

from transactions.models import *
from .importer import BaseImporter, BaseProcessor
from .util import parse_currency, get_or_create_alias


class SantanderImporter(BaseImporter):
    pass


@SantanderImporter.processor
class CashWithdrawalProcessor(BaseProcessor):
    transaction_class = CashWithdrawalTransaction
    pattern = re.compile(
        r'CASH WITHDRAWAL AT (?P<atm>.+), (?P<area>.+),(?P<requested_amount>\d+\.\d{2}) (?P<currency>.{3}) , (ON (?P<date>\d{2}-\d{2}-\d{4}))?')

    def clean_fields(self, fields):
        fields['requested_amount'] = parse_currency(fields['requested_amount'])
        return fields


@SantanderImporter.processor
class BillPaymentProcessor(BaseProcessor):
    transaction_class = BillPaymentTransaction
    pattern = re.compile(
        r'BILL PAYMENT (VIA (?P<via>.+) )?(TO (?P<recipient>.+?) (REFERENCE (?P<ref>.+?))? ?(, MANDATE NO (?P<mandate>\d+))?|FROM (?P<sender>.+), REFERENCE (?P<sender_ref>.+))$')

    def clean_fields(self, fields):
        return {
            'counterparty': get_or_create_alias(fields['recipient'] or fields['sender']),
            'ref': fields['ref'] or fields['sender_ref'],
            'mandate': fields['mandate'] or 0,
            'amount': fields['amount'],
            'cleared_date': fields['cleared_date'],
            # 'via': fields['via']  # "FASTER PAYMENT" or None
        }


@SantanderImporter.processor
class CardPaymentProcessor(BaseProcessor):
    transaction_class = CardPaymentTransaction
    pattern = re.compile(
        r'CARD PAYMENT TO (?P<recipient>.+)(,(?P<requested_amount>\d+\.\d{2}) (?P<currency>.{3}), RATE (?P<rate>\d+.\d{2})/GBP ON (?P<date>\d{2}-\d{2}-\d{4})( NON-STERLING (.+))?| ON (?P<date2>\d{4}-\d{2}-\d{2}))')

    def clean_fields(self, fields):
        return {
            'recipient': get_or_create_alias(fields['recipient']),
            'currency': fields['currency'] or 'GBP',
            'rate': decimal.Decimal(fields['rate'] or '1.00'),
            'requested_amount': fields['requested_amount'] or fields['amount'],
            'date': fields['date'] or fields['date2'],
            'amount': fields['amount'],
            'cleared_date': fields['cleared_date'],
        }


@SantanderImporter.processor
class BankGiroCreditProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'BANK GIRO CREDIT REF (?P<sender>.+), (?P<ref>.+)')

    def clean_fields(self, fields):
        fields['sender'] = get_or_create_alias(fields['sender'])
        fields['type'] = CreditTransaction.CreditType.GIRO
        return fields


@SantanderImporter.processor
class FasterPaymentProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'FASTER PAYMENTS RECEIPT REF.(?P<ref>.+) FROM (?P<sender>.+)')

    def clean_fields(self, fields):
        fields['sender'] = get_or_create_alias(fields['sender'])
        fields['type'] = CreditTransaction.CreditType.FASTER_PAYMENT
        return fields


@SantanderImporter.processor
class CreditProcessor(BaseProcessor):
    transaction_class = CreditTransaction
    pattern = re.compile(r'CREDIT FROM (?P<sender>.+) ON (?P<date>\d{4}-\d{2}-\d{2})')

    def clean_fields(self, fields):
        fields['sender'] = get_or_create_alias(fields['sender'])
        fields['type'] = CreditTransaction.CreditType.CREDIT
        return fields


@SantanderImporter.processor
class DirectDebitProcessor(BaseProcessor):
    transaction_class = DirectDebitTransaction
    pattern = re.compile(
        r'(PAID TRANSACTION )?DIRECT DEBIT PAYMENT TO (?P<recipient>.+) REF (?P<ref>.+?)(, MANDATE NO (?P<mandate>\d+))?$')

    def clean_fields(self, fields):
        fields['recipient'] = get_or_create_alias(fields['recipient'])
        fields['mandate'] = fields['mandate'] or 0
        return fields


@SantanderImporter.processor
class TransferProcessor(BaseProcessor):
    transaction_class = TransferTransaction
    pattern = re.compile(r'TRANSFER (TO|FROM) (?P<counterparty>.+)')

    def clean_fields(self, fields):
        return fields


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
    transaction_class = StandingOrderTransaction
    pattern = re.compile(
        r'STANDING ORDER (VIA (?P<via>.+))? TO (?P<recipient>.+) REFERENCE (?P<ref>.+) , MANDATE NO (?P<mandate>\d+)')

    def clean_fields(self, fields):
        fields['recipient'] = get_or_create_alias(fields['recipient'])
        del fields['via']  # "FASTER PAYMENT" or None
        return fields
