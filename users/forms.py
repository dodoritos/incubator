from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate

from django import forms
from .models import User


class BalanceForm(forms.Form):
    value = forms.DecimalField(max_digits=6, decimal_places=2)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'newsletter']


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification.")
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def auth_user(self):
        user = authenticate(
            username=self.cleaned_data.get("username"),
            password=self.cleaned_data.get("password1"),
        )

        return user
