import re

from django.views.generic import View, DetailView

from .models import Alias, CounterParty
from transactions.models import Transaction


class CreatePatternedCounterPartyView(View):
    def get(self):
        pass


class AliasPatternMatchesView(View):
    template_name = 'alias_pattern_matches.html'

    @staticmethod
    def get_matches(regex):
        for alias in Alias.objects.all():
            if regex.search(alias.pk, re.IGNORECASE):
                yield alias

    def get(self, pattern):
        regex = re.compile(pattern, re.IGNORECASE)
        return {
            'matches': AliasPatternMatchesView.get_matches(regex)
        }


class CounterPartyDetailView(DetailView):
    model = CounterParty
    template_name = 'counterparty_detail.html'
    context_object_name = 'counterparty'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transaction.objects.filter(
            counterparty_alias__in=self.object.alias_set.values_list('pk', flat=True)).order_by('-date')
        return context
