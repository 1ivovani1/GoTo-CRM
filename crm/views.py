from django.shortcuts import render,redirect

from crm.models import Student,Course

def index(request):
    students = Student.objects.all()
    return render(request,"index.html",{"students":students})

def details(request):
    id = request.GET.get('id')
    student = Student.objects.get(pk = id)
    return render(request,'details.html',{"student":student})

def add(request):
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
    id = request.GET.get('id')
    course = Course.objects.get(pk=id)
    students = Student.objects.filter(course = course).all()
    return render(request,'course-descript.html',{'course':course,'students':students})

def courseEdit(request):
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
    id = request.GET.get('id')
    course = Course.objects.get(pk = id)
    course.delete()
    return redirect('/course-list')

def edit(request):
    if request.method == 'GET':
        courses = Course.objects.all()
        id = request.GET.get('id')
        student = Student.objects.get(pk = id)
        return render(request,'change.html',{"student":student,'courses':courses})

    if request.method == "POST":
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
    id = request.GET.get('id')
    student = Student.objects.get(pk = id)
    student.delete()

    return redirect('/')

#работа с курсами

def showCourses(request):
    courses = Course.objects.all()
    return render(request,'course-list.html',{"courseList":courses})

def courseInfo(request):
    id = request.GET.get('id')
    course = Course.objects.get(pk = id)
    return render(request,'course-descript.html',{"course":course})
