import re

from django.db import models


class CounterPartyManager(models.Manager):
    def get_patterns(self):
        return {
            cp['pk']: re.compile(cp['pattern'])
            for cp in self.filter(pattern__isnull=False).values('pk', 'pattern')
        }

    def get_by_alias(self, alias):
        try:
            return self.get(pk=alias)
        except self.model.DoesNotExist:
            current_result = None

            for pk, pattern in self.get_patterns().items():
                if not pattern.search(alias):
                    continue

                if current_result:
                    raise self.model.MultipleObjectsReturned('alias is matched by more than one counterparty')

                return self.get(pk=pk)

            if current_result:
                return current_result

            raise self.model.DoesNotExist()

    def get_or_create_by_alias(self, alias):
        try:
            return self.get_by_alias(alias), False
        except self.model.DoesNotExist:
            return self.create(pk=alias), True


class CounterParty(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    auto_classify = models.ForeignKey('transactions.Category', null=True, blank=True)
    pattern = models.CharField(max_length=256, null=True, blank=True)

    objects = CounterPartyManager()

    class Meta:
        verbose_name_plural = 'counter parties'

    def __str__(self):
        return self.name
