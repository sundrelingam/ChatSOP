# import settings
from django.conf import settings

import os
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


def update_vector_store(user, api_key):
    # load all documents
    loader = PyPDFDirectoryLoader(os.path.join('documents', user))
    documents = loader.load()

    # split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    # select which embeddings we want to use
    embeddings = OpenAIEmbeddings(openai_api_key = api_key)

    # create the vectorstore to use as the index
    db = Chroma.from_documents(texts, embeddings, persist_directory='chroma_db', collection_name = user)


def create_path(instance, filename):
    return os.path.join(
        'documents',
        instance.user.username,
        filename
    )
