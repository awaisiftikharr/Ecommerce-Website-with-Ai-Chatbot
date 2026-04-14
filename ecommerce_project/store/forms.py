from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    # Add an email field (required for shopping)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    # This function removes the messy text and adds Bootstrap style
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""  # <--- THIS HIDES THE LONG TEXT
            field.widget.attrs.update({'class': 'form-control'})