from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=64, widget=forms.TextInput(
        attrs={"placeholder": "Username", "class": "form-control"}
    ))
    email = forms.EmailField(max_length=128, widget=forms.EmailInput(
        attrs={"placeholder": "Email Address", "class": "form-control"}
    ))
    password = forms.CharField(min_length=6, widget=forms.PasswordInput(
        attrs={"placeholder": "Password", "class": "form-control"}
    ))
    confirmation = forms.CharField(min_length=6, widget=forms.PasswordInput(
        attrs={"placeholder": "Re-enter Password", "class": "form-control"}
    ))


class NewJobForm(forms.Form):
    job_title = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={"placeholder": "Job Title", "class": "form-control"}
    ))
    employer_name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={"placeholder": "Company Name", "class": "form-control"}
    ))
    job_location = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={"placeholder": "Country", "class": "form-control"}
    ))
    job_apply_link = forms.URLField(required=False, widget=forms.URLInput(
        attrs={"placeholder": "Job Link (optional)", "class": "form-control"}
    ))