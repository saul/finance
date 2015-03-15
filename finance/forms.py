from django import forms


class LenientChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True
