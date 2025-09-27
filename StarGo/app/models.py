from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Celebrities(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    nickName = models.CharField(max_length=100)
    groups = models.ManyToManyField('Groups', blank=True)
    imageURL = models.CharField(max_length=300, blank=True, null=True)
    addByUsers = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName} ({self.nickName})"


class Groups(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    dateStartGroup = models.DateField(blank=True, null=True)
    addByUsers = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Places(models.Model):
    name = models.CharField(max_length=100)
    googlemapLink = models.CharField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length=200)
    addByUsers = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    imageURL = models.CharField(max_length=300, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Sightings(models.Model):
    celebrities = models.ForeignKey('Celebrities', on_delete=models.CASCADE)
    places = models.ForeignKey('Places', on_delete=models.CASCADE)
    arrivalDate = models.DateField()
    addByUsers = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sighting of {self.celebrities} at {self.places} on {self.arrivalDate}"
