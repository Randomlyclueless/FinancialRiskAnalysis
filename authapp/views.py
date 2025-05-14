from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect after successful login
        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')

    return render(request, 'authapp/login.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Signup failed. Please check the form and try again.')
    else:
        form = UserCreationForm()

    return render(request, 'authapp/signup.html', {'form': form})
