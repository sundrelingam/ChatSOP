from django.shortcuts import render, redirect
from .models import Subscription
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views import View

import stripe


# Create your views here.

class PlanView(View):
  def get(self, request):
    print(settings.STRIPE_PUBLISHABLE_KEY)
    user = request.user
    try:
        plan = Subscription.objects.get(user = user, status = "AV")
        plan = plan.status # change this to make it better
    except Subscription.DoesNotExist:
        plan = None

    return render(
      request,
      "payments_app/plan.html",
      context={"plan": plan}
    )


def set_api_key(request):
    print('worked')
    if request.method == 'POST':
        key = request.POST.get('key')
        form = APIKeyForm(request.POST, key)

        if form.is_valid():
            newkey = APIKey(user = request.user, key = key)
            newkey.save()

            return redirect('payments_app:plan')

    else:
        form = APIKeyForm()

    try:
        api_key = APIKey.objects.get(user = request.user).key

    except APIKey.DoesNotExist:
        api_key = None

    # check whether user has an active plan
    try:
        plan = Subscription.objects.get(user = request.user, status = "AV").plan

    except Subscription.DoesNotExist:
        plan = None

    except Subscription.MultipleObjectsReturned:
        # if there are multiple active plans, deactivate all but the first one
        plans = Subscription.objects.filter(user = request.user, status = "AV")
        for plan in plans[1:]:
            plan.status = "DE"
            plan.save()
        plan = None

    return render(request, 'payments_app/plan.html', context = {"form": form, "api_key": api_key, "plan": plan})


# Stripe views
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = settings.DOMAIN_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': 'price_1O7q7hImgTZanQyiJIZDHot8',
                        'quantity': 1,
                    },
                ],
                subscription_data={
                    'trial_period_days': 30,
                    },
            )
            return JsonResponse({'sessionId': checkout_session['id']})
            
        except Exception as e:
            return JsonResponse({'error': str(e)})


class SuccessView(TemplateView):
    template_name = 'payments_app/success.html'


class CancelledView(TemplateView):
    template_name = 'payments_app/cancelled.html'


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    # Stripe CLI setup + login
    # The easiest way to test our webhook is to download Stripe CLI (https://stripe.com/docs/stripe-cli)
    # After downloading it we need to login by running 'stripe login' in Terminal, this command will generate
    # a pairing code for us an open our web browser.
    #
    # ---------------------------------------------------------------
    # Your pairing code is: word1-word2-word3-word4
    # This pairing code verifies your authentication with Stripe.
    # Press Enter to open the browser (^C to quit)
    # ---------------------------------------------------------------
    #
    # By pressing enter CLI opens our browser and asks us if we want to allow Stripe CLI to access our account
    # information. We can allow it by clicking 'Allow access' button and confirming the action with our password.
    #
    # If everything goes well Stripe CLI will display the following message:
    #
    # ---------------------------------------------------------------
    # > Done! The Stripe CLI is configured for {ACCOUNT_NAME} with account id acct_{ACCOUNT_ID}
    # Please note: this key will expire after 90 days, at which point you'll need to re-authenticate.
    # ---------------------------------------------------------------
    #
    # Webhook setup
    # Once we successfully logged in we can start listening to Stripe events and forward them to our webhook using
    # the following command:
    #
    # stripe listen --forward-to localhost:8000/webhook/
    #
    # This will generate a webhook signing secret that we should save in our settings.py. After that we will
    # need to pass it when constructing a Webhook event.
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # Handle the checkout.session.completed event

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # This method will be called when user successfully purchases something.
        handle_checkout_session(session)

    return HttpResponse(status=200)


def handle_checkout_session(session):
    # client_reference_id = user's id
    client_reference_id = session.get("client_reference_id")
    payment_intent = session.get("payment_intent")
    subscription_id = session.get("subscription")

    if client_reference_id is None:
        # Customer wasn't logged in when purchasing
        return

    # Customer was logged in we can now fetch the Django user and make changes to our models
    try:
        user = User.objects.get(pk=client_reference_id)

        # TODO: make changes to our models.
        new_plan = Subscription(
            user = user,
            status = "AV",
            subscription_id = subscription_id,
            start_date = timezone.now(),
            max_files = 100,
            max_queries = 1000
            )
            
        new_plan.save()
    
    except User.DoesNotExist:
        # TODO: Give an error page
        pass


@csrf_exempt
def cancel_subscription(request):
    if request.method == 'POST':
        try:
            user = Subscription.objects.get(user = request.user, status = "AV")
            subscription_id = user.subscription_id

            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.delete(subscription_id)

            user.subscription_id = None
            user.status = "DE"
            user.save()

            return redirect('payments_app:success') # TODO sorry to see you go page
            
        except Subscription.DoesNotExist:
            return redirect("base_app/plan.html") # change this to an error page?
