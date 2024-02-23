from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()

    STATUS_CHOICES = [
        ("AV", "Active"),
        ("DE", "Deactivated"),
    ]
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="AV",
    )

    subscription_id = models.CharField(max_length = 100, default = None, null=True)
    files_used = models.IntegerField(default = 0)
    queries_used = models.IntegerField(default = 0)
    max_files = models.IntegerField()
    max_queries = models.IntegerField()
