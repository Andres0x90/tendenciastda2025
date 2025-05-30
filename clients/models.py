from django.db import models

# Create your models here.

class Client(models.Model):
    document = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'clients'

    def to_dict(self):
        return {
            'document': self.document,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }