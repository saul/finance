from django import forms

from finance.forms import LenientChoiceField
from .models import Transaction, Category


def get_category_choices():
    return Category.objects.values_list('pk', 'name')


class CategoryForm(forms.Form):
    category = LenientChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = get_category_choices()


class CategoriseForm(CategoryForm):
    transaction = forms.ModelChoiceField(queryset=Transaction.objects.all(), empty_label=None)
    create_category = forms.BooleanField(required=False)
