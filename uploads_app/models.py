from django.db import models
import os
from .utils import create_path


class Document(models.Model):
    # 63 is the max length for a ChromaDB collection name
    user = models.CharField(max_length = 63)
    docfile = models.FileField(upload_to=create_path)
