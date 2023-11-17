import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from account.models import User
from .models import Room
from account.forms import AddUserForm, EditUserForm

@require_POST
def create_room(request, uuid):
    name = request.POST.get('name', '')
    url = request.POST.get('url', '')

    Room.objects.create(uuid=uuid, client=name, url=url)

    return JsonResponse({'message': 'room created'})


@login_required
def admin(request):
    rooms = Room.objects.all()
    users = User.objects.filter(is_staff=True)

    return render(request, 'chat/admin.html', {
        'rooms': rooms,
        'users': users
    })


@login_required
def room(request, uuid):
    room = Room.objects.get(uuid=uuid)

    if room.status == Room.WAITING:
        room.status = Room.ACTIVE
        room.agent = request.user
        room.save()

    return render(request, 'chat/room.html', {
        'room': room
    })

@login_required # decorato restrict to authenticated user only
def add_user(request): #function that accepts http request as argument 
    form = AddUserForm() # creates an instance of add user form 

    return render(request, 'chat/add_user.html', { # this renders the tempate chat/add_user.html 
        'form':form # and passes dictionary containing form instance to the template 
    }) # render function is used to render the html template and return http response 