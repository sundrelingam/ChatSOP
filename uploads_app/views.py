import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from .models import Document
from payments_app.models import Subscription
from .forms import DocumentForm
from .utils import update_vector_store
from django.contrib.auth.models import User


def upload(request):
    # Check if the user has an active subscription
    try:
        print(request.user)
        # find an active subscription for the user 
        user = Subscription.objects.get(status="AV", user=request.user)
        plan = user.status
    except:
        plan = None

    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        
        # If the current date is one month past the user's start date, reset their usage
        if user.start_date.month + 1 == datetime.now().month:
            user.files_used = 0
            user.queries_used = 0
            user.save()

        if form.is_valid():
            file_size_mb = request.FILES['docfile'].size / (1024 * 1024) # convert to mb

            
            if user.files_used + file_size_mb <= user.max_files:
                # increment their monthly usage
                user.files_used = user.files_uzed + file_size_mb
                user.save()

                newdoc = Document(docfile = request.FILES['docfile'], user = request.user)
                newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('uploads_app:upload'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'uploads_app/upload.html',
        context={'documents': documents, 'form': form, 'plan': plan}
    )


def vectorstore(request):
  if request.method == 'POST':
    # TODO really this is the one that costs money and should be rate limited
    api_key = settings.OPENAI_API_KEY

    update_vector_store(user = request.user.username, api_key = api_key)

    return HttpResponseRedirect(reverse('uploads_app:upload'))
