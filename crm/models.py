from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length = 255)
    teacher = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

class Student(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    room = models.IntegerField(null = True)
    email = models.EmailField(null = True)
    description = models.TextField(default = '')
    course = models.ForeignKey(Course, on_delete = models.SET_NULL,null = True)

    def __str__(self):
        return self.first_name + " " + self.last_name

class Token(models.Model):
    inviteToken = models.CharField(max_length = 50)

    def __str__(self):
        return self.inviteToken

class Comment(models.Model):
     author = models.ForeignKey(User, on_delete = models.SET_NULL,null = True)
     whom_comm = models.ForeignKey(Student, on_delete = models.SET_NULL,null = True)
     text = models.TextField(max_length = 1500)

     def __str__(self):
         return self.author + " -> " + self.whom_comm
