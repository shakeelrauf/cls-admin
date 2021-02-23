from django import forms
import pdb
from dashboard.models import Sheet

class GetYearData(forms.Form):
    def __init__(self,*args,**kwargs):
        choices = kwargs.pop('choices')
        super(GetYearData,self).__init__(*args,**kwargs)
        CHOICES = []
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        for choice in choices: 
            CHOICES.append((choice, choice))
        self.fields['years'].choices = CHOICES
    years = forms.ChoiceField(required=True, choices=[],label ="Select Year to see yearly data")
