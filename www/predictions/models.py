from django.db import models

class CommonInfo(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

#where this function should be?
def is_numeric(str):
    try:
        float(str)
    except ValueError:
        return False
    else:
        return True