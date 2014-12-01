from django.db import models


class CounterParty(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    auto_classify = models.ForeignKey('transactions.Category', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'counter parties'

    def __str__(self):
        return self.name


class Pattern(models.Model):
    counterparty = models.ForeignKey(CounterParty)
    regex = models.CharField(max_length=200)

    class Meta:
        unique_together = ('counterparty', 'regex')


class Alias(models.Model):
    alias = models.CharField(max_length=100, primary_key=True)
    counterparty = models.ForeignKey(CounterParty)

    def __str__(self):
        return self.pk
