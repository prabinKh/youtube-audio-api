# yourapp/forms.py

from django import forms
from .models import YouTubeChannel

class YouTubeChannelForm(forms.ModelForm):
    class Meta:
        model = YouTubeChannel
        fields = ['name', 'url']
