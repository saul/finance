from django.contrib import admin

from .models import CounterParty, Alias, Pattern


@admin.register(CounterParty)
class CounterPartyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('auto_categorise',)


@admin.register(Alias, Pattern)
class AliasAdmin(admin.ModelAdmin):
    list_display = ('pk', 'counterparty')
