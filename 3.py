import sys  # Модуль для взаимодействия с системой
import hashlib  # Модуль для хеширования паролей
import json  # Модуль для работы с JSON файлами
from PyQt6 import QtWidgets  # Основной модуль PyQt для GUI
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox,
    QCheckBox, QGroupBox, QVBoxLayout
)
import os  # Модуль для работы с файловой системой

USER_DATA_FILE = 'users.json'  # Имя файла для хранения данных пользователей

class UserAuthApp(QMainWindow):
    def __init__(self):
        super().__init__()  # Инициализация родительского класса
        self.setWindowTitle('User Authentication System')  # Установка заголовка окна
        self.setGeometry(100, 100, 400, 300)  # Задание размера и позиции окна

        self.init_ui()  # Вызов метода для инициализации интерфейса

    def init_ui(self):
        # Создание основных элементов интерфейса
        self.usernameLabel = QLabel('Имя пользователя:')
        self.usernameInput = QLineEdit()
        self.passwordLabel = QLabel('Пароль:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)  # Скрытие пароля при вводе

        # Кнопки для входа и регистрации
        self.loginButton = QPushButton('Войти')
        self.registerButton = QPushButton('Зарегистрироваться')

        # Элементы панели администратора
        self.adminGroup = QGroupBox('Панель администратора')
        self.adminUsernameLabel = QLabel('Имя пользователя:')
        self.adminUsernameInput = QLineEdit()
        self.blockUserButton = QPushButton('Заблокировать пользователя')
        self.unblockUserButton = QPushButton('Разблокировать пользователя')
        self.setAdminButton = QPushButton('Назначить администратором')

        # Флажок для назначения пользователя администратором при регистрации
        self.adminCheckBox = QCheckBox('Назначить администратором')

        # Компоновка основных элементов
        layout = QVBoxLayout()
        layout.addWidget(self.usernameLabel)
        layout.addWidget(self.usernameInput)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordInput)
        layout.addWidget(self.loginButton)
        layout.addWidget(self.registerButton)
        layout.addWidget(self.adminCheckBox)

        # Компоновка элементов панели администратора
        adminLayout = QVBoxLayout()
        adminLayout.addWidget(self.adminUsernameLabel)
        adminLayout.addWidget(self.adminUsernameInput)
        adminLayout.addWidget(self.blockUserButton)
        adminLayout.addWidget(self.unblockUserButton)
        adminLayout.addWidget(self.setAdminButton)
        self.adminGroup.setLayout(adminLayout)

        layout.addWidget(self.adminGroup)
        self.update_admin_controls(False)  # Панель администратора отключена по умолчанию

        # Установка главного виджета
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Подключение кнопок к методам
        self.loginButton.clicked.connect(self.login)
        self.registerButton.clicked.connect(self.register_user)
        self.blockUserButton.clicked.connect(self.block_user)
        self.unblockUserButton.clicked.connect(self.unblock_user)
        self.setAdminButton.clicked.connect(self.set_admin)

    def load_users(self):
        # Загрузка данных пользователей из файла
        if not os.path.exists(USER_DATA_FILE):
            return {}
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)

    def save_users(self, users):
        # Сохранение данных пользователей в файл
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(users, file, indent=4)

    def hash_password(self, password):
        # Хеширование пароля с использованием SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def update_admin_controls(self, is_admin):
        # Включение или отключение панели администратора
        self.adminGroup.setEnabled(is_admin)

    def register_user(self):
        # Регистрация нового пользователя
        users = self.load_users()
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        is_admin = self.adminCheckBox.isChecked()

        if username in users:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь уже существует!')
            return

        users[username] = {
            'password': self.hash_password(password),
            'admin': is_admin,
            'blocked': False
        }

        self.save_users(users)
        QMessageBox.information(self, 'Успех', 'Пользователь зарегистрирован!')

    def login(self):
        # Авторизация пользователя
        users = self.load_users()
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        if username not in users:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь не найден!')
            return

        if users[username]['blocked']:
            QMessageBox.warning(self, 'Ошибка', 'Ваш аккаунт заблокирован!')
            return

        if users[username]['password'] == self.hash_password(password):
            is_admin = users[username]['admin']
            self.update_admin_controls(is_admin)
            QMessageBox.information(self, 'Успех', 'Вход выполнен!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный пароль!')

    def block_user(self):
        self.toggle_user_block(True)

    def unblock_user(self):
        self.toggle_user_block(False)

    def toggle_user_block(self, block):
        # Блокировка или разблокировка пользователя
        users = self.load_users()
        username = self.adminUsernameInput.text()
        if username in users:
            users[username]['blocked'] = block
            status = 'заблокирован' if block else 'разблокирован'
            self.save_users(users)
            QMessageBox.information(self, 'Успех', f'Пользователь {username} {status}!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь не найден!')

    def set_admin(self):
        # Назначение пользователя администратором
        users = self.load_users()
        username = self.adminUsernameInput.text()
        if username in users:
            users[username]['admin'] = True
            self.save_users(users)
            QMessageBox.information(self, 'Успех', f'Пользователь {username} теперь администратор!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь не найден!')

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создание приложения
    window = UserAuthApp()  # Создание основного окна
    window.show()  # Отображение окна
    sys.exit(app.exec())  # Запуск основного цикла приложения
