from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions

from .models import CounterParty


class CreateCounterPartyPatternForm(forms.Form):
    counterparty = forms.CharField(label='Name', max_length=100)
    pattern = forms.CharField(max_length=200)

    helper = FormHelper()
    helper.add_input(layout.Button('preview', 'Preview', css_id='pattern-preview', css_class='btn-default'))
    helper.add_input(layout.Submit('submit', 'Submit', css_class='btn-success'))
