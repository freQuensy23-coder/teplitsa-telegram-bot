import dataclasses

from db import get_all_courses


@dataclasses.dataclass
class Messages:
    @dataclasses.dataclass
    class Registration:
        start_1 = """"Привет! Это бот платформы Теплица.Курсы. Здесь вы можете:

1. Узнать, что такое парный созвон и записаться на него
2. Узнавать о расписании Марафона Поддержки, если вы в нем участвуете
3. Рассказать о технической проблеме, которая возникла на платформе
4. Дать любую обратную связь. 

Выберите, с чего хотите начать."""
        start_select_course = "Теперь выберете курсы которые вы проходите"
        registration_success = "Спасибо! Теперь вы будете получать уведомления от курса  "
        no_such_course = "Такого курса не существует"
        no_course_selected = "Вы не выбрали ни одного курса. Вы сможете добавить их позже нажав перезапустить бота в " \
                             "настройках. "

    @dataclasses.dataclass
    class Menu:
        use_menu_help = "Для управление ботом можно использовать меню"

    @dataclasses.dataclass
    class PairCall:
        select_group_call_type = "Выберете тип парного созвона"
        pair_call_already_created = "Вы уже отправляли запрос на парный созвон. Чтобы выйти из очереди напишите " \
                                    "/kick_call "
        pair_call_created_success = "Вы отправили запрос на парный созвон. Ожидайте ответа"
        leave_call_queue_help = "Выйти из очереди на парный созвон можно написав /kick_call"
        select_course = "Выберете курс из списка на клавиатуре"
        you_are_not_in_queue = "Вы не находитесь в очереди на парный созвон"
        leave_call_queue_success = "Вы вышли из очереди на парный созвон"
        what_is_pair_call_help = """Что такое парный созвон?
        Чтобы информация с курса усваивалась лучше, мы предлагаем вам пересказать все, что вы запомнили за пройденный курс. Для этого запишитесь на парный созвон, и мы подберем вам человека, который созвониться вместе с вами.

        * Как проходит парный созвон? *
        Вы выбираете удобное для вас с напарником время
        Созваниваетесь и по очереди рассказываете друг другу все, что помните о пройденном курсе 
        Пока ваш напарник рассказывает, вы слушаете и записываете вопросы
        Затем вы меняетесь

        * Что дает парный созвон? *
        Информация, пройденная за курс, усваивается лучше. Вы пересказываете ее напарнику и таким образом, у вас выстраивается система пройденного материала, которую вы можете озвучить. Это поможет вам легче применять материл на практике.

        * Правила: *
        Внимательно слушать напарника и не перебивать
        Задавать уточняющие вопросы
        Рассказывать про свой курс не больше 30 минут (иначе будет сложно держать концентрацию)

        *Сколько ждать напарника? *
        К сожалению, пока что парный созвон - это не распространенная практика, поэтому можно ждать от часа до нескольких дней. Вы можете написать в чат Теплицы.Курсы о своем желании созвониться с кем-то или попросить коллегу пройти курс на Теплице и вместе созвониться с вами :)"""
        not_reg_to_such_course = "Вы не являетесь участником такого курса. Пожалуйста, зарегистрируйтесь на этом " \
                                 "курсе через настройки "

        @staticmethod
        def global_pair_call_pair_found(pair):
            return f"Вам нашли пару для созвона - @{pair.username}. Напишите ему и назначте время встречи. " \
                   f"Используйте <a href=https://meet.google.com/new>Google Meet</a> для встречи."

        @staticmethod
        def leave_local_course_success(course_name):
            return f"Вы вышли из очереди на созвон по курсу {course_name}"

        @staticmethod
        def contact_user_to_pair_call(telegram_user, course):
            return f"Для вас нашлась пара на парный созвон на курсе {course.name} -  @{telegram_user.username}." \
                   f" Используйте <a href='https://vk.cc/cfKNE3'>данную</a>" \
                   f"  комнату в google meet. Но вначале напишите ему личное сообщение и " \
                   f"назначте время встречи "

    @dataclasses.dataclass
    class Settings:
        settings_help = "Вы можете выбрать другой курс или поменять настройки бота через это меню"
        select_course_again = "Вы вернулись к выборку курса"

    @dataclasses.dataclass
    class Notifications:
        notification_help = "Спасибо! Теперь вы будете получать напоминания о встречах на Марафоне Поддержки." \
                            " Мы пришлем напоминания за час до следующего мероприятия :) "

    class FeedBack:
        help = "Расскажите, с какой проблемой вы столкнулись? Можете прикрепить фотографию и подробно описать, " \
               "что пошло не так. Можете прикрепить картинку или файл."
        ok = "Спасибо! Скоро мы со всем разберемся и если это необходимо, свяжемся с вами."


@dataclasses.dataclass
class Buttons:
    @dataclasses.dataclass
    class Registration:
        start = "☑️Начать"

    @dataclasses.dataclass
    class PairCall:
        global_pair_call_button = "Я хочу на парный созвон кем угодно"
        course_pair_call_button = "Я хочу на парный созвон с человеком с моего курса"

    @dataclasses.dataclass
    class Menu:
        menu_settings = "⚙ Настройки"
        menu_notification = "🔔 Уведомлять о событиях Марафона Поддержки"
        menu_pair_call = "📲 Хочу на парный созвон"
        menu_feedback = "Обратная связь"
        menu = "◀ В меню"

    @dataclasses.dataclass
    class Settings:
        settings_restart = "🔄 Перезагрузить бота"

    @dataclasses.dataclass
    class Notification:
        on_notification = "✅ Уведомлять о событиях Марафона"
        off_notification = "❌ Выключить все уведомления"


@dataclasses.dataclass
class Commands:
    kick_all_calls = "/kick_call"


pair_call_queue = {course: None for course in get_all_courses()}
