# -*- coding: utf-8 -*-
from django import forms

class MugForm(forms.Form):
    mug = forms.FileField(
        label='Select a file',
        help_text='Max. file size: 42 MB'
    )