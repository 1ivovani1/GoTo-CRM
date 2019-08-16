from django.db import models


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


# Create your models here.
