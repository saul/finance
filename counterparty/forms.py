from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions

from .models import CounterParty
from transactions.models import Category


class LenientChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True


class CategoryMixin:
    def get_category_choices(self):
        return Category.objects.values_list('pk', 'name')


class CreateCounterPartyPatternForm(forms.Form, CategoryMixin):
    counterparty = forms.CharField(label='Name', max_length=100)
    auto_categorise = LenientChoiceField()
    pattern = forms.CharField(max_length=200)

    helper = FormHelper()
    helper.add_input(layout.Button('preview', 'Preview', css_id='pattern-preview', css_class='btn-default'))
    helper.add_input(layout.Submit('submit', 'Submit', css_class='btn-success'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auto_categorise'].choices = self.get_category_choices()


class CategoryForm(forms.Form, CategoryMixin):
    category = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = self.get_category_choices()
