from crispy_forms.layout import Layout, Field
from django import forms
from crispy_forms.helper import FormHelper

from common.models import Vote, Condition, Place
from common import choices

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'custom-select'


class VoteForm(forms.Form):
    your_vote = forms.FloatField(required=True, max_value=10, min_value=0,label='',
                                 widget=forms.NumberInput(
                                     attrs={'id': 'your_vote', 'step': "1.00"}))
    your_vote.widget.attrs['class'] = 'form-control vote-form'
    your_vote.widget.attrs['placeholder'] = "Your vote..."

    def clean_your_vote(self):
        data = self.cleaned_data['your_vote']
        return data

    class Meta:
        model = Vote
        fields = ('vote',)


class ConditionForm(BaseForm):

    pay = forms.ChoiceField(choices=choices.PAY_CHOICES)
    time = forms.ChoiceField(choices=choices.TIME_CHOICES)
    kitchen = forms.ChoiceField(choices=choices.KITCHEN_CHOICES)
    hunger = forms.ChoiceField(choices=choices.HUNGER_CHOICES)


    class Meta:
        model = Condition
        fields = ('pay', 'time', 'kitchen', 'hunger')
