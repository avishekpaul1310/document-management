from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Document, Category

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

class BatchUploadForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    files = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'accept': '.pdf,.doc,.docx,.txt,.xls,.xlsx'  # Add file type restrictions if needed
        }),
        help_text='Hold Ctrl/Cmd to select multiple files.',
        required=True
    )
    is_private = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_files(self):
        files = self.files.getlist('files')
        if not files:
            raise forms.ValidationError("No files were selected.")
        return files