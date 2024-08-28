from django.db import models

# Create your models here.
class SubjectBranch(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Subject(models.Model):
    branch_name = models.ForeignKey(SubjectBranch, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255, default="")
    scores = models.JSONField(default=dict)
    count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)


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
    

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    description_entities = models.JSONField(default=dict, blank=True)
    file = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=False)
    teachers = models.TextField(blank=True)
    teachers_entities = models.JSONField(default=dict, blank=True)



    def __str__(self) -> str:
        return self.name
    

class AvailableCourse(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    description_entities = models.JSONField(default=dict, blank=True)
    file = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=10, blank=True)
    students = models.JSONField(default=dict, blank=True)
    students_count = models.IntegerField(default=0, blank=True)
    start_date = models.DateField(default=None, blank=True)
    date = models.TextField(max_length=255, blank=True)
    status = models.CharField(max_length=20, blank=True)
    teacher = models.TextField(blank=True)
    teacher_entitie = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name
    

class TgGroup(models.Model):
    name = models.CharField(max_length=255)
    group_id = models.IntegerField(blank=True)
    group_link = models.CharField(max_length=255, blank=True)
    group_for = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
    

class ForwardMessage(models.Model):
    message_id = models.IntegerField(blank=True)
    forwarded_message_id = models.IntegerField(blank=True)
    user_id = models.IntegerField(blank=True)
    date = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.message_id}"
