import sys
import hashlib
import json
import os
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox,
    QCheckBox, QGroupBox, QVBoxLayout, QSpinBox
)

# Файл для хранения данных пользователей
USER_DATA_FILE = 'users.json'
# Фиксированное имя администратора
ADMIN_USERNAME = 'admin'


class UserAuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('User Authentication System')
        self.setGeometry(100, 100, 400, 350)
        self.init_ui()
        self.ensure_admin_exists()

    def init_ui(self):
        # Создание интерфейса пользователя
        self.usernameLabel = QLabel('Имя пользователя:')
        self.usernameInput = QLineEdit()
        self.passwordLabel = QLabel('Пароль:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.loginButton = QPushButton('Войти')
        self.registerButton = QPushButton('Зарегистрироваться')

        # Панель администратора
        self.adminGroup = QGroupBox('Панель администратора')
        self.adminUsernameLabel = QLabel('Имя пользователя:')
        self.adminUsernameInput = QLineEdit()
        self.blockUserButton = QPushButton('Заблокировать пользователя')
        self.unblockUserButton = QPushButton('Разблокировать пользователя')

        # Ограничения на пароль
        self.passwordRulesLabel = QLabel('Минимальная длина пароля:')
        self.passwordLengthInput = QSpinBox()
        self.passwordLengthInput.setMinimum(4)
        self.passwordLengthInput.setValue(6)
        self.savePasswordRulesButton = QPushButton('Сохранить правила')

        # Создание компоновки элементов
        layout = QVBoxLayout()
        layout.addWidget(self.usernameLabel)
        layout.addWidget(self.usernameInput)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordInput)
        layout.addWidget(self.loginButton)
        layout.addWidget(self.registerButton)

        adminLayout = QVBoxLayout()
        adminLayout.addWidget(self.adminUsernameLabel)
        adminLayout.addWidget(self.adminUsernameInput)
        adminLayout.addWidget(self.blockUserButton)
        adminLayout.addWidget(self.unblockUserButton)
        adminLayout.addWidget(self.passwordRulesLabel)
        adminLayout.addWidget(self.passwordLengthInput)
        adminLayout.addWidget(self.savePasswordRulesButton)
        self.adminGroup.setLayout(adminLayout)

        layout.addWidget(self.adminGroup)
        self.update_admin_controls(False)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Подключение кнопок к обработчикам
        self.loginButton.clicked.connect(self.login)
        self.registerButton.clicked.connect(self.register_user)
        self.blockUserButton.clicked.connect(self.block_user)
        self.unblockUserButton.clicked.connect(self.unblock_user)
        self.savePasswordRulesButton.clicked.connect(self.save_password_rules)

    def load_users(self):
        if not os.path.exists(USER_DATA_FILE):
            return {}
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)

    def save_users(self, users):
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(users, file, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def ensure_admin_exists(self):
        users = self.load_users()
        if ADMIN_USERNAME not in users:
            admin_password, ok = QtWidgets.QInputDialog.getText(self, "Установка пароля",
                                                              "Введите пароль для администратора:",
                                                              QLineEdit.EchoMode.Password)
            if ok and admin_password:
                users[ADMIN_USERNAME] = {'password': self.hash_password(admin_password), 'admin': True,
                                        'blocked': False, 'password_rules': {'min_length': 6}}
                self.save_users(users)
                QMessageBox.information(self, 'Успех', 'Администратор создан!')
            else:
                QMessageBox.critical(self, 'Ошибка', 'Пароль администратора обязателен! Приложение закроется.')
                sys.exit()

    def update_admin_controls(self, is_admin):
        self.adminGroup.setEnabled(is_admin)

    def save_password_rules(self):
        users = self.load_users()
        min_length = self.passwordLengthInput.value()
        users[ADMIN_USERNAME]['password_rules'] = {'min_length': min_length}
        self.save_users(users)
        QMessageBox.information(self, 'Успех', 'Правила пароля сохранены!')

    def login(self):
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

    def register_user(self):
        users = self.load_users()
        username = self.usernameInput.text()
        password = self.passwordInput.text()

        min_length = users.get(ADMIN_USERNAME, {}).get('password_rules', {}).get('min_length', 6)
        if len(password) < min_length:
            QMessageBox.warning(self, 'Ошибка', f'Пароль должен быть не менее {min_length} символов!')
            return

        if username in users:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь уже существует!')
            return

        users[username] = {'password': self.hash_password(password), 'admin': False, 'blocked': False}
        self.save_users(users)
        QMessageBox.information(self, 'Успех', 'Пользователь зарегистрирован!')

    def block_user(self):
        self.toggle_user_block(True)

    def unblock_user(self):
        self.toggle_user_block(False)

    def toggle_user_block(self, block):
        users = self.load_users()
        username = self.adminUsernameInput.text()
        if username == ADMIN_USERNAME:
            QMessageBox.warning(self, 'Ошибка', 'Нельзя заблокировать администратора!')
            return
        if username in users:
            users[username]['blocked'] = block
            status = 'заблокирован' if block else 'разблокирован'
            self.save_users(users)
            QMessageBox.information(self, 'Успех', f'Пользователь {username} {status}!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь не найден!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UserAuthApp()
    window.show()
    sys.exit(app.exec())
