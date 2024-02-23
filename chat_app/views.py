from django.shortcuts import render
from django.conf import settings

from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from payments_app.models import Subscription
# Create your views here.

def query(request):
    plan = None
    api_key = None
    message = None

    try:
        print(request.user)
        user = Subscription.objects.get(status="AV", user=request.user)
        plan = user.status # change this to make it better
    except Subscription.DoesNotExist:
        message = "It looks like you don't have an active plan. Please purchase one below!"

    if request.method == 'POST':
        prompt = request.POST.get('prompt')

        api_key = settings.OPENAI_API_KEY

        if plan:
            try:
                user_record = Subscription.objects.get(status="AV", user=request.user)
                if user_record.queries_used + 1 > user_record.max_queries:
                    message = "Sorry, you've reached the maximum number of queries for this month, please buy a new plan."
                else:
                    # Register that the user has used one query
                    user_record.queries_used += 1
                    user_record.save()
            except Subscription.DoesNotExist:
                message = "It appears you currently have no active plans, please purchase a plan."

        if not message:
            embeddings = OpenAIEmbeddings(openai_api_key = api_key)
            db = Chroma(collection_name = request.user.username, persist_directory="chroma_db", embedding_function=embeddings)

            # expose this index in a retriever interface
            retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":1})

            # create a chain to answer questions
            qa = RetrievalQA.from_chain_type(
                llm=OpenAI(openai_api_key = api_key), chain_type="stuff", retriever=retriever, return_source_documents=True
            )

            res = qa({"query": prompt})

            return render(request, 'chat_app/chat.html', context = {"completion": res["result"]})

    context = {"plan": plan, "message": message}
    return render(request, 'chat_app/chat.html', context)


def query_old(request):
    # Check if the user has an active subscription
    try:
        user = Subscription.objects.filter(status="AV", user=request.user).first()
        plan = user.plan
    except Subscription.DoesNotExist:
        plan = None
        return render(request, 'chat_app/chat.html', context = {"plan": plan, "message": "It looks like you don't have an active plan. Please purchase one below!"})

    if request.method == 'POST':
        prompt = request.POST.get('prompt')

        try:
            api_key = APIKey.objects.get(user = request.user.username).key

        except APIKey.DoesNotExist:
            #api_key = None
            return render(request, 'chat_app/chat.html', context = {"completion": "Sorry, could not find an OpenAPI key associated with your account."})

        
        try:
            # look for an active plan for this user
            user_record = Subscription.objects.filter(status="AV").get(user=request.user.username)
            if len(user_record) > 1:
                return render(request, 'chat_app/chat.html', context = {"completion": "Sorry, something went wrong with your account."})

            # TODO check that you are under your limit
            if user_record.queries_used >= user_record.max_queries:
                return render(
                    request, 
                    'chat_app/chat.html', 
                    context = {"completion": "Sorry, you've reached the maximum number of queries for this month, please buy a new plan."}
                    )

            else:
                # register that the user has used up one query
                user_record.queries_used = queries_so_far + 1
                user_record.save()

        except Subscription.DoesNotExist:
            return render(
                request, 
                'chat_app/chat.html', 
                context = {"completion": "It appears you currently have no active plans, please purchase a plan."}
                )


        embeddings = OpenAIEmbeddings(openai_api_key = api_key)
        db = Chroma(collection_name = request.user.username, persist_directory="chroma_db", embedding_function=embeddings)

        # expose this index in a retriever interface
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":1})

        # create a chain to answer questions
        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(openai_api_key = api_key), chain_type="stuff", retriever=retriever, return_source_documents=True
        )

        res = qa({"query": prompt})

        return render(request, 'chat_app/chat.html', context = {"completion": res["result"]})
    
    return render(request, 'chat_app/chat.html')
