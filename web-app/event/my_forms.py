from django import forms
from django.forms import ModelForm, Form, fields, ValidationError
from django.forms import widgets as wd

from event import models


class CreateEventForm(ModelForm):

    class Meta:
        model = models.Event
        fields=(
            'event_name',
            'event_time',
        )
        widget = {
            "evevt_time":wd.SelectDateWidget(),
        }


class QuestionnaireForm(ModelForm):


    class Meta:
        model = models.Questionnaire
        fields = '__all__'
        error_messages = {
            "event_name": {"required": 'Input!'},
            "classroom": {"required": 'Input!'},
        }
        widgets = {
            "title": wd.TextInput(attrs={"class": 'form-control', "aria-describedby": 'help-title'}),
            "classroom": wd.Select(attrs={"class": 'form-control', "aria-describedby": 'help-classroom'}),
        }


class QuestionForm(ModelForm):

    class Meta:
        model = models.Question
        fields = ['id', 'title', 'type', 'vendor_view', 'finalized']

        widgets = {
            "title": wd.TextInput(attrs={"class": 'form-control'}),
            "type": wd.Select(attrs={"class": 'form-control'}),
        }


class OptionForm(ModelForm):

    class Meta:
        model = models.Option
        fields = ['content']
        widgets = {
            "content": wd.TextInput(attrs={"class": 'form-control'}),
        }


class MaxValueForm(ModelForm):

    class Meta:
        model = models.MaxValue
        fields = ['max_value']


class AnswerForm(ModelForm):
    class Meta:
        model = models.Answer
        fields = ['id', 'question', 'guest', 'value', 'option', 'content']

        widgets = {
            "value": wd.NumberInput(attrs={"class": 'form-control'}),
            "content": wd.Textarea(),
        }


class ChoiceForm(Form):

    def __init__(self, foo_choices, *args, **kwargs):
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choice'].choices = foo_choices

    choice = forms.ChoiceField(choices=(), required=True)

