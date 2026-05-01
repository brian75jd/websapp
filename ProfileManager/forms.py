from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.password_validation import validate_password
from authuser.departments import FormDepartment
import re
from datetime import date

User = get_user_model()


class Edit_ProfileForm(forms.Form):
    name = forms.CharField()
    username = forms.CharField(max_length=50)
    email = forms.EmailField(widget=forms.EmailInput)
    phone = forms.CharField(max_length=12)
    #date_of_birth = forms.DateField()
    

    def __init__(self,*args, **kwargs):
        self.current_user = kwargs.pop('current_user',None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
          name = str(name).split()
          return name
        raise forms.ValidationError('Fullname is required')
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if username:
            if " " in username:
                raise forms.ValidationError('Username can not contain spaces')
            if User.objects.filter(username__iexact = username).exists():
                if username == self.current_user.username:
                    return username
                raise forms.ValidationError('Username already exists')
            return username
        raise forms.ValidationError('username is required')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                if email == self.current_user.email:
                    return email
                raise forms.ValidationError("Email already in use")
            if not '@' and 'gmail' in email:
                raise forms.ValidationError('Invalid email address')
            return email
        raise forms.ValidationError('Email is required')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if User.objects.filter(phone_number = phone).exists():
                if phone == self.current_user.phone_number:
                    return phone
                raise forms.ValidationError('Phone number already in use')
            pattern = re.compile(r'^(\+265|0)(8[89]|9[89])\d{6,7}$')
            if not pattern.match(phone):
                raise forms.ValidationError('Enter a valid phone number')
            return phone
        raise forms.ValidationError('Phone number required')
    """
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
    """


