from django.db import models
from django.core.urlresolvers import reverse


class CounterParty(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    auto_categorise = models.ForeignKey('transactions.Category', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'counter parties'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('counterparty:detail', args=[self.pk])


class Pattern(models.Model):
    regex = models.CharField(max_length=200, primary_key=True)
    counterparty = models.ForeignKey(CounterParty)


class Alias(models.Model):
    alias = models.CharField(max_length=100, primary_key=True)
    counterparty = models.ForeignKey(CounterParty)

    class Meta:
        verbose_name_plural = 'aliases'

    def __str__(self):
        return self.pk
