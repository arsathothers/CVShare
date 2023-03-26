from django import forms
from django.core.validators import FileExtensionValidator

def token_validation(value):
    if len(value) != 16:
        raise forms.ValidationError("Token should be 16 characters.")

class mail_datas(forms.Form):
    # from below we have added widgets to make a placeholder and removing label from form
    email = forms.EmailField(widget=forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-control'
                }), label='')
    token = forms.CharField(validators=[token_validation],
                            widget=forms.TextInput(attrs={
                'placeholder': 'Token',
                'class': 'form-control'
                }), label='')
    subject = forms.CharField(widget=forms.TextInput(attrs={
                'placeholder': 'Subject',
                'class': 'form-control'
                }), label='')
    message = forms.CharField(widget=forms.Textarea(attrs={
                'placeholder': 'Body of the mail',
                'class': 'form-control'
                }), label='')
    user_file = forms.FileField(widget=forms.ClearableFileInput(), label='Excel upload', validators=[FileExtensionValidator( ['xlsx'] ) ])
    resume_file = forms.FileField(widget=forms.ClearableFileInput(), label='Resume', validators=[FileExtensionValidator( ['pdf', 'docs', 'odt'] ) ])

    def clean(self):
        all_clean_data = super().clean()
        return all_clean_data
