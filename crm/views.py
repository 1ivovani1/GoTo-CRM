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
from django.template.defaulttags import register
from django.db.models import Q



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

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

shiftNow = {"shift_name":Shift.objects.filter(is_finished=False).first()}

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

        return redirect('/')

#main work
def index(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        id = request.GET.get('id')
        shift = Shift.objects.get(pk=int(id))
        shiftNow["shift_name"] = shift
        students = Student.objects.filter(shift = shift)

        courses = Course.objects.filter(shift = shiftNow['shift_name'],is_finished=False)

        return render(request,"index.html",{'students':students,'shift':shiftNow["shift_name"],"courses":courses})

    if request.method == 'POST':
        id = request.GET.get('id')
        shift = Shift.objects.get(pk=int(id))
        shiftNow["shift_name"] = shift
        students = Student.objects.filter(shift = shift)

        for student in students:
            course_id = int(request.POST.get(f'course_id{student.id}',''))
            if course_id != '':
                active = student.current_course
                if active != None:
                    student.course.remove(active)
                if course_id != -1:
                    new = Course.objects.get(pk=int(course_id))
                    student.course.add(new)

        return redirect(f'/shift?id={shift.id}')


def addShift(request):
    if request.method == 'GET':
        return render(request,'add-shift.html')
    if request.method == 'POST':
        shift = Shift()
        if Shift.objects.filter(name_shift=request.POST.get('name_shift')).exists():
            return HttpResponse('Такая смена уже была, не стоит повторять это снова')
        else:
            shift.name_shift = request.POST.get('name_shift')
            shift.save()

            allStudents = request.POST.get('pupils')
            student = allStudents.split('\n')


            for i in student:
                part = i.split(' ')
                if not Student.objects.filter(first_name = part[0],last_name = part[1]).exists():
                    student = Student()
                    student.first_name = part[0]
                    student.last_name = part[1]
                else:
                    student = Student.objects.filter(first_name = part[0],last_name = part[1]).first()

                if len(part) == 3:
                    student.room = part[2]

                student.save()
                student.shift.add(shift)
            return redirect(f'/shift?id={shift.id}')

def showShifts(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    activeShifts = False
    if Shift.objects.filter(is_finished=False).exists():
        activeShifts = True
    else:
        activeShifts = False
    finishedShifts = Shift.objects.filter(is_finished=True)
    unFinishedShifts = Shift.objects.filter(is_finished=False)
    return render(request,'shift-list.html',{"finishedShifts":finishedShifts,'unFinishedShifts':unFinishedShifts,'activeShifts':activeShifts})



def details(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        id = request.GET.get('id')
        user = request.user
        student = Student.objects.get(pk = id)
        participation = Participation.objects.filter(student=student).order_by('-id')



        comments = Comment.objects.filter(whom_comm = id).order_by('-id')
        return render(request,'details.html',{"student":student,'user':user,'comments':comments,'shift':shiftNow['shift_name'],'participation':participation})

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
        courses = Course.objects.filter(shift = shiftNow['shift_name'],is_finished = False)
        return render(request,'add.html',{'courses':courses,'shift':shiftNow['shift_name']})

    if request.method == "POST":
        first_name = request.POST.get("first_name", '')
        last_name = request.POST.get("last_name", '')
        course_id = request.POST.get('course_id','')
        room = request.POST.get('room','')
        email = request.POST.get('email','')
        description = request.POST.get('description','')

        student = Student()
        student.first_name = first_name
        student.last_name = last_name
        student.room = room
        student.email = email
        student.description = description
        if 'avatar' in request.FILES:
            student.avatar = request.FILES['avatar']
        student.save()

        student.shift.add(shiftNow['shift_name'])

        if course_id != '':
            studentCourse = Course.objects.get(pk=int(course_id),is_finished=False)
            student.course.add(studentCourse)


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
    if request.method == 'GET':
        id = request.GET.get('id')
        course = Course.objects.get(pk=id)
        students = Student.objects.filter(course = course).all()

        noCourseStudents = Student.objects.filter(~Q(course = course),shift=shiftNow['shift_name'])

        markDict = {}

        for student in students:
            participation = Participation.objects.filter(course=course, student=student).first()
            mark = participation.mark
            markDict[student.id] = mark

        return render(request,'course-descript.html',{'course':course,'students':students,'noCourseStudents':noCourseStudents,'shift':shiftNow['shift_name'],'markDict':markDict})

    if request.method == 'POST':
        if request.POST.get('send_marks') == 'marks':
            id = request.GET.get('id')
            course = Course.objects.get(pk=id,is_finished=False)
            students = course.student_set.all()
            course.is_finished = True


            for student in students:
                mark = request.POST.get(f'mark{student.id}','')

                participation = Participation.objects.filter(course=course, student=student).first()
                participation.mark = mark
                participation.save()

            course.save()
            student.course.add(course)
        else:
            id = request.GET.get('id')
            course = Course.objects.get(pk=id,is_finished=False)

            students = Student.objects.filter(~Q(course = course),shift=shiftNow['shift_name'])

            for student in students:
                is_on = request.POST.get(f'addTo{student.id}')
                if is_on != None:
                    active = student.current_course
                    if active != None:
                        student.course.remove(active)
                        student.course.add(course)
                    else:
                        student.course.add(course)

        return redirect(f'/course-descript?id={course.id}')

def courseEdit(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    id = request.GET.get('id')
    if request.method == 'GET':
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
    id = request.GET.get('id')
    course = Course.objects.get(pk = id)
    course.delete()
    return redirect('/course-list')

def edit(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':

        id = request.GET.get('id')
        student = Student.objects.get(pk = int(id))
        courses = student.course.filter(is_finished=False)

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

        student.save()

        if course_id != '':
            studentCourse = Course.objects.get(pk=int(course_id),is_finished=False)
            student.course.set([studentCourse])


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
    students = Student.objects.filter(shift = shiftNow['name_shift'])
    students.delete()

    return redirect('/')

def showCourses(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    id = request.GET.get('id')
    shift = shiftNow['shift_name']
    finishedCourses = Course.objects.filter(shift = shift,is_finished = True)
    unFinishedCourses = Course.objects.filter(shift=shift,is_finished = False)

    return render(request,'course-list.html',{"finishedCourses":finishedCourses,"unFinishedCourses":unFinishedCourses,'shift':shiftNow['shift_name']})
