from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.password_validation import validate_password
from authuser.departments import FormDepartment
import re
from datetime import date

User = get_user_model()

class OTP_Class(forms.Form):
    otp = forms.CharField(max_length=6)

    def clean(self):
        cleaned_data = super().clean()
        otp = cleaned_data.get('otp')
        if not otp:
            raise forms.ValidationError('OTP is required')
        return cleaned_data

class UserRegistrationPhaseOne(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField(max_length=50)
    email = forms.EmailField(widget=forms.EmailInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 =cleaned_data.get('password2')

        if p1 and p1 and p1 != p2:
            self.add_error('password2','Passwords do not match')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if " " in first_name:
            raise forms.ValidationError('First name can not contain spaces')
        return first_name
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if " " in username:
            raise forms.ValidationError('Username can not contain spaces')
        if User.objects.filter(username__iexact = username).exists():
            raise forms.ValidationError('Username already exists')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        return email
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password

class UserRegistrationPhaseTwo(forms.Form):
    phone_number = forms.CharField()
    date_of_birth = forms.DateField()
    department = forms.CharField(max_length=50)
    gender = forms.ChoiceField(choices=[
        ('male','male'),
        ('female','female'),
    ])
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number = phone_number).exists():
            raise forms.ValidationError('Phone number already in use')
        pattern = re.compile(r'^(\+265|0)(8[89]|9[89])\d{6,7}$')
        if not pattern.match(phone_number):
            raise forms.ValidationError('Enter a valid phone number')
        return phone_number
    
    def clean_date_of_birth(self):
        today = date.today()
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth >= today:
            raise forms.ValidationError('Date of birth can not be in future')
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        
        if age < 13:
            raise forms.ValidationError('You must be at least 13 years old')
        if age>100:
            raise forms.ValidationError('Please enter a valid date')
        
        return date_of_birth

class LogginUser(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username =="":
            raise forms.ValidationError('username is required')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password =="":
            raise forms.ValidationError('password is required')
        return password
