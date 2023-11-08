import sqlite3
from flask import (
    Blueprint, render_template,
    url_for, redirect, session, request, flash, g
)


admin = Blueprint(
    # admin - имя Blueprint, используется как суффикс ко всем именам методов,
    # которые будут использоваться
    # директива __name__ указывает на то, что каталоги templates и static
    # нужно искать относительного текущего католога
    'admin', __name__,
    template_folder='templates',
    static_folder='static'
)

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список статей'},
        {'url': '.logout', 'title': 'Выйти'}]


def login_admin():
    # В сессии создаем и сохраняем запись admin_logged со значением 1
    #  и в дальнейшем будем пологать, что если эта запись сессии существует,
    #  то пользователь зашел в админ панель
    session['admin_logged'] = 1


def isLogged():
    #  Проверяет зашел ли в админ панель или нет
    return True if session.get('admin_logged') else False


def logout_admin():
    # выход из админ панели
    session.pop('admin_logged', None)


# Ссылается на соединение с БД
db = None
@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    # в переменной link_db -храним соединение с БД
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')


@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            # Точка означает, что функцию представления index
            #  следует брать из текущего Blueprint
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    # Если администратор не вошел в админ панель
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))


@admin.route('/list-pubs')
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))

    # Из БД читаем список статей и сохраняем в list
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            # получаем список словарей
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template(
        'admin/listpubs.html', title='Список статей',
        menu=menu, list=list)


@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template(
        'admin/listusers.html', title='Список пользователей',
        menu=menu, list=list)
