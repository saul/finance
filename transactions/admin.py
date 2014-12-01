from django.contrib import admin
from .models import CounterParty
from django.contrib.admin import SimpleListFilter


class NullListFilter(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('1', 'Null'),
            ('0', 'Not Null'),
        )

    def queryset(self, request, queryset):
        if self.value() in ('0', '1'):
            kwargs = {'{0}__isnull'.format(self.parameter_name): self.value() == '1'}
            return queryset.filter(**kwargs)
        return queryset


class PatternNullListFilter(NullListFilter):
    title = 'Pattern'
    parameter_name = 'pattern'


class CounterPartyAdmin(admin.ModelAdmin):
    model = CounterParty
    list_display = ('name',)
    list_filter = ('auto_classify', PatternNullListFilter)


admin.site.register(CounterParty, CounterPartyAdmin)
