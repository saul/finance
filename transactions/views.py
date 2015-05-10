import datetime

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import View, ListView, FormView
from django.db.models import Sum, Count
from django.contrib import messages
from django.shortcuts import redirect

from .models import Transaction, Category
from .forms import CategoriseForm


def get_month_transaction_queryset(year, month):
    start = datetime.date(year, month, 1)
    if month == 12:
        end = datetime.date(year + 1, 1, 1)
    else:
        end = datetime.date(year, month + 1, 1)

    return Transaction.objects.filter(date__gte=start, date__lt=end)


class HomeView(ListView):
    model = Transaction
    template_name = 'home.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        today = datetime.date.today()
        month = int(self.request.GET.get('month', today.month))
        year = int(self.request.GET.get('year', today.year))
        return get_month_transaction_queryset(year, month).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        month = int(self.request.GET.get('month', today.month))
        year = int(self.request.GET.get('year', today.year))
        last_year_start = datetime.date(year - 1, 1, 1)
        next_year_start = datetime.date(year + 1, 1, 1)

        months = []
        for month_num in range(12):
            month_start = datetime.date(year, month_num + 1, 1)
            months.append((month_start, month_start > today))

        context['transaction_timeline'] = {
            'previous_year': (year - 1, last_year_start > today),
            'next_year': (year + 1, next_year_start > today),
            'current_month': month,
            'months': months
        }

        context['in_out_data_url'] = reverse('transactions:in_out_data', args=[year, month])

        return context


class IncomingOutgoingDataView(View):
    def get(self, request, year, month):
        transaction_qs = get_month_transaction_queryset(int(year), int(month))

        category_netamt_map = dict(transaction_qs.values('category__name').annotate(total=Sum('amount')).values_list('category__name', 'total'))

        categories = list(Category.objects.values_list('name', flat=True))

        net_data = ['Net']

        for category in [None] + categories:
            net_data.append(float(category_netamt_map.get(category, 0)))

        net_data.append(float(transaction_qs.aggregate(total=Sum('amount'))['total']))

        return JsonResponse({
            'data': [
                ['Category', 'Uncategorised'] + categories + [{'role': 'annotation'}],
                net_data
            ],
            'options': {
                'isStacked': True,
                'legend': {
                    'position': 'top',
                    'maxLines': 0
                },
                'backgroundColor': 'transparent'
            }
        })


class CategoriseView(FormView):
    form_class = CategoriseForm

    def form_valid(self, form):
        transaction = form.cleaned_data['transaction']

        category = form.cleaned_data['category']
        old_category = transaction.category

        # If we cannot find the category, assume it's not a PK but the name of the new category to create
        try:
            transaction.category = Category.objects.get(pk=category)
        except ValueError:
            transaction.category = Category.objects.create(name=category)

        transaction.save()

        # delete any orphaned categories
        if old_category:
            Category.objects.annotate(
                num_transactions=Count('transaction'),
                num_counterparties=Count('counterparty')
            ).filter(
                num_transactions=0,
                num_counterparties=0
            ).delete()

        messages.success(self.request, 'Updated category successfully')
        return redirect(self.request.META['HTTP_REFERER'])

    def form_invalid(self, form):
        messages.error(self.request, 'Unable to categorise transaction')
        return redirect(self.request.META['HTTP_REFERER'])
