from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Celebrities(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    groups = models.ManyToManyField('Groups', blank=True)
    imageurl = models.FileField(upload_to='images/', blank=True, null=True) # * ถ้า upload_to='' จะไปเก็บใน media เลย
    addby_users = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.nickname})"


class Groups(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    datestartgroup = models.DateField(blank=True, null=True)
    addby_users = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Places(models.Model):
    name = models.CharField(max_length=100)
    googlemaplink = models.CharField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length=200)
    addby_users = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    imageurl = models.FileField(upload_to='images/', blank=True, null=True) # * ถ้า upload_to='' จะไปเก็บใน media เลย
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Sightings(models.Model):
    celebrities = models.ForeignKey('Celebrities', on_delete=models.CASCADE)
    places = models.ForeignKey('Places', on_delete=models.CASCADE)
    arrivaldate = models.DateField()
    addby_users = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sighting of {self.celebrities} at {self.places} on {self.arrivaldate}"
