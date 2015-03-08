import re

from django.views.generic import TemplateView, DetailView, ListView, FormView
from django.db.models import Sum, Count, Max, Avg
from django.db import transaction
from django.contrib import messages
from django import http
from django.shortcuts import redirect

from transactions.models import Transaction, Category
from .models import Alias, CounterParty, Pattern
from .forms import CreateCounterPartyPatternForm, CategoryForm


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
            category, _ = Category.objects.get_or_create(
                name__iexact=form.cleaned_data['auto_categorise'],
                defaults={'name': form.cleaned_data['auto_categorise']}
            )

            if CounterParty.objects.filter(pk__iexact=form.cleaned_data['counterparty']).exists():
                transaction.rollback()
                messages.error(self.request, 'A counterparty under this name already exists')
                return self.form_invalid(form)

            counterparty = CounterParty.objects.create(
                pk=form.cleaned_data['counterparty'],
                auto_categorise=category
            )

            # create a pattern for this counterparty
            pattern = form.cleaned_data['pattern']
            Pattern.objects.create(counterparty=counterparty, regex=pattern)

            aliases = AliasPatternMatchesView.get_matches(pattern)

            # find which aliases this pattern matches that already have a counterparty
            invalid_aliases = aliases.annotate(
                num_counterparty_aliases=Count('counterparty__alias')
            ).filter(
                num_counterparty_aliases__gt=1
            )

            if invalid_aliases.exists():
                transaction.rollback()
                messages.error(self.request, 'This pattern matches aliases that already belong to a counterparty')
                return self.form_invalid(form)

            # update alias counterparties
            aliases.update(counterparty=counterparty)

            # update the category on all uncategorised transactions
            uncategorised_transactions = Transaction.objects.filter(
                counterparty_alias__counterparty=counterparty, category=None
            ).update(
                category=category
            )

            # delete orphaned counterparties
            CounterParty.objects.annotate(
                num_aliases=Count('alias')
            ).filter(
                num_aliases=0
            ).delete()

            messages.success(
                self.request,
                'Successfully created new counterparty (merged {} existing aliases)'.format(aliases.count())
            )
            return http.HttpResponseRedirect(counterparty.get_absolute_url())


class AliasPatternMatchesView(TemplateView):
    template_name = 'alias_pattern_matches.html'

    @staticmethod
    def get_matches(pattern):
        pks = filter(lambda alias: re.search(pattern, alias, re.IGNORECASE), Alias.objects.values_list('pk', flat=True))
        return Alias.objects.filter(pk__in=pks)

    def get_context_data(self):
        return {
            'matches': AliasPatternMatchesView.get_matches(self.request.GET['pattern']).annotate(
                num_counterparty_aliases=Count('counterparty__alias'))
        }


class CounterPartyDetailView(DetailView):
    model = CounterParty
    template_name = 'counterparty_detail.html'
    context_object_name = 'counterparty'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = Transaction.objects.filter(
            counterparty_alias__in=self.object.alias_set.values_list('pk', flat=True))
        context['transactions'] = transactions.order_by('-date')
        context['metrics'] = transactions.aggregate(sum=Sum('amount'), avg=Avg('amount'), count=Count('amount'))
        return context


class AddPatternModalView(TemplateView):
    template_name = 'counterparty_app_pattern_modal.html'


class CategoriseModalView(FormView):
    model = CounterParty
    template_name = 'counterparty_categorise_modal.html'
    form_class = CategoryForm

    def dispatch(self, request, pk):
        self.counterparty = CounterParty.objects.get(pk=pk)
        return super().dispatch(request)

    def form_valid(self, form):
        transactions = Transaction.objects.filter(counterparty_alias__counterparty=self.counterparty, category__isnull=True)
        transactions.update(category=form.cleaned_data['category'])

        self.counterparty.auto_categorise_id = form.cleaned_data['category']
        self.counterparty.save()

        messages.success(self.request, 'Transactions updated successfully')

        return redirect('reload_top')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['counterparty'] = self.counterparty
        return context
