"""
Every text the school results page shows, in its 4 languages: English, Bulgarian, Russian and
Romanian. alex_school_results.py asks for a text by its name (its "key") with translate().

To change a text, change it here in all 4 languages. To add one, add a new key with all 4
languages: the app checks at start that none is missing.

Texts with {names} in curly brackets get numbers or names filled in, like {count} or {region}.
Numbers in the texts keep the decimal point in every language, like the charts do.
"""

# The 4 languages, in the order of the buttons at the top of the page
LANGUAGES = {"en": "EN", "bg": "BG", "ru": "RU", "ro": "RO"}

# The language of the page at the plain address, like http://127.0.0.1:7860
FIRST_LANGUAGE = "bg"

# The name of each language in English, to tell the AI model which language to write in
LANGUAGE_NAMES = {"en": "English", "bg": "Bulgarian", "ru": "Russian", "ro": "Romanian"}

TEXTS = {
    # --- The top of the page ---
    "page_title": {
        "en": "Bulgarian school exam results",
        "bg": "Изпитни резултати на българските училища",
        "ru": "Результаты экзаменов в школах Болгарии",
        "ro": "Rezultatele școlilor din Bulgaria la examene",
    },
    "intro": {
        "en": "Official results by school from the Ministry of Education and Science (МОН), published on the national open data portal data.egov.bg. **NVO** (НВО) = national external assessment, average score in points (maximum 100). **DZI** (ДЗИ) = state matriculation exams (матури), May-June session, average grade from 2 to 6. **BEL** = Bulgarian language and literature, **MAT** = Maths.",
        "bg": "Официални резултати по училища от Министерството на образованието и науката (МОН), публикувани на националния портал за отворени данни data.egov.bg. **НВО** = национално външно оценяване, среден резултат в точки (максимум 100). **ДЗИ** = държавни зрелостни изпити (матури), сесия май–юни, среден успех от 2 до 6. **БЕЛ** = български език и литература, **МАТ** = математика.",
        "ru": "Официальные результаты по школам от Министерства образования и науки (МОН), опубликованные на национальном портале открытых данных data.egov.bg. **НВО** = национальное внешнее оценивание, средний балл (максимум 100). **ДЗИ** = государственные выпускные экзамены (матура), сессия май–июнь, средняя оценка от 2 до 6. **БЕЛ** = болгарский язык и литература, **МАТ** = математика.",
        "ro": "Rezultate oficiale pe școli de la Ministerul Educației și Științei (МОН), publicate pe portalul național de date deschise data.egov.bg. **NVO** (НВО) = evaluarea națională externă, punctaj mediu (maximum 100). **DZI** (ДЗИ) = examenele de stat de bacalaureat (матури), sesiunea mai-iunie, nota medie de la 2 la 6. **BEL** = limba și literatura bulgară, **MAT** = matematică.",
    },
    "data_status": {
        "en": "**Data:** {files} results files in the local database ({database}) · last checked on data.egov.bg: {last_check}",
        "bg": "**Данни:** {files} файла с резултати в локалната база данни ({database}) · последна проверка в data.egov.bg: {last_check}",
        "ru": "**Данные:** файлов с результатами в локальной базе ({database}): {files} · последняя проверка data.egov.bg: {last_check}",
        "ro": "**Date:** fișiere cu rezultate în baza de date locală ({database}): {files} · ultima verificare pe data.egov.bg: {last_check}",
    },
    "never": {
        "en": "never",
        "bg": "никога",
        "ru": "никогда",
        "ro": "niciodată",
    },
    "check_button": {
        "en": "Check for new results",
        "bg": "Провери за нови резултати",
        "ru": "Проверить новые результаты",
        "ro": "Caută rezultate noi",
    },
    "checking": {
        "en": "*Checking data.egov.bg for new results files: this takes about 20 seconds...*",
        "bg": "*Проверка в data.egov.bg за нови файлове с резултати: отнема около 20 секунди...*",
        "ru": "*Проверяем data.egov.bg на новые файлы с результатами: это займёт около 20 секунд...*",
        "ro": "*Caut fișiere noi cu rezultate pe data.egov.bg: durează cam 20 de secunde...*",
    },
    "check_failed": {
        "en": "Couldn't check for new results: {error}",
        "bg": "Неуспешна проверка за нови резултати: {error}",
        "ru": "Не удалось проверить новые результаты: {error}",
        "ro": "Nu am putut căuta rezultate noi: {error}",
    },
    "files_added": {
        "en": "New results files added: {count} ({files}).",
        "bg": "Добавени нови файлове с резултати: {count} ({files}).",
        "ru": "Добавлено новых файлов с результатами: {count} ({files}).",
        "ro": "Fișiere noi cu rezultate adăugate: {count} ({files}).",
    },
    "no_new_files": {
        "en": "No new results: the database is up to date.",
        "bg": "Няма нови резултати: базата данни е актуална.",
        "ru": "Новых результатов нет: база данных актуальна.",
        "ro": "Niciun rezultat nou: baza de date este la zi.",
    },

    # --- The choices above the tabs ---
    "exam_label": {
        "en": "Exam and school year",
        "bg": "Изпит и учебна година",
        "ru": "Экзамен и учебный год",
        "ro": "Examen și an școlar",
    },
    "region_label": {
        "en": "Region (област)",
        "bg": "Област",
        "ru": "Область",
        "ro": "Regiune (област)",
    },
    "town_label": {
        "en": "Town (град / село) - type to search",
        "bg": "Населено място (град / село) - пишете, за да търсите",
        "ru": "Населённый пункт (город / село) - введите для поиска",
        "ro": "Localitate (град / село) - scrie pentru a căuta",
    },
    "search_label": {
        "en": "School, town or municipality contains",
        "bg": "Училище, населено място или община съдържа",
        "ru": "Школа, населённый пункт или община содержит",
        "ro": "Școala, localitatea sau comuna conține",
    },
    "search_placeholder": {
        "en": "for example: Математическа",
        "bg": "например: Математическа",
        "ru": "например: Математическа",
        "ro": "de exemplu: Математическа",
    },
    "rank_label": {
        "en": "Rank schools by",
        "bg": "Подреди училищата по",
        "ru": "Рейтинг школ по",
        "ro": "Ordonează școlile după",
    },
    "show_button": {
        "en": "Show results",
        "bg": "Покажи резултатите",
        "ru": "Показать результаты",
        "ro": "Arată rezultatele",
    },
    "overview_button": {
        "en": "Write AI overview of the top {top} ({model})",
        "bg": "ИИ обзор на първите {top} ({model})",
        "ru": "Обзор ИИ лучших {top} ({model})",
        "ro": "Scrie prezentarea AI pentru top {top} ({model})",
    },
    "all_regions": {
        "en": "All regions",
        "bg": "Всички области",
        "ru": "Все области",
        "ro": "Toate regiunile",
    },
    "all_towns": {
        "en": "All towns",
        "bg": "Всички населени места",
        "ru": "Все населённые пункты",
        "ro": "Toate localitățile",
    },
    "subject: Bulgarian (BEL)": {
        "en": "Bulgarian (BEL)",
        "bg": "Български (БЕЛ)",
        "ru": "Болгарский (БЕЛ)",
        "ro": "Bulgară (BEL)",
    },
    "subject: Maths / 2nd exam": {
        "en": "Maths / 2nd exam",
        "bg": "Математика / 2-ри изпит",
        "ru": "Математика / 2-й экзамен",
        "ro": "Matematică / examenul 2",
    },
    "subject: Both subjects": {
        "en": "Both subjects",
        "bg": "Двата предмета",
        "ru": "Оба предмета",
        "ro": "Ambele materii",
    },

    # --- The exams, as the lists show them ---
    "exam: NVO 4th grade": {
        "en": "NVO 4th grade",
        "bg": "НВО 4. клас",
        "ru": "НВО 4 класс",
        "ro": "NVO clasa a 4-a",
    },
    "exam: NVO 7th grade": {
        "en": "NVO 7th grade",
        "bg": "НВО 7. клас",
        "ru": "НВО 7 класс",
        "ro": "NVO clasa a 7-a",
    },
    "exam: NVO 10th grade": {
        "en": "NVO 10th grade",
        "bg": "НВО 10. клас",
        "ru": "НВО 10 класс",
        "ro": "NVO clasa a 10-a",
    },
    "exam: DZI (matura)": {
        "en": "DZI (matura)",
        "bg": "ДЗИ (матури)",
        "ru": "ДЗИ (матура)",
        "ro": "DZI (bacalaureat)",
    },

    # --- The tables' column names ---
    "column: Region": {
        "en": "Region",
        "bg": "Област",
        "ru": "Область",
        "ro": "Regiune",
    },
    "column: Municipality": {
        "en": "Municipality",
        "bg": "Община",
        "ru": "Община",
        "ro": "Comună",
    },
    "column: Town": {
        "en": "Town",
        "bg": "Населено място",
        "ru": "Нас. пункт",
        "ro": "Localitate",
    },
    "column: School": {
        "en": "School",
        "bg": "Училище",
        "ru": "Школа",
        "ro": "Școală",
    },
    "column: School code": {
        "en": "School code",
        "bg": "Код на училището",
        "ru": "Код школы",
        "ro": "Cod școală",
    },
    "column: BEL students": {
        "en": "BEL students",
        "bg": "БЕЛ явили се",
        "ru": "Учеников БЕЛ",
        "ro": "Elevi BEL",
    },
    "column: BEL points": {
        "en": "BEL points",
        "bg": "БЕЛ точки",
        "ru": "Баллы БЕЛ",
        "ro": "Puncte BEL",
    },
    "column: MAT students": {
        "en": "MAT students",
        "bg": "МАТ явили се",
        "ru": "Учеников МАТ",
        "ro": "Elevi MAT",
    },
    "column: MAT points": {
        "en": "MAT points",
        "bg": "МАТ точки",
        "ru": "Баллы МАТ",
        "ro": "Puncte MAT",
    },
    "column: BEL grade": {
        "en": "BEL grade",
        "bg": "БЕЛ успех",
        "ru": "Оценка БЕЛ",
        "ro": "Notă BEL",
    },
    "column: 2nd exam students": {
        "en": "2nd exam students",
        "bg": "2-ри изпит явили се",
        "ru": "Учеников 2-й экз.",
        "ro": "Elevi examenul 2",
    },
    "column: 2nd exam grade": {
        "en": "2nd exam grade",
        "bg": "2-ри изпит успех",
        "ru": "Оценка 2-й экз.",
        "ro": "Notă examenul 2",
    },
    "column: Schools": {
        "en": "Schools",
        "bg": "Училища",
        "ru": "Школ",
        "ro": "Școli",
    },
    "column: Students": {
        "en": "Students",
        "bg": "Ученици",
        "ru": "Учеников",
        "ro": "Elevi",
    },
    "column: Both subjects": {
        "en": "Both subjects",
        "bg": "Двата предмета",
        "ru": "Оба предмета",
        "ro": "Ambele materii",
    },
    "column: Vs area average": {
        "en": "Vs area average",
        "bg": "Спрямо средното",
        "ru": "К среднему",
        "ro": "Față de media zonei",
    },

    # --- The tabs ---
    "tab_schools": {
        "en": "Schools",
        "bg": "Училища",
        "ru": "Школы",
        "ro": "Școli",
    },
    "tab_top": {
        "en": "Top {top} towns and schools + AI overview",
        "bg": "Първите {top} населени места и училища + ИИ обзор",
        "ru": "Топ-{top} пунктов и школ + обзор ИИ",
        "ro": "Top {top} localități și școli + prezentare AI",
    },
    "tab_map": {
        "en": "Map and trends of the regions",
        "bg": "Карта и тенденции на областите",
        "ru": "Карта и тренды областей",
        "ro": "Harta și tendințele regiunilor",
    },

    # --- Messages ---
    "choose_exam": {
        "en": "Please choose an exam and a school year.",
        "bg": "Моля, изберете изпит и учебна година.",
        "ru": "Выберите экзамен и учебный год.",
        "ro": "Alege un examen și un an școlar.",
    },
    "database_error": {
        "en": "Couldn't read the results from the database: {error}",
        "bg": "Резултатите не могат да бъдат прочетени от базата данни: {error}",
        "ru": "Не удалось прочитать результаты из базы данных: {error}",
        "ro": "Nu am putut citi rezultatele din baza de date: {error}",
    },

    # --- The Schools tab ---
    "schools_table": {
        "en": "Schools",
        "bg": "Училища",
        "ru": "Школы",
        "ro": "Școli",
    },
    "summary_head": {
        "en": "**{choice}** · {area} · **Schools: {count}**",
        "bg": "**{choice}** · {area} · **Училища: {count}**",
        "ru": "**{choice}** · {area} · **Число школ: {count}**",
        "ro": "**{choice}** · {area} · **Școli: {count}**",
    },
    "scale_nvo": {
        "en": "points (maximum 100)",
        "bg": "точки (максимум 100)",
        "ru": "баллов (максимум 100)",
        "ro": "puncte (maximum 100)",
    },
    "scale_dzi": {
        "en": "grade (2 to 6)",
        "bg": "успех (от 2 до 6)",
        "ru": "оценка (от 2 до 6)",
        "ro": "notă (de la 2 la 6)",
    },
    "short: BEL": {
        "en": "BEL",
        "bg": "БЕЛ",
        "ru": "БЕЛ",
        "ro": "BEL",
    },
    "short: MAT": {
        "en": "MAT",
        "bg": "МАТ",
        "ru": "МАТ",
        "ro": "MAT",
    },
    "short: 2nd exam": {
        "en": "2nd exam",
        "bg": "2-ри изпит",
        "ru": "2-й экзамен",
        "ro": "examenul 2",
    },
    "subject_line": {
        "en": "- {subject}: average **{average}** {scale}, students: {students}",
        "bg": "- {subject}: среден резултат **{average}** {scale}, явили се: {students}",
        "ru": "- {subject}: в среднем **{average}** {scale}, учеников: {students}",
        "ro": "- {subject}: media **{average}** {scale}, elevi: {students}",
    },
    "region_name": {
        "en": "{region} region",
        "bg": "област {region}",
        "ru": "область {region}",
        "ro": "regiunea {region}",
    },
    "bulgaria": {
        "en": "Bulgaria",
        "bg": "България",
        "ru": "Болгария",
        "ro": "Bulgaria",
    },
    "rank_in_bulgaria": {
        "en": "towns in Bulgaria",
        "bg": "населени места в България",
        "ru": "среди населённых пунктов Болгарии",
        "ro": "localități din Bulgaria",
    },
    "rank_in_region": {
        "en": "in {region} region",
        "bg": "в област {region}",
        "ru": "в области {region}",
        "ro": "în regiunea {region}",
    },
    "rank_item": {
        "en": "**#{rank} of {total}** {where} (towns with {minimum}+ students)",
        "bg": "**#{rank} от {total}** {where} (населени места с {minimum}+ явили се)",
        "ru": "**№{rank} из {total}** {where} (пункты, где учеников от {minimum})",
        "ro": "**#{rank} din {total}** {where} (localități cu {minimum}+ elevi)",
    },
    "town_rank": {
        "en": "- Town rank (average of both subjects): {ranks}",
        "bg": "- Място на населеното място (средно от двата предмета): {ranks}",
        "ru": "- Место населённого пункта (среднее по обоим предметам): {ranks}",
        "ro": "- Locul localității (media ambelor materii): {ranks}",
    },
    "not_ranked": {
        "en": "- Town rank: not ranked, fewer than {minimum} students took each exam",
        "bg": "- Място на населеното място: не е класирано, по-малко от {minimum} явили се на всеки изпит",
        "ru": "- Место населённого пункта: нет в рейтинге, каждый экзамен сдавали менее {minimum} учеников",
        "ro": "- Locul localității: fără loc în clasament, mai puțin de {minimum} elevi au dat fiecare examen",
    },
    "no_match": {
        "en": "No schools match your search.",
        "bg": "Няма училища, които отговарят на търсенето.",
        "ru": "Нет школ, подходящих под ваш поиск.",
        "ro": "Nicio școală nu corespunde căutării tale.",
    },

    # --- The Top 5 tab and the AI overview ---
    "top_intro": {
        "en": "For the chosen exam and region, ranked by the **average of both subjects**. Towns need at least {min_town} students in each exam ({min_town_region} inside one region), and schools at least {min_school}. The tables come from the data; the text below them is written by {model} on this computer, or by the program itself when the AI isn't available.",
        "bg": "За избрания изпит и област, подредени по **средното от двата предмета**. Населените места трябва да имат поне {min_town} явили се на всеки изпит ({min_town_region} в рамките на една област), а училищата поне {min_school}. Таблиците са от данните; текстът под тях е написан от {model} на този компютър или от самата програма, когато ИИ не е наличен.",
        "ru": "Для выбранного экзамена и области, рейтинг по **среднему по обоим предметам**. В населённом пункте должно быть не менее {min_town} учеников на каждом экзамене ({min_town_region} внутри одной области), в школе — не менее {min_school}. Таблицы взяты из данных; текст под ними пишет {model} на этом компьютере или сама программа, если ИИ недоступен.",
        "ro": "Pentru examenul și regiunea alese, clasament după **media ambelor materii**. Localitățile au nevoie de cel puțin {min_town} elevi la fiecare examen ({min_town_region} în interiorul unei regiuni), iar școlile de cel puțin {min_school}. Tabelele vin din date; textul de sub ele este scris de {model} pe acest calculator sau de programul însuși când AI-ul nu este disponibil.",
    },
    "top_towns_table": {
        "en": "Top {top} towns",
        "bg": "Първите {top} населени места",
        "ru": "Топ-{top} населённых пунктов",
        "ro": "Top {top} localități",
    },
    "top_schools_table": {
        "en": "Top {top} schools",
        "bg": "Първите {top} училища",
        "ru": "Топ-{top} школ",
        "ro": "Top {top} școli",
    },
    "area_all": {
        "en": "Bulgaria (all regions)",
        "bg": "България (всички области)",
        "ru": "Болгария (все области)",
        "ro": "Bulgaria (toate regiunile)",
    },
    "amount_above": {
        "en": "{amount} above",
        "bg": "с {amount} над",
        "ru": "на {amount} выше",
        "ro": "cu {amount} peste",
    },
    "amount_below": {
        "en": "{amount} below",
        "bg": "с {amount} под",
        "ru": "на {amount} ниже",
        "ro": "cu {amount} sub",
    },
    "not_enough_data": {
        "en": "Not enough data to rank: no town or school in {area} is big enough.",
        "bg": "Няма достатъчно данни за класиране: нито едно населено място или училище в {area} не е достатъчно голямо.",
        "ru": "Недостаточно данных для рейтинга: {area} — нет достаточно крупного населённого пункта или школы.",
        "ro": "Prea puține date pentru un clasament: nicio localitate și nicio școală din {area} nu este destul de mare.",
    },
    "heading_towns": {
        "en": "Top towns",
        "bg": "Най-добри населени места",
        "ru": "Лучшие населённые пункты",
        "ro": "Primele localități",
    },
    "heading_schools": {
        "en": "Top schools",
        "bg": "Най-добри училища",
        "ru": "Лучшие школы",
        "ro": "Primele școli",
    },
    "no_town_ranked": {
        "en": "No town in {area} has enough students to be ranked.",
        "bg": "Нито едно населено място в {area} няма достатъчно явили се, за да бъде класирано.",
        "ru": "{area}: ни в одном населённом пункте нет достаточно учеников для рейтинга.",
        "ro": "Nicio localitate din {area} nu are destui elevi pentru a intra în clasament.",
    },
    "no_school_ranked": {
        "en": "No school in {area} has enough students to be ranked.",
        "bg": "Нито едно училище в {area} няма достатъчно явили се, за да бъде класирано.",
        "ru": "{area}: ни в одной школе нет достаточно учеников для рейтинга.",
        "ro": "Nicio școală din {area} nu are destui elevi pentru a intra în clasament.",
    },
    "best_towns_intro": {
        "en": "The best towns in {area}, ranked by the average of both subjects:",
        "bg": "Най-добрите населени места в {area}, подредени по средното от двата предмета:",
        "ru": "Лучшие населённые пункты ({area}), рейтинг по среднему по обоим предметам:",
        "ro": "Cele mai bune localități din {area}, în ordinea mediei ambelor materii:",
    },
    "best_schools_intro": {
        "en": "The best schools in {area}, ranked by the average of both subjects:",
        "bg": "Най-добрите училища в {area}, подредени по средното от двата предмета:",
        "ru": "Лучшие школы ({area}), рейтинг по среднему по обоим предметам:",
        "ro": "Cele mai bune școli din {area}, în ordinea mediei ambelor materii:",
    },
    "town_item": {
        "en": "{rank}. **{town}**: {score}, {difference} the area's average",
        "bg": "{rank}. **{town}**: {score}, {difference} средното",
        "ru": "{rank}. **{town}**: {score}, {difference} среднего значения",
        "ro": "{rank}. **{town}**: {score}, {difference} media zonei",
    },
    "school_item": {
        "en": "{rank}. **{school}** ({town}): {score}, {difference} the area's average",
        "bg": "{rank}. **{school}** ({town}): {score}, {difference} средното",
        "ru": "{rank}. **{school}** ({town}): {score}, {difference} среднего значения",
        "ro": "{rank}. **{school}** ({town}): {score}, {difference} media zonei",
    },
    "all_top_in": {
        "en": "All of the top schools are in {town}.",
        "bg": "Всички най-добри училища са в {town}.",
        "ru": "Все лучшие школы находятся здесь: {town}.",
        "ro": "Toate școlile din top sunt în {town}.",
    },
    "most_top_in": {
        "en": "Most of the top schools are in {town}.",
        "bg": "Повечето от най-добрите училища са в {town}.",
        "ru": "Большинство лучших школ находится здесь: {town}.",
        "ro": "Majoritatea școlilor din top sunt în {town}.",
    },
    "ollama_not_running": {
        "en": "Ollama isn't running: start the Ollama app to get the AI overview.",
        "bg": "Ollama не работи: стартирайте приложението Ollama, за да получите ИИ обзора.",
        "ru": "Ollama не запущена: запустите приложение Ollama, чтобы получить обзор ИИ.",
        "ro": "Ollama nu rulează: pornește aplicația Ollama pentru a primi prezentarea AI.",
    },
    "model_missing": {
        "en": "{model} isn't downloaded: run `ollama pull {model}` in a terminal.",
        "bg": "{model} не е изтеглен: изпълнете `ollama pull {model}` в терминал.",
        "ru": "{model} не загружена: выполните `ollama pull {model}` в терминале.",
        "ro": "{model} nu este descărcat: rulează `ollama pull {model}` într-un terminal.",
    },
    "written_without_ai": {
        "en": "*Written by the program, without AI. {problem}*",
        "bg": "*Написано от програмата, без ИИ. {problem}*",
        "ru": "*Написано программой, без ИИ. {problem}*",
        "ro": "*Scris de program, fără AI. {problem}*",
    },
    "ai_writing": {
        "en": "*{model} is writing the overview - this takes 1 to 3 minutes on this computer...*",
        "bg": "*{model} пише обзора - това отнема от 1 до 3 минути на този компютър...*",
        "ru": "*{model} пишет обзор - на этом компьютере это занимает от 1 до 3 минут...*",
        "ro": "*{model} scrie prezentarea - durează între 1 și 3 minute pe acest calculator...*",
    },
    "ai_failed": {
        "en": "*Written by the program, because the AI stopped with an error: {error}*",
        "bg": "*Написано от програмата, защото ИИ спря с грешка: {error}*",
        "ru": "*Написано программой, потому что ИИ остановился с ошибкой: {error}*",
        "ro": "*Scris de program, pentru că AI-ul s-a oprit cu o eroare: {error}*",
    },

    # --- The map tab ---
    "map_intro": {
        "en": "The 28 regions for the chosen exam, always compared with the **Bulgarian average**, which cancels out how easy or hard each year's test was. **Dark red** = far below (or fell behind), **yellow** = about average (or no change), **light green** = far above (or improved). Darker always means lower. The map always shows the whole country.",
        "bg": "28-те области за избрания изпит, винаги сравнени със **средното за България**, което премахва влиянието на това колко лесен или труден е бил тестът през всяка година. **Тъмночервено** = много под (или изостава), **жълто** = около средното (или без промяна), **светлозелено** = много над (или се подобрява). По-тъмното винаги означава по-ниско. Картата винаги показва цялата страна.",
        "ru": "28 областей для выбранного экзамена, всегда в сравнении со **средним по Болгарии**, что убирает влияние того, насколько лёгким или трудным был тест в каждом году. **Тёмно-красный** = намного ниже (или отстала), **жёлтый** = около среднего (или без изменений), **светло-зелёный** = намного выше (или улучшилась). Темнее всегда значит ниже. Карта всегда показывает всю страну.",
        "ro": "Cele 28 de regiuni pentru examenul ales, comparate mereu cu **media Bulgariei**, ceea ce anulează cât de ușor sau de greu a fost testul din fiecare an. **Roșu închis** = mult sub medie (sau a rămas în urmă), **galben** = cam la medie (sau nicio schimbare), **verde deschis** = mult peste medie (sau s-a îmbunătățit). Mai închis înseamnă mereu mai slab. Harta arată mereu toată țara.",
    },
    "view_difference": {
        "en": "Difference from Bulgaria",
        "bg": "Разлика от България",
        "ru": "Отличие от Болгарии",
        "ro": "Diferența față de Bulgaria",
    },
    "view_change": {
        "en": "Change since the previous year",
        "bg": "Промяна спрямо предходната година",
        "ru": "Изменение за год",
        "ro": "Schimbarea față de anul precedent",
    },
    "view_trends": {
        "en": "Trends over the years",
        "bg": "Тенденции през годините",
        "ru": "Тренды по годам",
        "ro": "Tendințele de-a lungul anilor",
    },
    "colour_by": {
        "en": "Colour by",
        "bg": "Оцвети по",
        "ru": "Цвет по",
        "ro": "Colorează după",
    },
    "map_note": {
        "en": "Colours show differences in exam results, not the quality of the schools: results also depend on family income, town or village, and which students sit the exam.",
        "bg": "Цветовете показват разлики в изпитните резултати, а не качеството на училищата: резултатите зависят и от доходите на семействата, от това дали е град или село и кои ученици се явяват на изпита.",
        "ru": "Цвета показывают различия в результатах экзаменов, а не качество школ: результаты также зависят от доходов семей, от того, город это или село, и от того, какие ученики сдают экзамен.",
        "ro": "Culorile arată diferențe între rezultatele la examene, nu calitatea școlilor: rezultatele depind și de venitul familiilor, de oraș sau sat și de elevii care dau examenul.",
    },
    "borders_credit": {
        "en": "Region borders: Natural Earth (public domain).",
        "bg": "Граници на областите: Natural Earth (обществено достояние).",
        "ru": "Границы областей: Natural Earth (общественное достояние).",
        "ro": "Granițele regiunilor: Natural Earth (domeniu public).",
    },
    "chart_map": {
        "en": "Map",
        "bg": "Карта",
        "ru": "Карта",
        "ro": "Harta",
    },
    "chart_bars": {
        "en": "All regions, best at the top",
        "bg": "Всички области, най-добрите отгоре",
        "ru": "Все области, лучшие вверху",
        "ro": "Toate regiunile, cea mai bună sus",
    },
    "chart_change_map": {
        "en": "Map: change since the previous year",
        "bg": "Карта: промяна спрямо предходната година",
        "ru": "Карта: изменение за год",
        "ro": "Harta: schimbarea față de anul precedent",
    },
    "chart_change_bars": {
        "en": "All regions, most improved at the top",
        "bg": "Всички области, най-подобрилите се отгоре",
        "ru": "Все области, больше всего улучшились вверху",
        "ro": "Toate regiunile, cea mai îmbunătățită sus",
    },
    "chart_trend_grid": {
        "en": "Every region, year by year (best at the top)",
        "bg": "Всяка област, година по година (най-добрите отгоре)",
        "ru": "Каждая область по годам (лучшие вверху)",
        "ro": "Fiecare regiune, an de an (cea mai bună sus)",
    },
    "chart_trend_gap": {
        "en": "Gap between the best and worst region",
        "bg": "Разлика между най-добрата и най-слабата област",
        "ru": "Разрыв между лучшей и худшей областью",
        "ro": "Decalajul dintre cea mai bună și cea mai slabă regiune",
    },
    "map_missing": {
        "en": "The map file {file} is missing: it must be next to this script.",
        "bg": "Липсва файлът на картата {file}: той трябва да е до този скрипт.",
        "ru": "Файл карты {file} отсутствует: он должен лежать рядом с этим скриптом.",
        "ro": "Fișierul hărții {file} lipsește: trebuie să fie lângă acest script.",
    },
    "no_results_subject": {
        "en": "No results for {subject} in {choice}.",
        "bg": "Няма резултати за {subject} в {choice}.",
        "ru": "Нет результатов: {subject}, {choice}.",
        "ro": "Niciun rezultat pentru {subject} în {choice}.",
    },
    "unit_points": {
        "en": "points",
        "bg": "точки",
        "ru": "баллов",
        "ro": "puncte",
    },
    "unit_grade": {
        "en": "grade",
        "bg": "успех",
        "ru": "оценка",
        "ro": "notă",
    },
    "none": {
        "en": "none",
        "bg": "няма",
        "ru": "нет",
        "ro": "niciuna",
    },

    # Difference from Bulgaria
    "map_head": {
        "en": "**{choice}** · {subject} · Bulgaria: average **{national}** {unit}",
        "bg": "**{choice}** · {subject} · България: среден резултат **{national}** {unit}",
        "ru": "**{choice}** · {subject} · Болгария: в среднем **{national}** {unit}",
        "ro": "**{choice}** · {subject} · Bulgaria: media **{national}** {unit}",
    },
    "best_worst": {
        "en": "- Best region: **{best}** {best_score} ({best_difference}) · worst region: **{worst}** {worst_score} ({worst_difference}) · gap: **{gap}** {unit}",
        "bg": "- Най-добра област: **{best}** {best_score} ({best_difference}) · най-слаба област: **{worst}** {worst_score} ({worst_difference}) · разлика: **{gap}** {unit}",
        "ru": "- Лучшая область: **{best}** {best_score} ({best_difference}) · худшая область: **{worst}** {worst_score} ({worst_difference}) · разрыв: **{gap}** {unit}",
        "ro": "- Cea mai bună regiune: **{best}** {best_score} ({best_difference}) · cea mai slabă regiune: **{worst}** {worst_score} ({worst_difference}) · decalaj: **{gap}** {unit}",
    },
    "cities_villages": {
        "en": "- Cities (ГР.): {cities} · villages (С.): {villages} · gap: **{gap}** {unit}",
        "bg": "- Градове (ГР.): {cities} · села (С.): {villages} · разлика: **{gap}** {unit}",
        "ru": "- Города (ГР.): {cities} · сёла (С.): {villages} · разрыв: **{gap}** {unit}",
        "ro": "- Orașe (ГР.): {cities} · sate (С.): {villages} · decalaj: **{gap}** {unit}",
    },
    "hover_average": {
        "en": "Average",
        "bg": "Средно",
        "ru": "Среднее",
        "ro": "Media",
    },
    "hover_vs_bulgaria": {
        "en": "vs Bulgaria",
        "bg": "спрямо България",
        "ru": "К Болгарии",
        "ro": "față de Bulgaria",
    },
    "hover_schools": {
        "en": "Schools",
        "bg": "Училища",
        "ru": "Школ",
        "ro": "Școli",
    },
    "key_vs_bulgaria": {
        "en": "vs Bulgaria<br>({unit})",
        "bg": "спрямо България<br>({unit})",
        "ru": "К Болгарии<br>({unit})",
        "ro": "față de Bulgaria<br>({unit})",
    },
    "zero_average": {
        "en": "0 = average",
        "bg": "0 = средното",
        "ru": "0 = среднее",
        "ro": "0 = media",
    },
    "bars_axis": {
        "en": "Difference from the Bulgarian average ({unit})",
        "bg": "Разлика от средното за България ({unit})",
        "ru": "Отличие от среднего по Болгарии ({unit})",
        "ro": "Diferența față de media Bulgariei ({unit})",
    },

    # Change since the previous year
    "first_year": {
        "en": "**{choice}** is the first year in the data for this exam, so there's no previous year to compare with.",
        "bg": "**{choice}** е първата година в данните за този изпит, така че няма предходна година за сравнение.",
        "ru": "**{choice}** — первый год в данных для этого экзамена, поэтому сравнивать не с чем.",
        "ro": "**{choice}** este primul an din date pentru acest examen, deci nu există un an precedent cu care să-l comparăm.",
    },
    "hover_change": {
        "en": "Change",
        "bg": "Промяна",
        "ru": "Изменение",
        "ro": "Schimbare",
    },
    "hover_vs_bulgaria_in": {
        "en": "vs Bulgaria in {year}",
        "bg": "спрямо България през {year}",
        "ru": "К Болгарии в {year}",
        "ro": "față de Bulgaria în {year}",
    },
    "change_head": {
        "en": "**{exam}: {before} → {now}** · {subject} · how far each region moved compared with the Bulgarian average",
        "bg": "**{exam}: {before} → {now}** · {subject} · колко се е преместила всяка област спрямо средното за България",
        "ru": "**{exam}: {before} → {now}** · {subject} · насколько каждая область сдвинулась относительно среднего по Болгарии",
        "ro": "**{exam}: {before} → {now}** · {subject} · cât s-a mișcat fiecare regiune față de media Bulgariei",
    },
    "improved_most": {
        "en": "- Improved most: {regions}",
        "bg": "- Най-много се подобриха: {regions}",
        "ru": "- Больше всего улучшились: {regions}",
        "ro": "- S-au îmbunătățit cel mai mult: {regions}",
    },
    "fell_behind_most": {
        "en": "- Fell behind most: {regions}",
        "bg": "- Най-много изостанаха: {regions}",
        "ru": "- Больше всего отстали: {regions}",
        "ro": "- Au rămas cel mai mult în urmă: {regions}",
    },
    "typical_movement": {
        "en": "- Typical movement: {amount} {unit}. Smaller changes are often just year-to-year noise.",
        "bg": "- Обичайна промяна: {amount} {unit}. По-малките промени често са просто случайни колебания от година на година.",
        "ru": "- Типичный сдвиг: {amount} {unit}. Небольшие изменения часто — просто случайные колебания от года к году.",
        "ro": "- Mișcarea obișnuită: {amount} {unit}. Schimbările mai mici sunt adesea doar zgomot de la un an la altul.",
    },
    "national_moved": {
        "en": "- Bulgaria's own average went from {before} to {now} ({change}). That mostly reflects how hard each year's test was, which is why regions are compared with the national average.",
        "bg": "- Средното за самата България се промени от {before} на {now} ({change}). Това отразява най-вече колко труден е бил тестът през всяка година, затова областите се сравняват със средното за страната.",
        "ru": "- Среднее по самой Болгарии изменилось с {before} до {now} ({change}). В основном это отражает сложность теста в каждом году, поэтому области сравниваются со средним по стране.",
        "ro": "- Media Bulgariei însăși a trecut de la {before} la {now} ({change}). Asta arată mai ales cât de greu a fost testul din fiecare an, de aceea regiunile sunt comparate cu media națională.",
    },
    "key_change": {
        "en": "Change<br>({unit})",
        "bg": "Промяна<br>({unit})",
        "ru": "Изменение<br>({unit})",
        "ro": "Schimbare<br>({unit})",
    },
    "zero_no_change": {
        "en": "0 = no change",
        "bg": "0 = без промяна",
        "ru": "0 = без изменений",
        "ro": "0 = nicio schimbare",
    },
    "change_axis": {
        "en": "Change vs the Bulgarian average ({unit})",
        "bg": "Промяна спрямо средното за България ({unit})",
        "ru": "Изменение к среднему по Болгарии ({unit})",
        "ro": "Schimbarea față de media Bulgariei ({unit})",
    },

    # Trends over the years
    "one_year_only": {
        "en": "There's only one year of {exam} in the data, so there's no trend to show yet.",
        "bg": "В данните има само една година за {exam}, така че все още няма тенденция за показване.",
        "ru": "В данных есть только один год ({exam}), поэтому тренд пока показать нельзя.",
        "ro": "Există un singur an de {exam} în date, deci încă nu există o tendință de arătat.",
    },
    "trends_head": {
        "en": "**{exam}, {first} – {last}** · {subject} · each region's distance from the Bulgarian average, year by year",
        "bg": "**{exam}, {first} – {last}** · {subject} · разстоянието на всяка област от средното за България, година по година",
        "ru": "**{exam}, {first} – {last}** · {subject} · отклонение каждой области от среднего по Болгарии по годам",
        "ro": "**{exam}, {first} – {last}** · {subject} · distanța fiecărei regiuni față de media Bulgariei, an de an",
    },
    "gap_line": {
        "en": "- Gap between the best and worst region: {first_gap} in {first} → **{last_gap}** in {last} ({change} {unit})",
        "bg": "- Разлика между най-добрата и най-слабата област: {first_gap} през {first} → **{last_gap}** през {last} ({change} {unit})",
        "ru": "- Разрыв между лучшей и худшей областью: {first_gap} в {first} → **{last_gap}** в {last} ({change} {unit})",
        "ro": "- Decalajul dintre cea mai bună și cea mai slabă regiune: {first_gap} în {first} → **{last_gap}** în {last} ({change} {unit})",
    },
    "relative_line": {
        "en": "- The same gap compared with how spread out the schools' results were that year: {first_relative} → **{last_relative}** times the spread ({drift}). Some years' tests spread students further apart, which widens the gap by itself.",
        "bg": "- Същата разлика, сравнена с разсейването на резултатите на училищата през съответната година: {first_relative} → **{last_relative}** пъти разсейването ({drift}). Тестовете в някои години раздалечават учениците повече, което само по себе си увеличава разликата.",
        "ru": "- Тот же разрыв в сравнении с разбросом результатов школ в том году: {first_relative} → **{last_relative}** разброса ({drift}). В некоторые годы тесты сильнее разводят учеников, и это само по себе увеличивает разрыв.",
        "ro": "- Același decalaj comparat cu cât de împrăștiate au fost rezultatele școlilor în acel an: {first_relative} → **{last_relative}** ori împrăștierea ({drift}). În unii ani testele îi împrăștie mai mult pe elevi, ceea ce mărește singur decalajul.",
    },
    "caught_up_since": {
        "en": "- Caught up most since {first}: {regions}",
        "bg": "- Най-много наваксаха от {first} насам: {regions}",
        "ru": "- Больше всего догнали с {first}: {regions}",
        "ro": "- Au recuperat cel mai mult din {first}: {regions}",
    },
    "fell_behind_since": {
        "en": "- Fell behind most since {first}: {regions}",
        "bg": "- Най-много изостанаха от {first} насам: {regions}",
        "ru": "- Больше всего отстали с {first}: {regions}",
        "ro": "- Au rămas cel mai mult în urmă din {first}: {regions}",
    },
    "every_year": {
        "en": "- Regions below the national average in every year: {below} · above it in every year: {above}",
        "bg": "- Области под средното за страната през всяка година: {below} · над него през всяка година: {above}",
        "ru": "- Области ниже среднего по стране во все годы: {below} · выше него во все годы: {above}",
        "ro": "- Regiuni sub media națională în fiecare an: {below} · peste ea în fiecare an: {above}",
    },
    "endpoints_note": {
        "en": "- Caught up and fell behind compare only the first and the last year, so one unusual year at either end can change them.",
        "bg": "- Наваксалите и изостаналите се определят само по първата и последната година, така че една необичайна година в единия край може да ги промени.",
        "ru": "- «Догнали» и «отстали» сравнивают только первый и последний год, поэтому один необычный год на любом конце может их изменить.",
        "ro": "- Recuperarea și rămânerea în urmă compară doar primul și ultimul an, așa că un singur an neobișnuit la oricare capăt le poate schimba.",
    },
    "drift_apart": {
        "en": "the regions drifted apart",
        "bg": "областите се раздалечиха",
        "ru": "области разошлись",
        "ro": "regiunile s-au îndepărtat",
    },
    "drift_closer": {
        "en": "the regions came closer",
        "bg": "областите се сближиха",
        "ru": "области сблизились",
        "ro": "regiunile s-au apropiat",
    },
    "drift_same": {
        "en": "about the same",
        "bg": "почти без промяна",
        "ru": "примерно так же",
        "ro": "cam la fel",
    },
    "hover_gap": {
        "en": "Gap",
        "bg": "Разлика",
        "ru": "Разрыв",
        "ro": "Decalaj",
    },
    "hover_times_spread": {
        "en": "times the spread of the schools' results",
        "bg": "пъти разсейването на резултатите на училищата",
        "ru": "разброса результатов школ",
        "ro": "ori împrăștierea rezultatelor școlilor",
    },
    "gap_axis": {
        "en": "Best region minus worst ({unit})",
        "bg": "Разлика ({unit})",
        "ru": "Разрыв ({unit})",
        "ro": "Decalaj ({unit})",
    },
}


def translate(key, language, **values):
    """
    The text called `key` in the chosen language, with the {names} in it filled in from `values`.
    translate("region_name", "en", region="ВАРНА") gives "ВАРНА region"
    """
    text = TEXTS[key][language]
    # Only fill in texts that need it: Plotly's own "%{x}" codes must not be touched
    return text.format(**values) if values else text


def whole_number(number, language):
    """
    A whole number with its thousands separated: "53,739" in English, "53 739" in the other
    languages, where a comma would be read as a decimal comma
    """
    text = f"{int(number):,}"
    return text if language == "en" else text.replace(",", " ")


def missing_translations():
    """
    The texts that are missing in some language, like ["intro (ro)"]. The app checks this at start
    """
    return [f"{key} ({language})" for key, texts in TEXTS.items() for language in LANGUAGES if not texts.get(language)]
