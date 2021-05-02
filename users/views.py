from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignupForm


def signup(request):
    """
    Used during user registration
    """
    if request.method == "POST":
        form = SignupForm(request.POST)  # Init SignupForm with POST request
        if form.is_valid():
            form.save()  # Save form informations in User model
            username = request.POST['username']  # Gets Username
            password = request.POST['password1']  # Gets Password

            # Authenticate user with username & password
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect("/")  # Index redirection
    else:
        form = SignupForm()  # Init an Empty form

    return render(request, 'users/signup.html', {"form": form})


def user_account(request):
    """
    Used for user account page
    """
    return render(request, 'users/user_account.html')
