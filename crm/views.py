from django.shortcuts import render,redirect
from django.contrib import messages
from crm.models import Student,Course,Token,Comment
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django import forms
from django.http import HttpResponse

class RegisterValidation(forms.Form):
    login = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(min_length=6)

class LoginValidation(forms.Form):
    login = forms.CharField(max_length=30)
    password = forms.CharField(min_length=6)

#register
def logout_page(request):
    logout(request)
    return redirect('/login')
def login_page(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        form = LoginValidation(request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, 'Данные неверны!')
            return redirect('/login')

        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.add_message(request, messages.ERROR, 'Данные неверны!')
            return redirect('/login')
        else:
            login(request, user)
            return redirect('/')
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        form = RegisterValidation(request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, 'Минимальная длина пароля - 6 символов!')
            return redirect('/register')

        userToken = request.POST.get('inviteToken','')
        if Token.objects.filter(inviteToken = userToken).exists():
            user = User()
            user.username = request.POST.get('login')
            user.email = request.POST.get('email')
            user.set_password(request.POST.get('password'))
            user.save()

            login(request, user)

            return redirect('/')

        else:
            messages.add_message(request, messages.ERROR, 'Неверный инвайт код')
            return redirect('/register')

#main work
def index(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    students = Student.objects.all()
    return render(request,"index.html",{"students":students})
def details(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        id = request.GET.get('id')
        user = request.user
        student = Student.objects.get(pk = id)
        comments = Comment.objects.all()

        return render(request,'details.html',{"student":student,'user':user,'comments':comments})
    if request.method == 'POST':
        comment_text = request.POST.get('text','')
        id = request.GET.get('id')
        student = Student.objects.get(pk = id)

        if comment_text == '':
            messages.add_message(request, messages.ERROR, 'Ваш комментарий пустой!')
            return redirect('/student?id={}'.format(student.id))

        comment = Comment()
        comment.text = comment_text
        comment.author = request.user
        comment.whom_comm = student

        comment.save()
        return redirect('/student?id={}'.format(student.id))
def add(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':

        courses = Course.objects.all()
        return render(request,'add.html',{'courses':courses})
    if request.method == "POST":
        first_name = request.POST.get("first_name", '')
        last_name = request.POST.get("last_name", '')
        course_id = request.POST.get('course_id','')
        room = request.POST.get('room','')
        email = request.POST.get('email','')
        description = request.POST.get('description','')

        if first_name == '' or last_name == '' or room == '' or course_id == '' or email == '' or description == '':
            messages.add_message(request, messages.ERROR, 'Заполните все поля!')
            return redirect('/add')

        student = Student()
        student.first_name = first_name
        student.last_name = last_name
        student.room = room
        student.email = email
        student.description = description

        if course_id != '':
            course = Course.objects.get(pk=course_id)
            student.course = course
        else:
            student.course = None
        student.save()

        return redirect('/student?id={}'.format(student.id))
def courseAdd(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        return render(request,'course-add.html')
    if request.method == 'POST':
        name = request.POST.get('name')
        teacher = request.POST.get('teacher')

        course = Course()
        course.name = name
        course.teacher = teacher
        course.save()
    return redirect('/course-descript?id={}'.format(course.id))
def courseDescript(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    course = Course.objects.get(pk=id)
    students = Student.objects.filter(course = course).all()
    return render(request,'course-descript.html',{'course':course,'students':students})
def courseEdit(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    if request.method == 'GET':
        course = Course.objects.get(pk = id)
        return render(request,'course-edit.html',{"course":course})
    if request.method == 'POST':
        name = request.POST.get('name','')
        teacher = request.POST.get('teacher','')

        course = Course.objects.get(pk = id)
        course.name = name
        course.teacher = teacher
        course.save()
        return redirect('/course-descript?id={}'.format(id))
def deleteCourse(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    course = Course.objects.get(pk = id)
    course.delete()
    return redirect('/course-list')
def edit(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        courses = Course.objects.all()
        id = request.GET.get('id')
        student = Student.objects.get(pk = id)
        return render(request,'change.html',{"student":student,'courses':courses})

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/login')
        first_name = request.POST.get("first_name",'')
        last_name = request.POST.get("last_name",'')
        course_id = request.POST.get('course_id','')
        room = request.POST.get('room','')
        email = request.POST.get('email','')
        description = request.POST.get('description','')


        if first_name == '' or last_name == '':
            return HttpResponse('Заполните все поля')


        id = request.GET.get('id')
        student = Student.objects.get(pk = id)
        student.first_name = first_name
        student.last_name = last_name
        student.room = room
        student.email = email
        student.description = description

        if course_id != '':
            course = Course.objects.get(pk=course_id)
            student.course = course
        else:
            student.course = None
        student.save()

        return redirect('/student?id={}'.format(student.id))
def delete(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    student = Student.objects.get(pk = id)
    student.delete()

    return redirect('/')
def deleteAll(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    students = Student.objects.all()
    students.delete()

    return redirect('/')
def showCourses(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    courses = Course.objects.all()
    return render(request,'course-list.html',{"courseList":courses})
def courseInfo(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    course = Course.objects.get(pk = id)
    return render(request,'course-descript.html',{"course":course})
