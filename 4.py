"""
Программа для шифрования и дешифрования текста методами Цезаря и Виженера
Поддерживает русский и английский алфавиты, сохраняет регистр и неалфавитные символы
"""

import os
import random

# Функции для работы с файлами
def read_file(filename):
    """Чтение содержимого файла с проверкой его существования"""
    if not os.path.exists(filename):
        print(f"Ошибка: Файл {filename} не найден!")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, text):
    """Запись текста в файл"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def get_first_lines(text, n=5):
    """Получение первых n строк текста"""
    lines = text.splitlines()
    return "\n".join(lines[:n])


# Реализация шифра Цезаря
def caesar_encrypt(text, key):
    """Шифрование текста методом Цезаря с заданным ключом-сдвигом"""
    result = []
    # Определение алфавитов для латиницы и кириллицы (с учетом буквы Ё)
    LAT_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    LAT_LOWER = "abcdefghijklmnopqrstuvwxyz"
    RUS_UPPER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    RUS_LOWER = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

    for ch in text:
        # Обработка символов в зависимости от их принадлежности к алфавиту
        if ch in LAT_UPPER:
            new_index = (LAT_UPPER.index(ch) + key) % len(LAT_UPPER)
            result.append(LAT_UPPER[new_index])
        elif ch in LAT_LOWER:
            new_index = (LAT_LOWER.index(ch) + key) % len(LAT_LOWER)
            result.append(LAT_LOWER[new_index])
        elif ch in RUS_UPPER:
            new_index = (RUS_UPPER.index(ch) + key) % len(RUS_UPPER)
            result.append(RUS_UPPER[new_index])
        elif ch in RUS_LOWER:
            new_index = (RUS_LOWER.index(ch) + key) % len(RUS_LOWER)
            result.append(RUS_LOWER[new_index])
        else:
            result.append(ch)  # Неалфавитные символы остаются без изменений
    return "".join(result)

def caesar_decrypt(text, key):
    """Дешифрование текста методом Цезаря"""
    # Дешифрование - это шифрование с отрицательным ключом
    return caesar_encrypt(text, -key)


# Реализация шифра Виженера
CYRILLIC_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

def vigenere_square(alphabet):
    """Генерация квадрата Виженера для заданного алфавита"""
    size = len(alphabet)
    rows = []
    for i in range(size):
        # Каждая строка квадрата - это сдвинутый алфавит
        row = alphabet[i:] + alphabet[:i]
        rows.append(row)
    return "\n".join(rows)

def vigenere_encrypt(text, key, alphabet):
    """Шифрование текста методом Виженера"""
    result = []
    key_length = len(key)
    alphabet_upper = alphabet.upper()  # Алфавит в верхнем регистре
    alphabet_lower = alphabet.lower()  # Алфавит в нижнем регистре

    for i, ch in enumerate(text):
        if ch.upper() in alphabet_upper:
            # Обработка символов с учетом регистра
            if ch.isupper():
                index = alphabet_upper.index(ch)
                key_char = key[i % key_length].upper()
                key_index = alphabet_upper.index(key_char)
                enc_index = (index + key_index) % len(alphabet_upper)
                result.append(alphabet_upper[enc_index])
            else:
                index = alphabet_lower.index(ch)
                key_char = key[i % key_length].lower()
                key_index = alphabet_lower.index(key_char)
                enc_index = (index + key_index) % len(alphabet_lower)
                result.append(alphabet_lower[enc_index])
        else:
            result.append(ch)  # Неалфавитные символы остаются без изменений
    return "".join(result)

def vigenere_decrypt(text, key, alphabet):
    """Дешифрование текста методом Виженера"""
    result = []
    key_length = len(key)
    alphabet_upper = alphabet.upper()
    alphabet_lower = alphabet.lower()

    for i, ch in enumerate(text):
        if ch.upper() in alphabet_upper:
            # Обработка символов с учетом регистра (аналогично шифрованию, но с вычитанием)
            if ch.isupper():
                index = alphabet_upper.index(ch)
                key_char = key[i % key_length].upper()
                key_index = alphabet_upper.index(key_char)
                dec_index = (index - key_index) % len(alphabet_upper)
                result.append(alphabet_upper[dec_index])
            else:
                index = alphabet_lower.index(ch)
                key_char = key[i % key_length].lower()
                key_index = alphabet_lower.index(key_char)
                dec_index = (index - key_index) % len(alphabet_lower)
                result.append(alphabet_lower[dec_index])
        else:
            result.append(ch)
    return "".join(result)


# Пользовательские интерфейсы для методов шифрования
def caesar_cli():
    """Интерфейс командной строки для шифра Цезаря"""
    key = input("Введите ключ (целое число): ")
    try:
        key = int(key)
    except ValueError:
        print("Ошибка: Ключ должен быть целым числом!")
        return

    original = read_file("caesar_test.txt")
    if original is None or len(original) < 2000:
        print("Ошибка: Файл caesar_test.txt не найден или содержит менее 2000 символов!")
        return

    # Шифрование и дешифрование
    encrypted = caesar_encrypt(original, key)
    decrypted = caesar_decrypt(encrypted, key)

    # Сохранение результатов
    write_file("en_Cesar.txt", encrypted)
    write_file("de_Cesar.txt", decrypted)

    # Вывод результатов
    print(" Исходный текст (первые 5 строк) ")
    print(get_first_lines(original))
    print("\n Зашифрованный текст (Цезарь) ")
    print(get_first_lines(encrypted))
    print("\n Расшифрованный текст (Цезарь) ")
    print(get_first_lines(decrypted))

def vigenere_cli():
    """Интерфейс командной строки для шифра Виженера"""
    key = input("Введите ключ (текст): ").strip()
    if not key:
        print("Ошибка: Введите ключ!")
        return

    # Проверка, что ключ состоит только из букв алфавита
    if not all(ch.upper() in CYRILLIC_ALPHABET for ch in key):
        print("Ошибка: Ключ должен содержать только кириллические символы!")
        return

    # Выбор типа алфавита
    alphabet_option = input("Выберите вариант алфавита (1 - по порядку, 2 - случайным образом): ")
    if alphabet_option == "1":
        alphabet = CYRILLIC_ALPHABET
    elif alphabet_option == "2":
        alph_list = list(CYRILLIC_ALPHABET)
        random.shuffle(alph_list)
        alphabet = "".join(alph_list)
        print("Сгенерированный алфавит:", alphabet)
    else:
        print("Ошибка: Неверный выбор алфавита!")
        return

    # Вывод квадрата Виженера
    print("\n----- Квадрат Виженера -----")
    square = vigenere_square(alphabet)
    print(square)

    original = read_file("Vinzher_test.txt")
    if original is None or len(original) < 2000:
        print("Ошибка: Файл Vinzher_test.txt не найден или содержит менее 2000 символов!")
        return

    # Шифрование и дешифрование
    encrypted = vigenere_encrypt(original, key, alphabet)
    decrypted = vigenere_decrypt(encrypted, key, alphabet)

    # Сохранение результатов
    write_file("en_Vishner.txt", encrypted)
    write_file("de_Vishner.txt", decrypted)

    # Вывод результатов
    print("----- Исходный текст (первые 5 строк) -----")
    print(get_first_lines(original))
    print("\n----- Зашифрованный текст -----")
    print(get_first_lines(encrypted))
    print("\n----- Расшифрованный текст -----")
    print(get_first_lines(decrypted))


# Главное меню программы
def main():
    """Основная функция с меню выбора методов"""
    while True:
        print("\nВыберите метод:")
        print("1. Метод Цезаря")
        print("2. Метод Виженера")
        print("3. Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            caesar_cli()
        elif choice == "2":
            vigenere_cli()
        elif choice == "3":
            break
        else:
            print("Ошибка: Неверный выбор!")


# Точка входа в программу
if __name__ == "__main__":
    main()
