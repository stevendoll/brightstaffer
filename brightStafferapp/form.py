import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _



class RegistrationForm(forms.Form):
    #regex=r'^\w+$'
    first_name= forms.RegexField(regex=r'^[a-zA-Z]+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='First Name')), label=_("FirstName"), error_messages={ 'invalid': _("First Name value must contain only letters") })
    last_name= forms.RegexField(regex=r'^[a-zA-Z]+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='Last Name')), label=_("LastName"), error_messages={ 'invalid': _("Last Name value must contain only letters") })
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='Email')), label=_("Email"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, placeholder='Password',render=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, placeholder='Confirm Password',render=False)), label=_("Password (again)"))

    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("The Email already exists. Please try another one."))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password1')
        password_confirm = cleaned_data.get('password2')

        if password and password_confirm:
            if password != password_confirm:
                msg = "The two password fields must match."
                self.add_error('password2', msg)
        return cleaned_data

class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='Email address...')), label=_("Email"))





class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, placeholder='Password', render_value=False)), label=_("Password"))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, placeholder='Confirm Password', render_value=False)), label=_("Confirm Password"))

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='Email')),
                             label=_("Email"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, placeholder='Password', render=False)),
        label=_("Password"))
