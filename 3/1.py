import sys
import hashlib
import json
import os
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QVBoxLayout, QHBoxLayout, QListWidget, QInputDialog, QWidget,
    QDialog
)
from PyQt6.QtCore import Qt

# Константы
USER_DATA_FILE = 'users.json'
ADMIN_USERNAME = 'admin'
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4CAF50"
TEXT_COLOR = "#333333"


class PasswordSetupDialog(QDialog):
    def __init__(self, username, has_password_rules=False, parent=None):
        super().__init__(parent)
        self.username = username
        self.has_password_rules = has_password_rules
        self.setWindowTitle(f"Установка пароля для {username}")
        self.setModal(True)
        self.setFixedSize(350, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Стилизация
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_COLOR};
                font-size: 14px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                margin-bottom: 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 15px;
            }}
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)

        # Поля для пароля
        rules_note = " (минимум 6 символов)" if self.has_password_rules else ""
        self.password_label = QLabel(f"Новый пароль:{rules_note}")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")

        self.confirm_label = QLabel("Подтвердите пароль:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Повторите пароль")

        # Кнопки
        button_layout = QHBoxLayout()
        self.set_button = QPushButton("Установить пароль")
        self.set_button.clicked.connect(self.validate_password)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.set_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_label)
        layout.addWidget(self.confirm_input)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def validate_password(self):
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not password:
            QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        if self.has_password_rules and len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 6 символов!")
            return

        self.accept()


class UserAuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_attempts = 0
        self.current_user = None
        self.setWindowTitle('Система аутентификации пользователей')
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR};")
        self.init_ui()
        self.check_first_run()

    def init_ui(self):
        # Главный виджет и компоновка
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Окно входа
        self.login_group = QGroupBox('Вход в систему')
        self.login_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        self.login_layout = QVBoxLayout()

        # Поля ввода
        input_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                margin-bottom: 15px;
            }
        """

        self.username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(input_style)
        self.username_input.setPlaceholderText("Введите имя пользователя")

        self.password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)
        self.password_input.setPlaceholderText("Введите пароль")

        # Кнопки входа
        buttons_layout = QHBoxLayout()
        self.login_button = QPushButton('Войти')
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)

        self.exit_button = QPushButton('Выход')
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.exit_button)

        self.login_layout.addWidget(self.username_label)
        self.login_layout.addWidget(self.username_input)
        self.login_layout.addWidget(self.password_label)
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addLayout(buttons_layout)

        self.login_group.setLayout(self.login_layout)
        self.layout.addWidget(self.login_group)

        # Панель администратора
        self.init_admin_panel()
        self.admin_group.hide()

        # Панель пользователя
        self.init_user_panel()
        self.user_group.hide()

        # Подключение сигналов
        self.login_button.clicked.connect(self.login)
        self.exit_button.clicked.connect(self.close)

    def init_admin_panel(self):
        self.admin_group = QGroupBox('Панель администратора')
        self.admin_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        self.admin_layout = QVBoxLayout()

        # Список пользователей
        self.user_list = QListWidget()
        self.user_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                min-height: 150px;
            }
        """)

        # Кнопки администратора
        self.change_admin_pass_button = QPushButton('Сменить пароль администратора')
        self.add_user_button = QPushButton('Добавить пользователя')
        self.block_user_button = QPushButton('Заблокировать пользователя')
        self.unblock_user_button = QPushButton('Разблокировать пользователя')
        self.toggle_password_rules_button = QPushButton('Включить/выключить ограничения паролей')
        self.admin_exit_button = QPushButton('Завершить работу')

        # Стилизация кнопок
        for button in [
            self.change_admin_pass_button,
            self.add_user_button,
            self.block_user_button,
            self.unblock_user_button,
            self.toggle_password_rules_button,
            self.admin_exit_button
        ]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BUTTON_COLOR};
                    color: white;
                    border: none;
                    padding: 8px;
                    font-size: 14px;
                    border-radius: 4px;
                    margin-bottom: 10px;
                }}
                QPushButton:hover {{
                    background-color: #45a049;
                }}
            """)

        self.admin_exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        self.admin_layout.addWidget(self.user_list)
        self.admin_layout.addWidget(self.change_admin_pass_button)
        self.admin_layout.addWidget(self.add_user_button)
        self.admin_layout.addWidget(self.block_user_button)
        self.admin_layout.addWidget(self.unblock_user_button)
        self.admin_layout.addWidget(self.toggle_password_rules_button)
        self.admin_layout.addWidget(self.admin_exit_button)

        self.admin_group.setLayout(self.admin_layout)
        self.layout.addWidget(self.admin_group)

        # Подключение сигналов администратора
        self.change_admin_pass_button.clicked.connect(self.change_admin_password)
        self.add_user_button.clicked.connect(self.add_user)
        self.block_user_button.clicked.connect(lambda: self.toggle_user_block(True))
        self.unblock_user_button.clicked.connect(lambda: self.toggle_user_block(False))
        self.toggle_password_rules_button.clicked.connect(self.toggle_password_rules)
        self.admin_exit_button.clicked.connect(self.close)

    def init_user_panel(self):
        self.user_group = QGroupBox('Панель пользователя')
        self.user_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        self.user_layout = QVBoxLayout()

        self.change_pass_button = QPushButton('Сменить пароль')
        self.user_exit_button = QPushButton('Завершить работу')

        # Стилизация кнопок
        self.change_pass_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border: none;
                padding: 8px;
                font-size: 14px;
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)

        self.user_exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        self.user_layout.addWidget(self.change_pass_button)
        self.user_layout.addWidget(self.user_exit_button)

        self.user_group.setLayout(self.user_layout)
        self.layout.addWidget(self.user_group)

        # Подключение сигналов пользователя
        self.change_pass_button.clicked.connect(self.change_user_password)
        self.user_exit_button.clicked.connect(self.close)

    def check_first_run(self):
        users = self.load_users()
        if ADMIN_USERNAME not in users or users[ADMIN_USERNAME]['password'] == '':
            self.set_admin_password()

    def set_admin_password(self):
        dialog = PasswordSetupDialog(ADMIN_USERNAME, True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.password_input.text()
            users = self.load_users()
            users[ADMIN_USERNAME] = {
                'password': self.hash_password(password),
                'admin': True,
                'blocked': False,
                'password_rules': True
            }
            self.save_users(users)
            QMessageBox.information(self, 'Успех', 'Пароль администратора установлен!')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Пароль администратора обязателен!')
            sys.exit()

    def load_users(self):
        if not os.path.exists(USER_DATA_FILE):
            return {ADMIN_USERNAME: {'password': '', 'admin': True, 'blocked': False, 'password_rules': True}}
        try:
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        except:
            return {ADMIN_USERNAME: {'password': '', 'admin': True, 'blocked': False, 'password_rules': True}}

    def save_users(self, users):
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(users, file, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def update_user_list(self):
        users = self.load_users()
        self.user_list.clear()
        for username, data in users.items():
            if username != ADMIN_USERNAME:
                status = " (заблокирован)" if data['blocked'] else ""
                rules = " (ограничения паролей)" if data.get('password_rules', False) else ""
                self.user_list.addItem(f"{username}{status}{rules}")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        users = self.load_users()

        if not username:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя пользователя!')
            return

        if username not in users:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь не найден!')
            return

        if users[username]['blocked']:
            QMessageBox.warning(self, 'Ошибка', 'Ваш аккаунт заблокирован!')
            return

        # Если пароль не задан (новый пользователь)
        if users[username]['password'] == '':
            dialog = PasswordSetupDialog(
                username,
                users[username].get('password_rules', False)
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_password = dialog.password_input.text()
                users[username]['password'] = self.hash_password(new_password)
                self.save_users(users)
                QMessageBox.information(self, 'Успех', 'Пароль успешно установлен!')
                self.current_user = username
                self.login_group.hide()
                self.user_group.show()
            return

        if users[username]['password'] == self.hash_password(password):
            self.current_user = username
            self.login_group.hide()

            if username == ADMIN_USERNAME:
                self.update_user_list()
                self.admin_group.show()
            else:
                self.user_group.show()

            self.login_attempts = 0
        else:
            self.login_attempts += 1
            if self.login_attempts >= 3:
                QMessageBox.critical(self, 'Ошибка', 'Превышено количество попыток входа. Программа завершает работу.')
                self.close()
            else:
                QMessageBox.warning(self, 'Ошибка', f'Неверный пароль! Осталось попыток: {3 - self.login_attempts}')

    def change_admin_password(self):
        users = self.load_users()
        old_password, ok = QInputDialog.getText(
            self,
            'Смена пароля администратора',
            'Введите старый пароль:',
            QLineEdit.EchoMode.Password
        )

        if ok and users[ADMIN_USERNAME]['password'] == self.hash_password(old_password):
            dialog = PasswordSetupDialog(ADMIN_USERNAME, True)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_password = dialog.password_input.text()
                users[ADMIN_USERNAME]['password'] = self.hash_password(new_password)
                self.save_users(users)
                QMessageBox.information(self, 'Успех', 'Пароль администратора изменен!')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный старый пароль!')

    def add_user(self):
        username, ok = QInputDialog.getText(
            self,
            'Добавление пользователя',
            'Введите имя нового пользователя:'
        )

        if ok and username:
            if not username.strip():
                QMessageBox.warning(self, 'Ошибка', 'Имя пользователя не может быть пустым!')
                return

            users = self.load_users()
            if username in users:
                QMessageBox.warning(self, 'Ошибка', 'Пользователь уже существует!')
            else:
                users[username] = {
                    'password': '',
                    'admin': False,
                    'blocked': False,
                    'password_rules': False
                }
                self.save_users(users)
                self.update_user_list()
                QMessageBox.information(self, 'Успех', f'Пользователь {username} добавлен с пустым паролем!')

    def toggle_user_block(self, block):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пользователя!')
            return

        username = selected_items[0].text().split()[0]
        users = self.load_users()

        if username in users:
            users[username]['blocked'] = block
            self.save_users(users)
            self.update_user_list()
            status = 'заблокирован' if block else 'разблокирован'
            QMessageBox.information(self, 'Успех', f'Пользователь {username} {status}!')

    def toggle_password_rules(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пользователя!')
            return

        username = selected_items[0].text().split()[0]
        users = self.load_users()

        if username in users:
            users[username]['password_rules'] = not users[username]['password_rules']
            self.save_users(users)
            self.update_user_list()
            status = 'включены' if users[username]['password_rules'] else 'выключены'
            QMessageBox.information(self, 'Успех', f'Ограничения паролей для {username} {status}!')

    def change_user_password(self):
        users = self.load_users()
        username = self.current_user

        # Для новых пользователей (без пароля)
        if users[username]['password'] == '':
            dialog = PasswordSetupDialog(
                username,
                users[username].get('password_rules', False)
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_password = dialog.password_input.text()
                users[username]['password'] = self.hash_password(new_password)
                self.save_users(users)
                QMessageBox.information(self, 'Успех', 'Пароль успешно установлен!')
            return

        # Для существующих пользователей (смена пароля)
        old_password, ok = QInputDialog.getText(
            self,
            'Смена пароля',
            'Введите старый пароль:',
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return

        if users[username]['password'] != self.hash_password(old_password):
            QMessageBox.warning(self, 'Ошибка', 'Неверный старый пароль!')
            return

        dialog = PasswordSetupDialog(
            username,
            users[username].get('password_rules', False)
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_password = dialog.password_input.text()
            users[username]['password'] = self.hash_password(new_password)
            self.save_users(users)
            QMessageBox.information(self, 'Успех', 'Пароль успешно изменен!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = UserAuthApp()
    window.show()
    sys.exit(app.exec())
