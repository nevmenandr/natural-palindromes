import os
import time
import re
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Точка входа
ROOT_DIR = "./ruscorpora/source/texts/"
OUTPUT_FILENAME = "palindromes_found.txt"
MIN_WORDS_FOR_PALINDROME = 2  # Одно слово не считается палиндромом
MIN_PALINDROME_LENGTH = 10  # Минимальная длина палиндрома (без учета пробелов и знаков препинания)

# Регулярное выражение для извлечения слов (только русские буквы)
WORD_PATTERN = re.compile(r'[а-яА-ЯёЁ]+')


def normalize_palindrome_text(text):
    """Нормализует текст палиндрома для сравнения (приводит к нижнему регистру, убирает пробелы)"""
    # Приводим к нижнему регистру
    text_lower = text.lower()
    # Убираем пробелы для сравнения
    return text_lower.replace(' ', '')


def load_existing_palindromes(output_path):
    """Загружает уже найденные палиндромы из файла и приводит их к нормализованному виду"""
    existing_palindromes = {}  # Словарь: нормализованный_вид -> оригинальный_текст
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем служебные строки (начинаются с "=" или "Поиск")
                    if line and not line.startswith('=') and not line.startswith('Поиск') and not line.startswith('ОШИБКА'):
                        # Сохраняем оригинальный текст палиндрома
                        original_text = line
                        # Создаем нормализованную версию для сравнения
                        normalized = normalize_palindrome_text(original_text)
                        existing_palindromes[normalized] = original_text
        except Exception as e:
            print(f"Предупреждение: не удалось загрузить существующие палиндромы: {e}")
    return existing_palindromes


def count_files(root_dir):
    """Подсчет общего количества файлов во всех вложенных каталогах"""
    total_files = 0
    for _, _, files in os.walk(root_dir):
        total_files += len(files)
    return total_files


def normalize_text(text):
    """Удаляет пробелы и знаки препинания, приводит к нижнему регистру"""
    # Оставляем только буквы
    cleaned = re.sub(r'[^а-яёА-ЯЁ]', '', text)
    cleaned = cleaned.replace('ё', 'е')
    cleaned = cleaned.replace('Ё', 'е')
    return cleaned.lower()


def is_palindrome(word_sequence):
    """Проверяет, является ли последовательность слов палиндромом"""
    if len(word_sequence) < MIN_WORDS_FOR_PALINDROME:
        return False
    
    # Проверяем, не состоит ли последовательность из одного и того же слова
    first_word = word_sequence[0]
    all_same = all(word == first_word for word in word_sequence)
    if all_same:
        return False
    
    # Объединяем слова в одну строку без пробелов
    combined = ''.join(word_sequence)
    normalized = normalize_text(combined)
    
    # Проверяем минимальную длину и палиндромность
    return len(normalized) >= MIN_PALINDROME_LENGTH and normalized == normalized[::-1]


def find_palindromes_in_text(text, file_path, output_file, existing_palindromes):
    """Поиск палиндромов в тексте"""
    # Извлекаем все слова из текста и приводим к нижнему регистру
    words_raw = WORD_PATTERN.findall(text)
    # Приводим все слова к нижнему регистру сразу при извлечении
    words = [word.lower() for word in words_raw]
    
    if len(words) < MIN_WORDS_FOR_PALINDROME:
        return
    
    # Перебираем все возможные начальные позиции
    for i in range(len(words)):
        # Проверяем от 10 слов до 2 слов (одно слово не считается)
        max_len = min(10, len(words) - i)
        for length in range(max_len, MIN_WORDS_FOR_PALINDROME - 1, -1):
            sequence = words[i:i + length]
            if is_palindrome(sequence):
                # Нашли палиндром (все слова уже в нижнем регистре)
                palindrome_text = ' '.join(sequence)
                
                # Создаем нормализованную версию для сравнения (без пробелов)
                normalized = palindrome_text.replace(' ', '')
                
                # Проверяем, не был ли этот палиндром уже найден (игнорируем регистр)
                if normalized not in existing_palindromes:
                    output_file.write(palindrome_text + "\n")
                    output_file.flush()  # Немедленно записываем на диск
                    existing_palindromes[normalized] = palindrome_text  # Сохраняем нормализованную версию
                break  # Переходим к следующему слову


def process_files(root_dir):
    """Основная функция обработки файлов"""
    # Определяем путь к выходному файлу
    output_path = os.path.join('./ruscorpora/', OUTPUT_FILENAME)
    
    # Загружаем уже существующие палиндромы
    print("Загрузка существующих палиндромов...")
    existing_palindromes = load_existing_palindromes(output_path)
    print(f"Загружено {len(existing_palindromes)} существующих палиндромов")
    
    # Подсчитываем общее количество файлов
    print("Подсчет количества файлов...")
    total_files = count_files(root_dir)
    print(f"Всего файлов для обработки: {total_files}")
    print("-" * 60)
    
    start_time = time.time()
    processed = 0
    new_palindromes_count = 0
    
    # Открываем выходной файл для добавления (append mode)
    # Если файл не существует, создаем его с заголовком
    file_mode = 'a' if os.path.exists(output_path) else 'w'
    
    with open(output_path, file_mode, encoding='utf-8') as output_file:
        # Если файл создается заново, добавляем заголовок
        if file_mode == 'w':
            output_file.write(f"Поиск палиндромов начат: {datetime.now()}\n")
            output_file.write("=" * 80 + "\n\n")
        
        # Рекурсивный обход всех файлов
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Пропускаем выходной файл, если он уже существует
            if OUTPUT_FILENAME in filenames:
                filenames.remove(OUTPUT_FILENAME)
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                processed += 1
                remaining = total_files - processed
                elapsed = time.time() - start_time
                
                # Расчет приблизительного оставшегося времени
                if processed > 1:
                    avg_time_per_file = elapsed / processed
                    estimated_remaining = avg_time_per_file * remaining
                    eta_str = str(timedelta(seconds=int(estimated_remaining)))
                else:
                    eta_str = "calculating..."
                
                # Вывод прогресса в консоль
                print(f"Файл {processed}/{total_files} | Осталось: {remaining} | "
                      f"Прошло: {str(timedelta(seconds=int(elapsed)))} | "
                      f"Осталось примерно: {eta_str}")
                
                # Обработка файла
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Считаем количество палиндромов до обработки файла
                    before_count = len(existing_palindromes)
                    find_palindromes_in_text(content, file_path, output_file, existing_palindromes)
                    after_count = len(existing_palindromes)
                    new_palindromes_count += after_count - before_count
                    
                except Exception as e:
                    # Логируем ошибки, но продолжаем работу
                    print(f"  Ошибка при обработке {file_path}: {e}")
                    output_file.write(f"ОШИБКА при обработке {file_path}: {e}\n")
                    output_file.flush()
        
        # Добавляем информацию о завершении
        output_file.write("\n" + "=" * 80 + "\n")
        output_file.write(f"Поиск завершен: {datetime.now()}\n")
        output_file.write(f"Обработано файлов: {processed}\n")
        output_file.write(f"Найдено новых палиндромов: {new_palindromes_count}\n")
        output_file.write(f"Всего палиндромов в базе: {len(existing_palindromes)}\n")
        output_file.write(f"Общее время: {str(timedelta(seconds=int(time.time() - start_time)))}\n")
    
    print("-" * 60)
    print(f"Обработка завершена!")
    print(f"Найдено новых палиндромов: {new_palindromes_count}")
    print(f"Всего палиндромов в базе: {len(existing_palindromes)}")


def run_paper_script():
    """Запускает скрипт palindromes_paper.py"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "palindromes_paper.py")
    
    if os.path.exists(script_path):
        print("\n" + "=" * 60)
        print(f"Запуск скрипта: {script_path}")
        print("=" * 60)
        try:
            # Запускаем скрипт в том же процессе
            subprocess.run([sys.executable, script_path], check=True)
            print("\nСкрипт palindromes_paper.py успешно выполнен!")
        except subprocess.CalledProcessError as e:
            print(f"\nОшибка при выполнении palindromes_paper.py: {e}")
        except Exception as e:
            print(f"\nНеожиданная ошибка при запуске palindromes_paper.py: {e}")
    else:
        print(f"\nПредупреждение: файл {script_path} не найден!")


def main():
    """Точка входа в программу"""
    if not os.path.exists(ROOT_DIR):
        print(f"Ошибка: директория {ROOT_DIR} не существует!")
        sys.exit(1)
    
    output_path = os.path.join('./ruscorpora/', OUTPUT_FILENAME)
    
    print(f"Начинаем поиск палиндромов в: {ROOT_DIR}")
    print(f"Результаты будут сохранены в: {output_path}")
    print(f"Минимальная длина палиндрома: {MIN_PALINDROME_LENGTH} символов")
    print(f"Регистр символов игнорируется при поиске и сравнении")
    print(f"Повторение одного и того же слова НЕ считается палиндромом")
    print("-" * 60)
    
    # Запускаем основной процесс
    process_files(ROOT_DIR)
    print("\nПоиск завершен!")
    
    # Запускаем palindromes_paper.py
    run_paper_script()


if __name__ == "__main__":
    main()
