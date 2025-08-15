from django import forms
from myadmin.models import LeaveType, Employee

from django import forms
from django.core.exceptions import ValidationError


class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    empcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Employee Code')
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("New password and confirm password do not match.")


class LeaveForm(forms.Form):
    leavetype = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        label="Leave Type",
        empty_label=None,
        widget=forms.Select(attrs={'class':'form-control'})
    )
    fromdate    = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    todate      = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))  

    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['firstName', 'lastName','gender', 'address', 'city', 'country', 'mobileno']