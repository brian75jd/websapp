from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login,authenticate
import json
from django.contrib.auth import get_user_model
from events.forms import OrganizerCreationForm
from events.forms import UserCreationForm
from events.utils import check_phone_Number
from django.urls import reverse


User = get_user_model()

@require_POST
def CreateOrganizer(request):
    try:
        data = json.loads(request.body)
        form = OrganizerCreationForm(data)
       
        if not form.is_valid():
            errors = []

            for field, field_errors in form.errors.get_json_data().items():
                for err in field_errors:
                    errors.append(err['message'])

            return JsonResponse({'detail': errors}, status=400)

        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        password = form.cleaned_data.get('password')

        user =  User.objects.create_user(
            username= email,
            name = name,
            phone_number =phone_number,
            email=email,
            password = password,
            is_organizer = True,
        )
        login(request,user)
        return JsonResponse({
            'detail':'Organizer created',
            'url':'/dashboard/',
            'success':True
            },status=200)
    except Exception as exp:
        return JsonResponse({'detail':str(exp)},status=400)


def CreateUser(request):
    try:
        data = json.loads(request.body)
        form = UserCreationForm(data)
        if not form.is_valid():
            errors = []
            for field, field_errors in form.errors.get_json_data().items():
                for err in field_errors:
                    errors.append(err['message'])
            return JsonResponse({'detail': errors}, status=400)
        
        username = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        phone_number = form.cleaned_data.get('phone_number')
        user = User.objects.create(
            username = username,
            email = email if email else " ",
            phone_number = phone_number,
            password = password
        )

        return JsonResponse({"success":True,'detail':'user Created'},status = 200)
    except Exception as exp:
        return JsonResponse({'detail':str(exp)},status = 400)



def LogginCredential(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'detail': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)

        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            return JsonResponse({'success': False, 'detail': 'All fields are required'}, status=400)

    
        user = authenticate(username=identifier, password=password)

        if user is None:
            phone = check_phone_Number(identifier)

            try:
                user_obj = User.objects.get(phone_number=phone)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'detail': 'User not found'}, status=400)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'url': '/dashboard/' if user.is_organizer else "/"
            })
            

        return JsonResponse({'success': False, 'detail': 'Invalid credentials'}, status=400)

    except Exception as e:
        print("LOGIN ERROR:", e)
        return JsonResponse({'success': False, 'detail': 'Something went wrong'}, status=500)