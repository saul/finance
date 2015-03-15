from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms import layout

from finance.forms import LenientChoiceField
from transactions.forms import get_category_choices


class CreateCounterPartyPatternForm(forms.Form):
    counterparty = forms.CharField(label='Name', max_length=100)
    auto_categorise = LenientChoiceField()
    pattern = forms.CharField(max_length=200)

    helper = FormHelper()
    helper.add_input(layout.Button('preview', 'Preview', css_id='pattern-preview', css_class='btn-default'))
    helper.add_input(layout.Submit('submit', 'Submit', css_class='btn-success'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auto_categorise'].choices = get_category_choices()



