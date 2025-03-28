import sys
import hashlib
import json
import os
import re
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QVBoxLayout, QHBoxLayout, QListWidget, QInputDialog, QWidget,
    QDialog, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt

# Константы
USER_DATA_FILE = 'users.json'
ADMIN_USERNAME = 'admin'
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4CAF50"
TEXT_COLOR = "#333333"


class PasswordRulesDialog(QDialog):
    def __init__(self, username, current_rules=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.current_rules = current_rules or {
            'min_length': 6,
            'require_upper': False,
            'require_lower': False,
            'require_digit': False,
            'require_special': False
        }
        self.setWindowTitle(f"Настройка правил пароля для {username}")
        self.setModal(True)
        self.setFixedSize(350, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_COLOR};
                font-size: 14px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                margin-bottom: 5px;
            }}
            QSpinBox {{
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            QCheckBox {{
                margin-bottom: 10px;
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

        # Минимальная длина
        self.min_length_label = QLabel("Минимальная длина пароля:")
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setRange(4, 20)
        self.min_length_spin.setValue(self.current_rules['min_length'])

        # Чекбоксы для правил
        self.upper_check = QCheckBox("Требовать заглавные буквы (A-Z)")
        self.upper_check.setChecked(self.current_rules['require_upper'])

        self.lower_check = QCheckBox("Требовать строчные буквы (a-z)")
        self.lower_check.setChecked(self.current_rules['require_lower'])

        self.digit_check = QCheckBox("Требовать цифры (0-9)")
        self.digit_check.setChecked(self.current_rules['require_digit'])

        self.special_check = QCheckBox("Требовать спецсимволы (!@#$% и т.д.)")
        self.special_check.setChecked(self.current_rules['require_special'])

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(self.min_length_label)
        layout.addWidget(self.min_length_spin)
        layout.addWidget(self.upper_check)
        layout.addWidget(self.lower_check)
        layout.addWidget(self.digit_check)
        layout.addWidget(self.special_check)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_rules(self):
        return {
            'min_length': self.min_length_spin.value(),
            'require_upper': self.upper_check.isChecked(),
            'require_lower': self.lower_check.isChecked(),
            'require_digit': self.digit_check.isChecked(),
            'require_special': self.special_check.isChecked()
        }


class PasswordSetupDialog(QDialog):
    def __init__(self, username, password_rules=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.password_rules = password_rules or {
            'min_length': 0,  # По умолчанию нет ограничений
            'require_upper': False,
            'require_lower': False,
            'require_digit': False,
            'require_special': False
        }
        self.setWindowTitle(f"Установка пароля для {username}")
        self.setModal(True)
        self.setFixedSize(350, 250)
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
        rules_text = self._get_rules_text()
        self.password_label = QLabel(f"Новый пароль:{rules_text}")
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

    def _get_rules_text(self):
        if not any(self.password_rules.values()):
            return ""
            
        rules = []
        if self.password_rules['min_length'] > 0:
            rules.append(f" мин. {self.password_rules['min_length']} симв.")
        
        if self.password_rules['require_upper']:
            rules.append(" заглавные буквы")
        
        if self.password_rules['require_lower']:
            rules.append(" строчные буквы")
        
        if self.password_rules['require_digit']:
            rules.append(" цифры")
        
        if self.password_rules['require_special']:
            rules.append(" спецсимволы")
        
        if rules:
            return " (требуется:" + ",".join(rules) + ")"
        return ""

    def validate_password(self):
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not password:
            QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        # Проверка минимальной длины
        if self.password_rules['min_length'] > 0 and len(password) < self.password_rules['min_length']:
            QMessageBox.warning(
                self, 
                "Ошибка", 
                f"Пароль должен быть не менее {self.password_rules['min_length']} символов!"
            )
            return

        # Проверка на заглавные буквы
        if self.password_rules['require_upper'] and not re.search(r'[A-ZА-Я]', password):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пароль должен содержать хотя бы одну заглавную букву!"
            )
            return

        # Проверка на строчные буквы
        if self.password_rules['require_lower'] and not re.search(r'[a-zа-я]', password):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пароль должен содержать хотя бы одну строчную букву!"
            )
            return

        # Проверка на цифры
        if self.password_rules['require_digit'] and not re.search(r'[0-9]', password):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пароль должен содержать хотя бы одну цифру!"
            )
            return

        # Проверка на спецсимволы
        if self.password_rules['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пароль должен содержать хотя бы один спецсимвол!"
            )
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

    # ... (остальные методы остаются такими же, кроме set_admin_password)

    def set_admin_password(self):
        # Для первого входа администратора не устанавливаем ограничения
        dialog = PasswordSetupDialog(ADMIN_USERNAME, {
            'min_length': 0,
            'require_upper': False,
            'require_lower': False,
            'require_digit': False,
            'require_special': False
        })
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.password_input.text()
            users = self.load_users()
            users[ADMIN_USERNAME] = {
                'password': self.hash_password(password),
                'admin': True,
                'blocked': False,
                'password_rules': {
                    'min_length': 8,  # После первого входа устанавливаем стандартные правила
                    'require_upper': True,
                    'require_lower': True,
                    'require_digit': True,
                    'require_special': True
                }
            }
            self.save_users(users)
            QMessageBox.information(self, 'Успех', 'Пароль администратора установлен!')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Пароль администратора обязателен!')
            sys.exit()

    # ... (остальной код остается без изменений)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = UserAuthApp()
    window.show()
    sys.exit(app.exec())
