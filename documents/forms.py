from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Document, Category
from django.forms.widgets import FileInput

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'category', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class MultipleFileInput(FileInput):
    def __init__(self, attrs=None):
        default_attrs = {'multiple': 'multiple'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class BatchUploadForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Category'
    )
    files = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.txt,.xls,.xlsx'
        }),
        help_text='Hold Ctrl/Cmd to select multiple files.',
        label='Select Files'
    )
    is_private = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Make Private'
    )