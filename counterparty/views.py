import re

from django.views.generic import TemplateView, DetailView, ListView, FormView
from django.db.models import Sum, Count, Max
from django.db import transaction
from django.contrib import messages
from django import http

from transactions.models import Transaction
from .models import Alias, CounterParty
from .forms import CreateCounterPartyPatternForm


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


class CreatePatternedCounterPartyView(FormView):
    template_name = 'counterparty_create.html'
    form_class = CreateCounterPartyPatternForm

    def form_valid(self, form):
        with transaction.atomic():
            counterparty, _ = CounterParty.objects.get_or_create(pk__iexact=form.cleaned_data['counterparty'])
            print('{!r}'.format(counterparty))

            pattern = form.cleaned_data['pattern']
            aliases = AliasPatternMatchesView.get_matches(pattern)

            # find which aliases this pattern matches that already have a counterparty
            invalid_aliases = aliases.annotate(num_counterparty_aliases=Count('counterparty__alias')).filter(num_counterparty_aliases__gt=1)
            if invalid_aliases.exists():
                transaction.rollback()
                messages.error(self.request, 'This pattern matches aliases that already belong to a counterparty')
                return self.form_invalid(form)

            # update alias counterparties
            aliases.update(counterparty=counterparty)

            # delete orphaned counterparties
            CounterParty.objects.annotate(num_aliases=Count('alias')).filter(num_aliases=0).delete()

            return http.HttpResponseRedirect(counterparty.get_absolute_url())


class AliasPatternMatchesView(TemplateView):
    template_name = 'alias_pattern_matches.html'

    @staticmethod
    def get_matches(pattern):
        pks = filter(lambda alias: re.search(pattern, alias, re.IGNORECASE), Alias.objects.values_list('pk', flat=True))
        return Alias.objects.filter(pk__in=pks)

    def get_context_data(self):
        return {
            'matches': AliasPatternMatchesView.get_matches(self.request.GET['pattern']).annotate(num_counterparty_aliases=Count('counterparty__alias'))
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
