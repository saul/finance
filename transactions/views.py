import datetime

from django.views.generic import ListView

from .models import Transaction


class HomeView(ListView):
    model = Transaction
    template_name = 'home.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        today = datetime.date.today()
        month = int(self.request.GET.get('month', today.month))
        year = int(self.request.GET.get('year', today.year))

        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)
        return Transaction.objects.filter(date__gte=start, date__lt=end).order_by('-date')

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

        return context
