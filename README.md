# 🔄 Natural Palindromes

[![DOI](https://zenodo.org/badge/1156733651.svg)](https://doi.org/10.5281/zenodo.20701309) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Ruscorpora](https://img.shields.io/badge/data-Ruscorpora-blue.svg)](https://ruscorpora.ru/)
[![Telegram](https://img.shields.io/badge/Telegram-обсуждение-2CA5E0?logo=telegram)](https://t.me/schonenrede/882)

Поиск **естественных (несконструированных)** палиндромов в текстах [Национального корпуса русского языка](https://ruscorpora.ru/).

> 📢 [Обсуждение в Telegram-канале](https://t.me/schonenrede/882)

---

## 📖 Замысел

Все знают виртуозные палиндромы вроде *«А роза упала на лапу Азора»* или *«Тарту дорог как город утрат»* — но они специально сконструированы остроумцами и мастерами слова. А что если поискать **случайные**, естественно возникшие палиндромы в живой речи?

Бывают случайные метры в прозе, а должны быть случайные палиндромы в текстах.

Этот проект — попытка найти такие палиндромы в массиве текстов [НКРЯ](https://ruscorpora.ru/).

---

## 🎯 Особенности поиска

Чтобы отсеять тривиальные и сконструированные случаи, были установлены следующие фильтры:

| Фильтр | Значение | Обоснование |
|--------|----------|-------------|
| **Минимальная длина** | 10 букв | Отсекаем короткие и случайные совпадения |
| **Минимум слов** | 2 | Одно слово — не палиндром (банальность) |
| **Исключение повторов** | Да | `«кошка кошка кошка»` — не считается |
| **Регистронезависимость** | Да | Приводим всё к нижнему регистру |
| **Игнорирование пунктуации** | Да | Учитываем только буквы |

Дополнительно: сравнение с уже найденными палиндромами при повторных запусках, чтобы избежать дублирования.

---

## 🧹 Постобработка результатов

После автоматического поиска я **вручную очистил** результаты от мусора — бессмысленных последовательностей, которые формально являются палиндромами, но не представляют интереса:

```
е о а а а са а а о е
м ммм м м м м м м
жжж жжж жжж ууу ууу ууу жжж жжж жжж
э эээ эээээээээ
с ссссс сссс ссссс
о о о оо о о о о о оо
т д д т д д т д д т
ю ю ю ю ю ю ю ю ю ююю
ахаха а ха ха
```

Это позволило оставить в итоговом списке только осмысленные или хотя бы забавные фразы.

---

## ⚙️ Алгоритм

### Почему не Манакер?

В задачах поиска палиндромов часто упоминается **[алгоритм Манакера](https://en.wikipedia.org/wiki/Longest_palindromic_substring)** — эффективный метод поиска всех палиндромных подстрок в строке за линейное время O(n). Однако в данном проекте он **не используется** и вот почему:

| Критерий | Наш подход | Алгоритм Манакера |
|----------|------------|-------------------|
| **Что ищем** | Палиндромы на уровне **слов** (2–10 слов) | Палиндромы на уровне **символов** |
| **Размерность** | Проверяем до 9 вариантов на каждое слово | Каждая возможная подстрока |
| **Сложность** | O(n × m), где m ≤ 10 | O(L), где L — длина текста |
| **Учёт границ слов** | ✅ Да (критично для осмысленности) | ❌ Нет |

Наш подход **намеренно ограничен** последовательностями из 2–10 слов, что делает наивную проверку `s == s[::-1]` не только достаточной, но и оптимальной для этой задачи. Алгоритм Манакера был бы избыточным и не учитывал бы границы слов, что привело бы к большому количеству бессмысленных находок.

### Текущая реализация

```python
def is_palindrome(word_sequence):
    combined = ''.join(word_sequence)
    normalized = normalize_text(combined)  # только буквы, нижний регистр
    return len(normalized) >= MIN_PALINDROME_LENGTH and normalized == normalized[::-1]
```

Просто, быстро и ровно под нашу задачу.

---

## ⚡ Производительность

Несмотря на «наивность» подхода, **современные машины легко справляются** с большими объёмами данных. Время выполнения для 131 391 файла (~6 часов 48 минут) зафиксировано в файле результатов:

```
================================================================================
Поиск завершен: 2026-08-14 07:51:49.609437
Обработано файлов: 131391
Найдено новых палиндромов: 217
Общее время: 6:48:27
```

Это полностью приемлемо для одноразового исследования, а при необходимости обработку можно распараллелить.

---

## ⚙️ Код

### Структура

```
.
├── README.md
├── CITATION.cff                  # Информация для цитирования
├── palindromes_found.txt          # Результаты из основного корпуса
├── palindromes_found2.txt         # Результаты из газетного корпуса
└── src/
    ├── palindromes.py             # Основной скрипт для source/texts/
    └── palindromes_paper.py       # Скрипт для газетного корпуса paper/
```

### Алгоритм работы скриптов

1. Обход всех текстовых файлов в `./ruscorpora/source/texts/` и `./ruscorpora/paper/`
2. Извлечение всех слов (только кириллица)
3. Проверка последовательностей длиной от 2 до 10 слов на палиндромность
4. Запись в выходной файл только уникальных палиндромов
5. Игнорирование ошибок кодировки (бинарные файлы `.git/index`, `.pack`, `.idx`)

### Автоматический запуск

Скрипт `palindromes.py` после завершения обработки основного корпуса **автоматически запускает** `palindromes_paper.py` для газетного корпуса. Вам не нужно ждать и запускать второй скрипт вручную — всё происходит в одном сеансе.

### Ключевые функции

- `normalize_text()` — очистка от знаков препинания и приведение к нижнему регистру
- `is_palindrome()` — проверка последовательности на палиндромность
- `find_palindromes_in_text()` — основной поиск по тексту файла
- `load_existing_palindromes()` — загрузка уже найденных для исключения дублей

---

## 🔍 Результаты

### 🌿 Естественные палиндромы (с подтверждённым контекстом)

| Палиндром | Контекст в НКРЯ |
|-----------|------------------|
| `еще и еще и еще` | [ссылка](https://ruscorpora.ru/s/P1qA4) |
| `искать такси` | [ссылка](https://ruscorpora.ru/s/Q1rB9) |
| `он тут как тут но` | [ссылка](https://ruscorpora.ru/s/MjnxG) |
| `воду с судов` | [ссылка](https://ruscorpora.ru/s/Nxoyv) |
| `одессе до` | [ссылка](https://ruscorpora.ru/s/RgvDE) |
| `и манекенами` | [ссылка](https://ruscorpora.ru/s/O7pzr) |

### 🏆 Из газетного корпуса

| Палиндром | Примечание |
|-----------|------------|
| `Ани Лорак Каролина` | Настоящее имя певицы (2019) |
| `соник в кино с` | Газетная статья 2019 года |
| `или заразили` | Случайное совпадение в новостном тексте |

### 🎭 Красивые сконструированные (попавшиеся по пути)

> *«Кот учен, но как он нечуток!»*  
> *«А в окне чирикала Кириченкова»*  
> *«У шпал Ленин ел лапшу»*  
> *«Муза, ранясь шилом опыта, ты помолишься на разум»*  
> *«Я и ты — боги и иго бытия»*  
> *«Да вот на деле дантов Ад»*  
> *«Конец оценок»*

### 🔄 Типичные естественные паттерны

В корпусе обнаружились целые серии палиндромов, построенных по одному принципу:

- `еще и еще и еще`
- `летел и летел`
- `лил и лил и лил`

Это свидетельствует о том, что повторяющиеся конструкции с союзами часто дают палиндромические эффекты.

---

## 📊 Статистика

| Корпус | Обработано файлов | Найдено новых палиндромов | Время |
|--------|-------------------|---------------------------|-------|
| Основной | 131 391 | 217 | ~6 ч 48 м |
| Газетный | — | — | — |


---

## 📁 Результаты

- [`palindromes_found.txt`](./palindromes_found.txt) — палиндромы из основного корпуса
- [`palindromes_found2.txt`](./palindromes_found2.txt) — палиндромы из газетного корпуса

---

## 📎 Ссылки

- [Обсуждение в Telegram-канале](https://t.me/schonenrede/882)
- [НКРЯ — Национальный корпус русского языка](https://ruscorpora.ru/)
- [Статья о случайных метрах в прозе](https://nevmenandr.github.io/portfolio/assets/pdf/rhythm_prose.pdf)
- [Коллекция палиндромов на tema.ru](https://www.tema.ru/rrr/palindromes/)
- [Алгоритм Манакера (Wikipedia)](https://en.wikipedia.org/wiki/Longest_palindromic_substring)

---

## Автор

[Борис Орехов](https://nevmenandr.github.io/): 

[![Bluesky](https://img.shields.io/badge/Bluesky-0285FF?style=for-the-badge&logo=Bluesky&logoColor=white)](https://bsky.app/profile/nevmenandr.bsky.social) [![Mastodon](https://img.shields.io/badge/-MASTODON-%232B90D9?style=for-the-badge&logo=mastodon&logoColor=white)](https://mastodon.social/@nevmenandr) [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/schonenrede) [![X](https://img.shields.io/badge/X-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)](https://x.com/nevmenandr) [![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://www.youtube.com/@schonenrede/)

[![academia Logo](https://img.shields.io/badge/academia-41454A?style=flat-square&logo=academia&logoColor=white)](https://hse-ru.academia.edu/BorisOrekhov) [![arxiv Logo](https://img.shields.io/badge/-arxiv-B31B1B?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/search/cs?searchtype=author&query=Orekhov,+B) [![dev.to Logo](https://img.shields.io/badge/dev-000000?style=flat-square&logo=dev.to&logoColor=white)](https://dev.to/nevmenandr) [![elsevier Logo](https://img.shields.io/badge/elsevier-FF6C00?style=flat-square&logo=elsevier&logoColor=white)](https://www.scopus.com/authid/detail.uri?authorId=57190401804) [![habr Logo](https://img.shields.io/badge/habr-65A3BE?style=flat-square&logo=habr&logoColor=white)](https://habr.com/ru/users/nevmenandr/) [![huggingface Logo](https://img.shields.io/badge/huggingface-FFD21E?style=flat-square&logo=huggingface&logoColor=white)](https://huggingface.co/nevmenandr) [![orcid Logo](https://img.shields.io/badge/orcid-A6CE39?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0000-0002-9099-0436) [![osf Logo](https://img.shields.io/badge/osf-2CB9F1?style=flat-square&logo=osf&logoColor=white)](https://osf.io/phy74/) 

[![pypi Logo](https://img.shields.io/badge/pypi-3775A9?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/user/nevmenandr/) [![researchgate Logo](https://img.shields.io/badge/researchgate-00CCBB?style=flat-square&logo=researchgate&logoColor=white)](https://researchgate.net/profile/Boris-Orekhov) [![semanticscholar Logo](https://img.shields.io/badge/semanticscholar-1857B6?style=flat-square&logo=semanticscholar&logoColor=white)](https://www.semanticscholar.org/author/Boris-V.-Orekhov/2080424505)  [![wikipedia Logo](https://img.shields.io/badge/wikipedia-000000?style=flat-square&logo=wikipedia&logoColor=white)](https://ru.wikipedia.org/wiki/%D0%A3%D1%87%D0%B0%D1%81%D1%82%D0%BD%D0%B8%D0%BA:Nevmenandr)


