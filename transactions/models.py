from django.db import models
from polymorphic import PolymorphicModel
from counterparty.models import CounterParty


class Category(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    parent = models.ForeignKey('self', null=True, related_name='children')


class Transaction(PolymorphicModel):
    description = models.CharField(max_length=512)
    category = models.ForeignKey(Category, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    cleared_date = models.DateField()
    date = models.DateField()
    week = models.IntegerField()  # automatically calculated from `date` on save

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


class BillPaymentTransaction(Transaction):
    ref = models.CharField(max_length=64)
    mandate = models.IntegerField(null=True)
    counterparty = models.ForeignKey(CounterParty)

    class Meta:
        verbose_name = 'bill payment'

    class AppMeta:
        list_template_name = 'transaction_detail/bill_payment.html'

    def __repr__(self):
        if self.amount < 0:
            return '{}, recipient={!r}, ref={!r}, mandate={}>'.format(
                super().__repr__()[:-1],
                self.counterparty,
                self.ref,
                self.mandate,
            )
        else:
            return '{}, sender={!r}, ref={!r}>'.format(
                super().__repr__()[:-1],
                self.counterparty,
                self.ref,
            )


class CardPaymentTransaction(Transaction):
    recipient = models.ForeignKey(CounterParty)
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
            self.recipient,
            self.requested_amount,
            self.currency,
        )


class DirectDebitTransaction(Transaction):
    recipient = models.ForeignKey(CounterParty)
    ref = models.CharField(max_length=64)
    mandate = models.IntegerField()

    class Meta:
        verbose_name = 'direct debit'

    class AppMeta:
        list_template_name = 'transaction_detail/direct_debit.html'

    def __repr__(self):
        return '{}, recipient={!r}, ref={!r}, mandate={}>'.format(
            super().__repr__()[:-1],
            self.recipient,
            self.ref,
            self.mandate,
        )


class CreditTransaction(Transaction):
    sender = models.ForeignKey(CounterParty)
    ref = models.CharField(max_length=64)

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
            self.sender,
            self.ref,
        )


class TransferTransaction(Transaction):
    # TODO: could this be a Recipient foreign key?
    counterparty = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'transfer'

    class AppMeta:
        list_template_name = 'transaction_detail/transfer.html'

    def __repr__(self):
        return '{}, {}={!r}>'.format(
            super().__repr__()[:-1],
            'to' if self.amount < 0 else 'from',
            self.counterparty,
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


class StandingOrderTransaction(Transaction):
    recipient = models.ForeignKey(CounterParty)
    ref = models.CharField(max_length=64)
    mandate = models.IntegerField()

    class Meta:
        verbose_name = 'standing order'

    class AppMeta:
        list_template_name = 'transaction_detail/standing_order.html'

    def __repr__(self):
        return '{}, to={!r}, ref={!r}, mandate={}>'.format(
            super().__repr__()[:-1],
            self.recipient,
            self.ref,
            self.mandate,
        )
