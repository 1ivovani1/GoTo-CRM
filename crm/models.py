from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    tg_login = models.CharField(max_length = 50,null=True)

class Shift(models.Model):
    name_shift = models.CharField(max_length=50)
    is_finished = models.BooleanField(default=False)
    def __str__(self):
        return self.name_shift

class Course(models.Model):
    name = models.CharField(max_length = 255,null=True)
    teacher = models.CharField(max_length = 100,null=True)
    shift = models.ForeignKey('Shift',on_delete = models.SET_NULL,null = True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Participation(models.Model):
    student = models.ForeignKey('Student',null=True, on_delete=models.CASCADE)
    course = models.ForeignKey('Course',null = True, on_delete=models.CASCADE)
    mark = models.IntegerField(null=True)

class Student(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    room = models.IntegerField(null = True)
    email = models.EmailField(null = True,default='None')
    description = models.TextField(default = '')
    course = models.ManyToManyField(Course,null = True,through='Participation')
    avatar = models.FileField(upload_to='media/avatars',default='media/avatars/logo.jpg',null=True)
    shift = models.ManyToManyField('Shift',null = True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def current_course(self):
        return self.course.filter(is_finished=False).first()


class Token(models.Model):
    inviteToken = models.CharField(max_length = 50)
    isAdmin = models.BooleanField(default=False)

    def __str__(self):
        return self.inviteToken

class Comment(models.Model):
     author = models.ForeignKey(CustomUser, on_delete = models.SET_NULL,null = True)
     whom_comm = models.ForeignKey(Student, on_delete = models.SET_NULL,null = True)
     text = models.TextField(max_length = 1500)
     status = models.BooleanField(default=False)

     # def __str__(self):
     #     return self.author.username + " -> " + self.whom_comm.first_name + " " + self.whom_comm.last_name
