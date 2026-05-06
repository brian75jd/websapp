from django import forms
import re
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class OrganizerCreationForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=13)
    password = forms.CharField(max_length=255)


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists. Try another one') 
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number').strip()

        if len(phone) > 13:
            raise forms.ValidationError('Phone number is too long')

        if phone.startswith('0'):
            phone = '+265' + phone[1:]

        elif phone.startswith('+265'):
            pass 

        else:
            raise forms.ValidationError("Phone must start with 0 or +265")


        pattern = r'^\+265(88|99)\d{7}$'

        if not re.match(pattern, phone):
            raise forms.ValidationError("Enter a valid Malawi phone number")


        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("Phone number already in use")
        return phone

    

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters.")

        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must include at least one number.")

        if not any(char.isalpha() for char in password):
            raise forms.ValidationError("Password must include at least one letter.")

        if password.lower() in ["password", "123456", "qwerty"]:
            raise forms.ValidationError("This password is too common.")

        return password
    


class UserCreationForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=12)
    password = forms.CharField(max_length=255)
    password2 = forms.CharField(max_length=255)

    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError('Password do not match')
        
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists. Try another one') 
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number').strip()

        if phone.startswith('0'):
            phone = '+265' + phone[1:]

        elif phone.startswith('+265'):
            pass 

        else:
            raise forms.ValidationError("Phone must start with 0 or +265")


        pattern = r'^\+265(88|99)\d{7}$'

        if not re.match(pattern, phone):
            raise forms.ValidationError("Enter a valid Malawi phone number")


        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("Phone number already in use")
        return phone

    

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters.")

        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must include at least one number.")

        if not any(char.isalpha() for char in password):
            raise forms.ValidationError("Password must include at least one letter.")

        if password.lower() in ["password", "123456", "qwerty"]:
            raise forms.ValidationError("This password is too common.")

        return password
    

class ValidateEventCreationForm(forms.Form):
    title = forms.CharField(max_length=300, required=True,
        error_messages={'required': 'This field cannot be empty'})

    description = forms.CharField(max_length=300, required=True,
        error_messages={'required': 'Description is required'})

    event_type = forms.CharField(max_length=300, required=True,
        error_messages={'required': 'Event type is required'})

    location = forms.CharField(max_length=300, required=True,
        error_messages={'required': 'Venue is required'})

    start_datetime = forms.DateTimeField(
        required=True,
        input_formats=['%Y-%m-%dT%H:%M'],
        error_messages={'required': 'Start date/time is required'}
    )

    end_datetime = forms.DateTimeField(
        required=True,
        input_formats=['%Y-%m-%dT%H:%M'],
        error_messages={'required': 'End time is required'}
    )

    vip_price = forms.IntegerField(min_value=0, required=False)
    vip_capacity = forms.IntegerField(min_value=0, required=False)
    standard_price = forms.IntegerField(min_value=0, required=False)
    standard_capacity = forms.IntegerField(min_value=0, required=False)
    regular_price = forms.IntegerField(min_value=0, required=False)
    regular_capacity = forms.IntegerField(min_value=0, required=False)

    poster = forms.ImageField(required=True,
        error_messages={'required': 'Image is required'})

    def clean(self):
        cleaned_data = super().clean()
        today = timezone.now()

        start_time = cleaned_data.get('start_datetime')
        end_time = cleaned_data.get('end_datetime')

        if start_time and end_time:
            if start_time < today or end_time < today:
                raise forms.ValidationError('Event start time cannot be in the past')

            if end_time <= start_time:
                raise forms.ValidationError('End time must be after start time')

        return cleaned_data

    def clean_poster(self):  
        poster = self.cleaned_data.get('poster')

        if not poster:
            raise forms.ValidationError('Event poster is required')

        return poster