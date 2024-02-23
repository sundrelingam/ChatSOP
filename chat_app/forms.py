from django import forms

class ChatForm(forms.Form):
    message = forms.CharField(
        label='Enter your message',
        max_length=1000,
        help_text='max. 1000 characters'
    )
