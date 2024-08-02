from django import forms
from .models import Test, Image

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['text', 'answer', 'options']

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']