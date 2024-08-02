from django.db import models

# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=255, default="")
    scores = models.JSONField(default=dict)


    def __str__(self) -> str:
        return self.name


class Test(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.TextField(default="")
    answer = models.IntegerField(default=0)
    options = models.JSONField(default=dict)

    def __str__(self) -> str:
        return self.text
    

class Image(models.Model):
    question = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="uploads/",blank=True)

    def __str__(self) -> str:
        return f"{self.question.id}"
    

class BotUser(models.Model):
    user_name = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    user_id = models.IntegerField()
    phone_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=50, default="", blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_id}"  
    

class MainPostForBot(models.Model):
    text = models.TextField(default="")
    entities = models.JSONField(default=dict, blank=True)
    file = models.CharField(max_length=255, default="")
    file_type = models.CharField(max_length=20, blank=True)
    post_id = models.IntegerField(default=0)
    why = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return self.text[:20]
