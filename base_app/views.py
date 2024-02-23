from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

# We will use django's default UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.views import View

from django.shortcuts import render
from django.http import JsonResponse

from payments_app.models import Subscription


class ProfileView(View):
  def get(self, request):
    # get whether the user has an active subscription
    try:
        user = Subscription.objects.get(user = request.user, status = "AV")
        plan = user.status

        # determine the number of files and queries used
        files_used = user.files_used
        queries_used = user.queries_used

        # determine the maximum number of files and queries
        max_files = user.max_files
        max_queries = user.max_queries

        context = {'plan': plan, 'files_used': files_used, 'queries_used': queries_used, 'max_files': max_files, 'max_queries': max_queries}

    except Subscription.DoesNotExist:
        plan = None

        context = {'plan': plan}

    return render(
      request,
      "base_app/profile.html",
      context=context
    )


class IndexView(View):
  def get(self, request):
    return render(
      request,
      # render base_app/index.html and return it in the response
      "base_app/index.html",
    )

class SignUpView(View):
  def get(self, request):
    # Render giffy_app/signup.html with 
    # UserCreationForm upon page load
    return render(
      request,
      "base_app/signup.html",
      {
        "form": UserCreationForm(),
      },
    )

  def post(self, request):
    # Validate form, create user, and login 
    # upon sign-up form submission
    form = UserCreationForm(request.POST)

    # If user credentials are valid
    if form.is_valid():
      # create a new user in the database
      form.save()

      # get username and password from form
      username = form.data["username"]
      password = form.data["password1"]

      # authenticate user using credentials
      # submited in the UserCreationForm
      user = authenticate(
        request,
        username=username,
        password=password,
      )

      if user:
        # login user
        login(request, user)

      # redirect user to index page
      return redirect("/")

    # if form is not valid, re-render the template
    # showing the validation error messages
    return render(
      request,
      "base_app/signup.html",
      {
        "form": form,
      },
    )
  