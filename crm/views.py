from django.shortcuts import render,redirect
from django.contrib import messages
from crm.models import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import Group
from django import forms
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
import random
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail

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
            dbToken = Token.objects.filter(inviteToken = userToken).first()
            if CustomUser.objects.filter(username = request.POST.get('login')).exists():
                messages.add_message(request, messages.ERROR, 'Пользователь с таким именем уже существует!')
                return redirect('/register')
            else:
                user = CustomUser()
                user.tg_login = request.POST.get('tg_login')
                user.username = request.POST.get('login')
                user.email = request.POST.get('email')
                user.set_password(request.POST.get('password'))
                user.save()

                if dbToken.isAdmin == True:
                    group = Group.objects.filter(name='Admin').first()
                    user.groups.add(group)
                else:
                    group = Group.objects.filter(name='Teacher').first()
                    user.groups.add(group)

                login(request, user)
                return redirect('/')

        else:
            messages.add_message(request, messages.ERROR, 'Неверный инвайт код')
            return redirect('/register')

def passReset(request):
    if request.method == 'GET':
       return render(request,'pass-reset.html')

    if request.method == 'POST':
        if CustomUser.objects.filter(username = request.POST.get('login')).exists():
            users = CustomUser.objects.all()
            for user in users:
                if user.username == request.POST.get('login'):
                    chars = '+-/abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
                    password = ''
                    length = random.randint(10,15)
                    for i in range(length):
                        password += random.choice(chars)
                    email = user.email
                    name = user.username
                    user.set_password(password)
                    user.save()
                    html_message = render_to_string('email.html',{'name':name,'password':password})
                    plain_message = strip_tags(html_message)
                    mail.send_mail('Восстановление пароля',plain_message,settings.EMAIL_HOST_USER, [email],html_message=html_message)
                    return redirect('/success-send')

        else:
           messages.add_message(request, messages.ERROR, 'Пользователя с таким именем не существует!')
           return redirect('/password-reset')

def sucessRender(request):
    return render(request,'sucess-send.html')

shiftNow = {}

def shiftFinish(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        id = request.GET.get('id')
        shift = Shift.objects.get(pk=int(id))
        students = Student.objects.filter(shift = shift)

        return render(request,'shift-finish.html',{'students':students,'shift':shiftNow["shift_name"]})
    if request.method == 'POST':
        id = request.GET.get('id')
        shift = Shift.objects.get(pk=int(id))
        shift.is_finished = True
        shift.save()
        students = Student.objects.filter(shift = shift)

        for i in students:
            mark = request.POST.get(f'mark{i.id}','')
            i.mark = mark
            i.save()



        return redirect('/')

#main work
def index(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        id = request.GET.get('id')
        shift = Shift.objects.get(pk=int(id))
        students = Student.objects.filter(shift = shift)

        shift_status = students[0].mark == None

        shiftNow["shift_name"] = shift

        return render(request,"index.html",{'students':students,'shift':shiftNow["shift_name"],'shift_status':shift_status})


def addShift(request):
    if request.method == 'GET':
        return render(request,'add-shift.html')
    if request.method == 'POST':
        shift = Shift()
        if Shift.objects.filter(name_shift=request.POST.get('name_shift')).exists():
            return HttpResponse('Такая смена уже была,не стоит повторять это снова')
        else:
            shift.name_shift = request.POST.get('name_shift')
            shift.save()

            allStudents = request.POST.get('pupils')
            student = allStudents.split('\n')


            for i in student:
                part = i.split(' ')
                is_been = False
                if Student.objects.filter(first_name = part[0],last_name = part[1]).exists():
                    is_been = True
                student = Student()
                student.first_name = part[0]
                student.last_name = part[1]
                student.room = part[2]
                student.shift = shift
                student.is_been = is_been

                student.save()


            return redirect(f'/shift?id={shift.id}')

def showShifts(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    shifts = Shift.objects.all()
    return render(request,'shift-list.html',{"shifts":shifts})



def details(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        id = request.GET.get('id')
        user = request.user
        student = Student.objects.get(pk = id)
        comments = Comment.objects.filter(whom_comm = id).order_by('-id')
        return render(request,'details.html',{"student":student,'user':user,'comments':comments,'shift':shiftNow['shift_name']})

    if request.method == 'POST':

        comment_text = request.POST.get('text','')
        id = request.GET.get('id')
        student = Student.objects.get(pk = id)
        comment_status = request.POST.get('status')


        if comment_text == '':
            messages.add_message(request, messages.ERROR, 'Ваш комментарий пустой!')
            return redirect('/student?id={}'.format(student.id))



        comment = Comment()
        comment.status = False
        if comment_status == "on":
            comment.status = True
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
        return render(request,'add.html',{'courses':courses,'shift':shiftNow['shift_name']})

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
        student.avatar = request.FILES['avatar']


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
        return render(request,'course-add.html',{'shift':shiftNow['shift_name']})

    if request.method == 'POST':
        name = request.POST.get('name')
        teacher = request.POST.get('teacher')

        course = Course()
        course.name = name
        course.teacher = teacher
        course.shift = shiftNow['shift_name']
        course.save()
        return redirect('/course-descript?id={}'.format(course.id))

def courseDescript(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    isAdmin = False
    if request.user.groups.filter(name='Admin').exists():
        isAdmin = True
    id = request.GET.get('id')
    course = Course.objects.get(pk=id)
    students = Student.objects.filter(course = course).all()
    return render(request,'course-descript.html',{'course':course,'students':students,'isAdmin':isAdmin,'shift':shiftNow['shift_name']})

def courseEdit(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    if request.method == 'GET':
        if request.user.groups.filter(name='Admin').exists():
            course = Course.objects.get(pk = id)
            return render(request,'course-edit.html',{"course":course,'shift':shiftNow['shift_name']})
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
    if request.user.groups.filter(name='Admin').exists():
        id = request.GET.get('id')
        course = Course.objects.get(pk = id)
        course.delete()
        return redirect('/course-list')

def edit(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':

        courses = Course.objects.filter(shift=shiftNow['shift_name'])
        id = request.GET.get('id')
        student = Student.objects.get(pk = id)
        return render(request,'change.html',{"student":student,'courses':courses,'shift':shiftNow['shift_name']})

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
        if 'avatar' in request.FILES:
            student.avatar = request.FILES['avatar']

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

    isAdmin = False
    if request.user.groups.filter(name='Admin').exists():
        isAdmin = True
    id = request.GET.get('id')
    shift = Shift.objects.get(pk=int(id))
    courses = Course.objects.filter(shift = shift)


    return render(request,'course-list.html',{"courseList":courses,'isAdmin':isAdmin,'shift':shiftNow['shift_name']})

def courseInfo(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    isAdmin = False
    course = Course.objects.get(pk = id)
    if request.user.groups.filter(name='Admin').exists():
        isAdmin = True
    return render(request,'course-descript.html',{"course":course,'isAdmin':isAdmin,'shift':shiftNow['shift_name']})
