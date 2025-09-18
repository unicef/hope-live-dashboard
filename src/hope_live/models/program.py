from django.db import models

from .base import BaseModel
from .office import Office


class Program(BaseModel):
    hope_id = models.CharField(max_length=200, unique=True, editable=False)
    country_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=10, db_index=True)
    sector = models.CharField(max_length=50, db_index=True)
