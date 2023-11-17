import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
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

@login_required
def user_detail(request, uuid):
    user = User.objects.get(pk=uuid)
    rooms = user.rooms.all()
    return render(request, 'chat/user_detail.html', {
        'user': user,
        'rooms' : rooms
    })
    
@login_required
def user_edit(request, uuid):
    if request.user.has_perm('user.edit_user'):
        user = User.objects.get(pk=uuid)
        if request.method == 'POST':
            form = EditUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'The change was saved!')
                return redirect('/chat-admin/')
        else:
            form = EditUserForm(instance=user)
        return render(request, 'chat/edit_user.html', {
            'user': user, 
            'form': form
        })
    else:
        messages.error(request, 'You do not have access to edit users!')
        return redirect('/chat-admin/') 




@login_required  # decorator restricts access to authenticated users only
def add_user(request):  # function that accepts an HTTP request as an argument

    # Check if the authenticated user has permission to add users
    if request.user.has_perm('user.add_user'):

        # Handling POST request for form submission
        if request.method == 'POST':  # Check if the request method is POST (form submission)

            # Create a form instance with the POST data received
            form = AddUserForm(request.POST)

            if form.is_valid():  # Check if the form data is valid

                # Save the form data to a new user object without committing to the database yet
                user = form.save(commit=False)

                # Set the 'is_staff' attribute of the user object to True (indicating staff status)
                user.is_staff = True

                # Set the password for the user based on the input received in the request
                user.set_password(request.POST.get('password'))

                # Save the user object (with updated attributes) to the database
                user.save()


                # Add user to the 'Managers' group if their role is 'Manager'
                if user.role == User.MANAGER:  # Checking if the user's role is set to 'MANAGER'
                    group = Group.objects.get(name='Managers')  # Fetching the 'Managers' group from the database
                    group.user_set.add(user)  # Adding the 'user' to the 'Managers' group
                    # This associates the 'user' object with the 'Managers' group in the database.


                # Display success message and redirect to chat admin page
                messages.success(request, 'The user was added!')
                return redirect('/chat-admin/')

        else:  # Handling GET request for displaying form
            form = AddUserForm()  # creates an instance of the AddUserForm

        # Render the 'chat/add_user.html' template and pass the form instance to the template
        return render(request, 'chat/add_user.html', {
            'form': form  # dictionary containing form instance passed to the template
        })

    else:  # Redirect if the user doesn't have permission to add users
        messages.error(request, 'You do not have access to add users!')
        return redirect('/chat-admin/')

