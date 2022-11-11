import telebot
from telebot import types
from data import db_session
from data.users import User

user = User()

token = "5734490621:AAFmw1D559xMWqn9Ohosx-I42YLKurAeQXQ"
bot = telebot.TeleBot(token)

db_session.global_init("db/db.db")
db_sess = db_session.create_session()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print("Запущена команда /start")
    current_user_id = message.from_user.id

    if db_sess.query(User).filter(User.id == current_user_id).first():
        print(f"Пользователь {current_user_id} зарегистрирован")
        init_user(current_user_id)
        text = f"Добро пожаловать, {user.fio}"
        bot.send_message(message.from_user.id, text)
        show_main_keyboard(message)
    else:
        print(f"Пользователь {current_user_id} не зарегистрирован")
        text = "Здравствуйте, похоже вы у нас первый раз"
        bot.send_message(message.from_user.id, text)
        register_user(message)


def init_user(current_user_id):
    user_db = db_sess.query(User).filter(User.id == current_user_id).first()
    user.fio = user_db.fio
    user.birthday = user_db.birthday
    user.phone = user_db.phone
    user.sex = user_db.sex


def register_user(message):
    user.id = message.from_user.id
    bot.send_message(message.from_user.id,
                     "Давайте заполним вашу карточку! Как Вас зовут?\n"
                     "Введите ФИО в формате (Иванов Иван Иванович)")
    bot.register_next_step_handler(message, input_fio)


def input_fio(message):
    user.fio = message.text
    bot.send_message(message.from_user.id, "Когда у Вас день рождения?\n"
                                           "Введите дату в формате (01.01.1999)")
    bot.register_next_step_handler(message, input_birthday)


def input_birthday(message):
    user.birthday = message.text
    bot.send_message(message.from_user.id, "Теперь нам нужен Ваш номер телефона.\n"
                                           "Введите номер телефона в формате (+79998887766)")
    bot.register_next_step_handler(message, input_phone)


def input_phone(message):
    user.phone = message.text

    keyboard = types.InlineKeyboardMarkup()
    key_male = types.InlineKeyboardButton(text='Мужской', callback_data='male')
    keyboard.add(key_male)
    key_female = types.InlineKeyboardButton(text='Женский', callback_data='female')
    keyboard.add(key_female)

    bot.send_message(message.from_user.id, text="Ваш пол?", reply_markup=keyboard)


def show_confirm_input_keyboard(call):
    keyboard = types.InlineKeyboardMarkup()

    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)

    question = 'Ваша карточка:' + '\nФИО: ' + user.fio + '\nДата рождения: ' + user.birthday + '\nНомер телефона: ' \
               + user.phone + '\nПол: ' + user.sex + '\nВсе верно?'

    bot.send_message(call.message.chat.id, text=question, reply_markup=keyboard)


def show_main_keyboard(message):
    keyboard = types.InlineKeyboardMarkup()

    key_my_cart = types.InlineKeyboardButton(text='Моя карта', callback_data='my_cart')
    keyboard.add(key_my_cart)
    key_all_doctor = types.InlineKeyboardButton(text='Врачи', callback_data='all_doctor')
    keyboard.add(key_all_doctor)
    key_all_services = types.InlineKeyboardButton(text='Услуги', callback_data='all_services')
    keyboard.add(key_all_services)

    bot.send_message(message.chat.id, text="Выберите пункт меню:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "male":
        user.sex = "Мужской"
        bot.send_message(call.message.chat.id, text="Вы выбрали мужской пол!")
        show_confirm_input_keyboard(call)
    elif call.data == "female":
        user.sex = "Женский"
        bot.send_message(call.message.chat.id, text="Вы выбрали женский пол!")
        show_confirm_input_keyboard(call)
    elif call.data == "yes":
        db_sess.add(user)
        db_sess.commit()
        bot.send_message(call.message.chat.id, "Отлично, карточка добавлена в картотеку!")

        print(f"Пользователь {user.id} зарегистрирован и добавлен в картотеку")
        show_main_keyboard(call.message)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Попробуем еще раз!")
        bot.send_message(call.message.chat.id,
                         "Давайте заполним вашу карточку! Как Вас зовут?\n"
                         "Введите ФИО в формате (Иванов Иван Иванович)")
        bot.register_next_step_handler(call.message, input_fio)
    elif call.data == "my_cart":
        text = 'Ваша карточка:' + '\nФИО: ' + user.fio + '\nДата рождения: ' + user.birthday + '\nНомер телефона: ' \
                   + user.phone + '\nПол: ' + user.sex
        bot.send_message(call.message.chat.id, text)


bot.polling()
