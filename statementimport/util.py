import decimal
import re

from counterparty.models import Alias, CounterParty, Pattern


def parse_currency(amount):
    amount = amount.replace(',', '').replace('£', '')

    if ' ' in amount:
        if not amount.endswith(' GBP'):
            raise ValueError('unexpected currency (%s)' % amount)

        amount = amount[:-4]

    return decimal.Decimal(amount)


def get_or_create_alias(alias_name):
    try:
        return Alias.objects.get(pk__iexact=alias_name)
    except Alias.DoesNotExist:
        pass

    counterparty = None

    # does this alias match a counterparty pattern?
    for pattern in Pattern.objects.all():
        if not re.search(pattern.regex, alias_name, re.IGNORECASE):
            continue

        if counterparty:
            raise Alias.MultipleObjectsReturned('alias matched by multiple patterns')

        counterparty = pattern.counterparty

    if not counterparty:
        counterparty = CounterParty.objects.create(pk=alias_name)

    return Alias.objects.create(pk=alias_name, counterparty=counterparty)
