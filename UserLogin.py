from flask_login import UserMixin
from flask import url_for


class UserLogin(UserMixin):
    # Используется при создание объекта в декораторе user_loader
    def fromDB(self, user_id, db):
        # Формируем частное свойство _user и присваеваем то,
        #  что возвратит метод getUser
        self.__user = db.getUser(user_id)
        return self

    # Вызываем, когда пользователь проходит авторизацию
    def create(self, user):
        self.__user = user
        return self

    # Через методы выше будет сформировано свойство __user,
    #  через кооторые можно получать id,
    #  чтобы модуль Flasklogin мог идентифицировать текущего пользователя
    def get_id(self):
        return str(self.__user['id'])

    # Возвращает имя пользователя
    def getName(self):
        return self.__user['name'] if self.__user else "Без имени"

    # Возвращает email пользователя
    def getEmail(self):
        return self.__user['email'] if self.__user else "Без email"

    def getAvatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: "+str(e))
        else:
            img = self.__user['avatar']

        return img

    def verifyExt(self, filename):
        # Делаем разделение файла с конца и находим точку
        ext = filename.rsplit('.', 1)[1]
        # Если остаток соответствует
        if ext == "png" or ext == "PNG":
            return True
        return False
