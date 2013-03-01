# -*- coding: utf-8 -*-
from django import forms

class MugForm(forms.Form):
    mug = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )