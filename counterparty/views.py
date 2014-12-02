import re

from django.views.generic import View, DetailView, ListView
from django.db.models import Sum, Count, Max
from .models import Alias, CounterParty
from transactions.models import Transaction


class CounterPartyListView(ListView):
    model = CounterParty
    template_name = 'counterparty_list.html'
    context_object_name = 'counterparties'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(net_amount=Sum('alias__transaction__amount'),
                         total_transactions=Count('alias__transaction'),
                         most_recent_transaction=Max('alias__transaction__date'))
        qs = qs.order_by('-most_recent_transaction')
        return qs


class CreatePatternedCounterPartyView(View):
    template_name = 'counterparty_create.html'

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
