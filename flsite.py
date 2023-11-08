import sqlite3
import os
from flask import (
    Flask, render_template, abort, g,
    flash, request, session, redirect, url_for, make_response)
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user,
)
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin


# Конфигурация
# DATABASE - путь к базе данных
DATABASE = '/tmp/flsite.db'
# Режим отладки
DEBUG = True
SECRET_KEY = '_s8f$h&)7xdc$yh_yaowt@%=om'
# Какого максимального объема файл можно загружать на сервер в байтах (1МБ)
MAX_CONTENT_LENGTH = 1024 * 1024


app = Flask(__name__)
# Загружаем конфигурацию. __name__ ссылается на текущий модуль
app.config.from_object(__name__)

# Переопределяем путь к базе данных. root_path - ссылается на текущий каталог
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
# app.config['SECRET_KEY'] = '_s8f$h&)7xdc$yh_yaowt@%=om'

# первым параметром указывается каким именно blueprint будет регистрироваться,
# благодаря url_prefix, все url внутри blueprint будут иметь такой вид:
# домен/<url_prefix>/<URL-blueprint>
app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Аввторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    ''' Функция установления соединения с базой данных '''
    conn = sqlite3.connect(app.config['DATABASE'], timeout=20)
    # Записи представлены в виде словарей
    conn.row_factory = sqlite3.Row
    # Возвращает установленное соединение
    return conn


def create_db():
    ''' Вспомогательная функция для созданя таблиц БД '''
    # Вызываем функцию
    db = connect_db()
    # Используем менеджер контекста для того, чтобы прочитать файл 'sq_db.sql',
    #  который находится в рабочем катологе нашего приложения и в нем записан
    # набор sql скриптов, для создания таблиц для работы нашего сайта.
    # Режим 'r' - открываем файл для чтения
    with app.open_resource('sq_db.sql', mode='r') as f:
        # Запускает выполнения скриптов из файла 'sq_db.sql'
        db.cursor().executescript(f.read())
    db.commit()
    db.cursor().close()
    db.close()


def get_db():
    ''' Соединение с БД, если она еще не установлена '''
    # g - записана информация установления соединения с БД
    # проверяем ли существует ли у g свойство 'link_db'
    # Если существует, то соединение уже есть
    if not hasattr(g, 'link_db'):
        # Если соединения нет, то вызываем функцию
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    ''' Установление соединения с БД перед выполнением запроса '''
    global dbase
    # Соединяемся с базой данных
    db = get_db()
    # Создаем экземпляр класса FDataBase
    dbase = FDataBase(db)


# Декоратор для разрыва соединения
# Срабатывает при уничтожение контекста приложения
# Обычно происходит в момент завершения обработки запроса
@app.teardown_appcontext
def close_db(error):
    ''' Закрываем соединение с БД, если оно было установлено '''
    # Если соединение было установлено, то его надо закрыть
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
def index():
    # getMenu возвращает коллекцию из словарей
    # menu - формируем ссылку на коллекцию
    return render_template(
        'index.html', menu=dbase.getMenu(),
        posts=dbase.getPostsAnonce()
    )


@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    # если данные от формы пришли
    if request.method == 'POST':
        # Если заголовок статьи больше 4 символов и содержимое статьи больше 10
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            # добавляем пост в базу данных
            res = dbase.addPost(
                request.form['name'], request.form['post'], request.form['url']
            )
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template(
        'add_post.html', menu=dbase.getMenu(), title='Добавление статьи'
    )


@app.route('/post/<alias>')
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template(
        'post.html', menu=dbase.getMenu(), title=title, post=post
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    # Были ли отправлены данные POST запросом, а также корректны ли данные
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

    return render_template(
        "login.html", menu=dbase.getMenu(), title="Авторизация",
        form=form
    )
    # if request.method == "POST":
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         userlogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(userlogin, remember=rm)
    #         return redirect(request.args.get("next") or url_for("profile"))

    #     flash("Неверная пара логин/пароль", "error")

    # return render_template(
    #     "login.html", menu=dbase.getMenu(), title="Авторизация"
    # )


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Кодируем введенный пароль (генерируем хэш)
        hash = generate_password_hash(request.form['psw'])
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")
    # Если пришли данные по POST запросу
    # if request.method == "POST":
    #     if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
    #         and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
    #         # Кодируем введенный пароль (генерируем хэш)
    #         hash = generate_password_hash(request.form['psw'])
    #         res = dbase.addUser(request.form['name'], request.form['email'], hash)
    #         if res:
    #             flash("Вы успешно зарегистрированы", "success")
    #             return redirect(url_for('login'))
    #         else:
    #             flash("Ошибка при добавлении в БД", "error")
    #     else:
    #         flash("Неверно заполнены поля", "error")

    return render_template(
        "register.html", menu=dbase.getMenu(), title="Регистрация",
        form=form
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template(
        "profile.html", menu=dbase.getMenu(), title="Профиль"
    )


@app.route('/userava')
@login_required
def userava():
    # Берем аватарку текущего пользователя
    img = current_user.getAvatar(app)
    if not img:
        return ""

    # Создается объект запроса,
    # и в нем параметр 'Content-Type' устанавливается 'image/png'
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        # Если файл успешно загружен и что его расширение - png
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                # updateUserAvatar - происходит изменение аватара пользователя
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
