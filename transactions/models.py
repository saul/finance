from django.db import models
from django.core.exceptions import ValidationError
from polymorphic import PolymorphicModel
from counterparty.models import Alias


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Transaction(PolymorphicModel):
    category = models.ForeignKey(Category, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    cleared_date = models.DateField()
    date = models.DateField()
    week = models.IntegerField()  # automatically calculated from `date` on save
    counterparty_alias = models.ForeignKey(Alias, null=True, blank=True)

    def __repr__(self):
        return '<{} amount={}, date={}, cleared={}>'.format(
            self.__class__.__name__,
            self.amount,
            self.date.strftime('%d/%m/%Y'),
            self.cleared_date.strftime('%d/%m/%Y'),
        )

    @property
    def list_template_name(self):
        return self.AppMeta.list_template_name


class CounterPartyTransaction(Transaction):
    def clean(self):
        if self.counterparty_alias is None:
            raise ValidationError('expected counterparty_alias specified for {} transaction'.format(self.__class__.__name__))


class CashWithdrawalTransaction(Transaction):
    atm = models.CharField(max_length=128)
    area = models.CharField(max_length=64)
    requested_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=6)

    class Meta:
        verbose_name = 'cash withdrawal'

    class AppMeta:
        list_template_name = 'transaction_detail/cash_withdrawal.html'

    def __repr__(self):
        return '{}, atm={!r}, area={!r}>'.format(
            super().__repr__()[:-1],
            self.atm,
            self.area,
        )


class PaymentTransaction(CounterPartyTransaction):
    ref = models.CharField(max_length=64)
    mandate = models.IntegerField(default=0)

    class PaymentType:
        BILL_PAYMENT = 1
        STANDING_ORDER = 2
        DIRECT_DEBIT = 3

        CHOICES = (
            (BILL_PAYMENT, 'bill payment'),
            (STANDING_ORDER, 'standing order'),
            (DIRECT_DEBIT, 'direct debit')
        )

    type = models.IntegerField(choices=PaymentType.CHOICES)

    class Meta:
        verbose_name = 'payment'

    class AppMeta:
        list_template_name = 'transaction_detail/payment.html'

    def __repr__(self):
        return '{}, recipient={!r}, ref={!r}, mandate={}>'.format(
            super().__repr__()[:-1],
            self.counterparty_alias,
            self.ref,
            self.mandate,
        )

    def clean(self):
        super().clean()

        if self.amount > 0:
            raise ValidationError('payment with a positive amount (should be negative)')


class CardPaymentTransaction(CounterPartyTransaction):
    requested_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=6)
    rate = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'card payment'

    class AppMeta:
        list_template_name = 'transaction_detail/card_payment.html'

    def __repr__(self):
        return '{}, recipient={!r}, requested_amount={} {}>'.format(
            super().__repr__()[:-1],
            self.counterparty_alias,
            self.requested_amount,
            self.currency,
        )


class CreditTransaction(CounterPartyTransaction):
    ref = models.CharField(max_length=64, blank=True)

    class CreditType:
        CREDIT = 1
        GIRO = 2
        FASTER_PAYMENT = 3

        CHOICES = (
            (CREDIT, 'credit'),
            (GIRO, 'giro credit'),
            (FASTER_PAYMENT, 'faster payment')
        )

    type = models.IntegerField(choices=CreditType.CHOICES)

    class Meta:
        verbose_name = 'credit'

    class AppMeta:
        list_template_name = 'transaction_detail/credit.html'

    def __repr__(self):
        return '{}, type={!r} from={!r}, ref={!r}>'.format(
            super().__repr__()[:-1],
            self.get_type_display(),
            self.counterparty_alias,
            self.ref,
        )

    def clean(self):
        super().clean()

        if self.amount < 0:
            raise ValidationError('credit with a negative amount (should be positive)')


class TransferTransaction(CounterPartyTransaction):
    class Meta:
        verbose_name = 'transfer'

    class AppMeta:
        list_template_name = 'transaction_detail/transfer.html'

    def __repr__(self):
        return '{}, {}={!r}>'.format(
            super().__repr__()[:-1],
            'to' if self.amount < 0 else 'from',
            self.counterparty_alias,
        )


class RegularTransferTransaction(Transaction):
    sortcode = models.CharField(max_length=6)
    account_number = models.CharField(max_length=8)
    mandate = models.IntegerField()

    class Meta:
        verbose_name = 'regular transfer'

    class AppMeta:
        list_template_name = 'transaction_detail/regular_transfer.html'

    def __repr__(self):
        return '{}, sortcode={}, account={}, mandate={}>'.format(
            super().__repr__()[:-1],
            self.sortcode,
            self.account,
            self.mandate,
        )


class CashPaidTransaction(Transaction):
    branch = models.CharField(max_length=32)

    class Meta:
        verbose_name = 'cash paid'

    class AppMeta:
        list_template_name = 'transaction_detail/cash_paid.html'

    def __repr__(self):
        return '{}, branch={!r}>'.format(
            super().__repr__()[:-1],
            self.branch,
        )


class InterestTransaction(Transaction):
    tax = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'interest'

    class AppMeta:
        list_template_name = 'transaction_detail/interest.html'

    def __repr__(self):
        return '{}, tax={}>'.format(
            super().__repr__()[:-1],
            self.tax,
        )
