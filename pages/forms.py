"""Django forms for server-rendered pages."""
from django import forms
from api.models import User, Member


class BaseForm(forms.Form):
    """Base form with common styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(forms.Form):
    """
    Login form accepting email or national ID + password.
    Reuses logic from api/views.py login() endpoint.
    """
    identifier = forms.CharField(
        max_length=255,
        label='Email or National ID',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email or national ID',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        min_length=1,
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        })
    )

    def clean_identifier(self):
        """Normalize identifier: lowercase if email, uppercase if national_id."""
        identifier = self.cleaned_data.get('identifier', '').strip()
        if '@' in identifier:
            return identifier.lower()
        # Assume national_id: remove spaces, uppercase
        return identifier.replace(' ', '').upper()


class SignupForm(forms.Form):
    """
    Signup form: name, email or national_id, password.
    Reuses logic from api/serializers.py SignupSerializer.
    """
    name = forms.CharField(
        max_length=255,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autofocus': True,
        })
    )
    email = forms.EmailField(
        required=False,
        label='Email (optional if National ID provided)',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email',
        })
    )
    national_id = forms.CharField(
        required=False,
        max_length=50,
        label='National ID (optional if Email provided)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter national ID',
        })
    )
    password = forms.CharField(
        min_length=8,
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'At least 8 characters',
        })
    )
    password_confirm = forms.CharField(
        min_length=8,
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').strip().lower() if cleaned_data.get('email') else ''
        national_id = cleaned_data.get('national_id', '').replace(' ', '').upper() if cleaned_data.get('national_id') else ''
        password = cleaned_data.get('password', '')
        password_confirm = cleaned_data.get('password_confirm', '')

        # Ensure at least email or national_id provided
        if not email and not national_id:
            raise forms.ValidationError('Please provide either an email or a national ID.')

        # Check email uniqueness
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError({'email': 'Email is already registered.'})

        # Check national_id uniqueness
        if national_id and Member.objects.filter(national_id=national_id).exists():
            raise forms.ValidationError({'national_id': 'National ID is already registered.'})

        # Check password match
        if password != password_confirm:
            raise forms.ValidationError({'password_confirm': 'Passwords do not match.'})

        return cleaned_data
