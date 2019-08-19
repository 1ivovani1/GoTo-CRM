token = "986077789:AAFGgfn9yUbD2Kkqvhp0ZgYXOpSGeWtW850"
import os
import django
import telebot
import uuid
from telebot import types
os.environ["DJANGO_SETTINGS_MODULE"] = 'GoToHelper.settings'
django.setup()
from crm.models import Student, Course, Comment,CustomUser,Shift

telebot.apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
bot = telebot.TeleBot(token)


users = CustomUser.objects.all()
telegram_users = {798710883:0}

class States:
    logined = 0

    name_for_photo = 1
    add_photo = 2


    name_for_comment = 4
    add_comment = 5

    get_photo = 8

    @staticmethod
    def set_state(user_id, state):
        telegram_users[user_id] = state

    @staticmethod
    def get_state(user_id):
        return telegram_users[user_id]

    @staticmethod
    def check(message, state):
        return len(users.filter(tg_login=message.from_user.username)) > 0 and States.get_state(message.from_user.id) == state


def get_name(message, state):
    data = message.text.split()

    if len(data) != 2:
        bot.send_message(message.chat.id, 'Заполните поле правильно')
    else:
        shift = Shift.objects.filter(is_finished=False).first()
        print(shift)
        students = Student.objects.filter(first_name=data[0], last_name=data[1],shift = shift).all()
        if not students:
            bot.send_message(message.chat.id, 'Такого участника нет в базе данных')
        else:
            States.set_state(message.from_user.id, state)
            return students[0]


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in telegram_users.keys():
        telegram_users[message.from_user.id] = -1

    if len(users.filter(tg_login=message.from_user.username)) > 0:
        bot.send_message(message.chat.id, 'Привет, все в порядке, ты зарегестрирован. \nМожешь сразу приступить к работе или узнать доступные команды /help')
        States.set_state(message.from_user.id, States.logined)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа.')


@bot.message_handler(commands=['help'], func=lambda message: States.check(message, state=States.logined))
def help(message):
    keyboard = types.ReplyKeyboardMarkup()
    sendPhoto = types.KeyboardButton(text="/send_photo")
    addComment = types.KeyboardButton(text="/add_comment")
    getPhoto = types.KeyboardButton(text="/get_photo")
    keyboard.add(sendPhoto)
    keyboard.add(addComment)
    keyboard.add(getPhoto)
    bot.send_message(message.chat.id,'СпИсОк ДоСтУпНыХ кОмАнД:\n/send_photo\n/add_comment\n/get_photo',reply_markup=keyboard)

@bot.message_handler(commands=['send_photo'], func=lambda message: States.check(message, state=States.logined))
def command_send_photo(message):
    bot.send_message(message.chat.id, 'Отправь имя и фамилию участника которому хочешь изменить фотографию')
    States.set_state(message.from_user.id, state=States.name_for_photo)

@bot.message_handler(content_types=['text'], func=lambda message: States.check(message, state=States.name_for_photo))
def name_for_photo(message):
    student = get_name(message, States.add_photo)
    bot.register_next_step_handler(bot.send_message(message.chat.id, 'Теперь пришли фотографию которую надо добавить'), add_photo, student)



@bot.message_handler(content_types=['image'], func=lambda message: States.check(message, state=States.add_photo))
def add_photo(message,student):
    file_id = message.photo[-1].file_id
    path = bot.get_file(file_id)
    downloaded_file = bot.download_file(path.file_path)

    extn = '.' + str(path.file_path).split('.')[-1]
    name = 'media/avatars/' + str(uuid.uuid4()) + extn


    with open(name, 'wb') as new_file:
        new_file.write(downloaded_file)

    student.avatar = name
    student.save()

    States.set_state(message.from_user.id, States.logined)
    bot.send_message(message.chat.id,'Фотография успешно обновлена!')

@bot.message_handler(commands=['add_comment'],func=lambda message: States.check(message,state=States.logined))
def command_comment(message):
    bot.send_message(message.chat.id, 'Отправь имя и фамилию участника для которого хочешь оставить комментарий')
    States.set_state(message.from_user.id, States.name_for_comment)

@bot.message_handler(content_types=['text'],func=lambda message:States.check(message,state=States.name_for_comment))
def name_for_comment(message):
    student = get_name(message, States.add_comment)
    bot.register_next_step_handler(bot.send_message(message.chat.id, 'Теперь пришли комментарий который хочешь оставить'), add_comment, student)


@bot.message_handler(content_types=['text'], func=lambda message: States.check(message, state=States.add_comment))
def add_comment(message, student):
    comment = Comment()
    comment.author = users.filter(tg_login = message.from_user.username)[0]
    comment.whom_comm = student
    comment.text = message.text
    comment.save()
    States.set_state(message.from_user.id,States.logined)
    bot.send_message(message.chat.id,'Ваш комментарий был успешно загружен!')

@bot.message_handler(commands=['get_photo'], func=lambda message: States.check(message, state=States.logined))
def command_get_photo(message):
    States.set_state(message.from_user.id, States.get_photo)
    bot.register_next_step_handler(bot.send_message(message.chat.id, 'Отправь имя и фамилию ученика,фотку которого хочешьполучить!'),get_photo)

@bot.message_handler(content_types=['text'], func=lambda message: States.check(message, state=States.get_photo))
def get_photo(message):
    student = get_name(message, States.logined)
    photo = student.avatar
    bot.send_photo(message.chat.id,photo)
    States.set_state(message.from_user.id, States.logined)


bot.polling(none_stop=True)
