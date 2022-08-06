import dataclasses


@dataclasses.dataclass
class Texts:
    start_1 = "Чтобы начать общаться, выберете тот курс, который вы проходите"
    start_select_course = "Выберете курс из списка на клавиатуре"
    registration_succes = "Спасибо! Теперь мы знаем, что вы проходите курс ..."
    use_menu_help = "Для управление ботом можно использовать меню"
    no_such_course = "Такого курса не существует"
    pair_call_already_created = "Вы уже отправляли запрос на парный созвон. Чтобы выйти из очереди напишите /kick_call"
    pair_call_created_success = "Вы отправили запрос на парный созвон. Ожидайте ответа"
    leave_call_queue_help = "Выйти из очереди на парный созвон можно написав /kick_call"
    you_are_not_in_queue = "Вы не находитесь в очереди на парный созвон"
    leave_call_queue_success = "Вы вышли из очереди на парный созвон"
    notification_help = "Вы можете настроить уведомления о событиях Марафона Поддержки через это меню (пока не функционирует)"
    settings_help = "Вы можете выбрать другой курс или поменять настройки бота через это меню"
    select_course_again = "Вы вернулись к выборку курса"
    what_is_pair_call = """Что такое парный созвон?
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


courses = ["Тестовый курс 1", "Тестовый курс 2", "Тестовый курс 3"]
menu_settings = "⚙ Настройки"
menu_notification = "🔔 Уведомлять о событиях Марафона Поддержки"
menu_pair_call = "📲 Хочу на парный созвон"
settings_restart = "🔄 Перезагрузить бота"
menu = "◀ В меню"
