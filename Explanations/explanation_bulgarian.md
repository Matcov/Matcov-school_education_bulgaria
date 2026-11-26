# Как работи `alex_school_results.py` — обяснено просто

Това ръководство е за хора, които **тепърва започват с Python**. То обяснява с прости думи всяка
функция (`def`) в [alex_school_results.py](../alex_school_results.py) и после показва как работят
заедно. Обяснява и [translations.py](../translations.py) — файла с всички текстове на страницата
на 4 езика.

Как да го четете:
1. Прочетете **„Какво прави програмата“** и **„Думи, които ще срещнете“**.
2. Разгледайте **диаграмата** в раздел 4.
3. Прочетете функциите. Всяка има връзка към своя ред в кода (номерата на редовете са към
   26 ноември 2026 г.).

---

## 1. Какво прави програмата

1. **Пази** официалните изпитни резултати на всяко училище в България в **локална база данни** —
   файла `school_results.db`. Министерството на образованието и науката (МОН) ги публикува в
   интернет; програмата ги изтегля само първия път или когато щракнете зеления бутон
   **Провери за нови резултати**.
2. **Почиства** данните, докато ги изтегля, защото са разхвърляни: имена, написани по различен
   начин, числа със запетаи и т.н.
3. **Показва** резултатите на уеб страница във вашия браузър, направена с библиотеката Gradio.
4. На страницата **избирате** изпит, учебна година, област и населено място. Програмата
   **подрежда** училищата и населените места в класация.
5. Ако искате, **локален изкуствен интелект** (моделът gemma4, който работи в Ollama на вашия
   компютър) пише кратък обзор на първите 5 населени места и училища. Ако ИИ не е наличен,
   програмата сама пише по-опростен обзор.
6. **Карта на 28-те области** оцветява всяка област според това колко се отличават резултатите ѝ
   от средното за страната — от тъмночервено (много под) до светлозелено (много над), до стълбова
   диаграма с точните числа.
7. Три бутона в раздела с картата превключват между три **изгледа**: тази разлика от средното за
   страната, **промяната спрямо предходната година** и **тенденциите през годините**.
8. Страницата е на **4 езика**: български, английски, руски и румънски. Четири сини бутона до
   заглавието (EN, BG, RU, RO) превключват между тях. Българската страница е на основния адрес
   (http://127.0.0.1:7860), а другите — на `/en`, `/ru` и `/ro`. Всички текстове на страницата са
   във файла `translations.py`. Имената на училищата, населените места и областите остават на
   кирилица, както са в данните, а числата запазват десетичната точка на всеки език.

**Изпитите:**
- **НВО** (национално външно оценяване) в 4., 7. и 10. клас: точки от 0 до 100 по български
  език и литература (**BEL**) и математика (**MAT**).
- **ДЗИ** (държавни зрелостни изпити, матури) в 12. клас: оценки от 2 до 6 по български език и
  по втори изпит.

---

## 2. Думи, които ще срещнете

| Дума | Значение |
|---|---|
| **функция** (`def`) | Рецепта с име. Давате ѝ съставки (**параметри**), тя прави няколко стъпки и връща резултат (**`return`**). Пример: `def add(a, b): return a + b` → `add(2, 3)` дава `5`. |
| **извикване** на функция | Използването ѝ: `tidy_town("ГР. СОФИЯ")`. „A извиква B“ означава, че функцията A използва функцията B. |
| **`None`** | Думата на Python за „нищо, няма стойност“. |
| **низ** (string) | Текст в кавички: `"Варна"`. |
| **списък** (list) `[ ]` | Няколко стойности подред: `["Варна", "Бургас"]`. |
| **кортеж** (tuple) `( )` | Като списък, но не се променя: `("ГР.ВАРНА", "ВАРНА")`. Функция може да върне две стойности като кортеж. |
| **речник** (dictionary) `{ }` | Двойки *ключ → стойност*, като телефонен указател: `{"NVO 7th grade": "b56288b6-..."}`. |
| **таблица** (pandas `DataFrame`) | Лист като в Excel, но вътре в Python: редове и колони. |
| **база данни** (SQLite) | Файл, който пази таблици и в който се търси бързо. SQLite е вградена в Python, а цялата база е един файл — тук `school_results.db`. |
| **SQL** | Езикът, с който се задават въпроси на база данни. `SELECT school FROM results WHERE town = 'ГР.ВАРНА'` означава „дай ми училищата във Варна“. |
| **транзакция** | Няколко промени в база данни, които стават **всички заедно или никоя**. Ако нещо се провали по средата, нищо не остава записано наполовина. |
| **API** | Уебсайт, направен за **програми**, а не за хора: изпращате въпрос и получавате данни. |
| **JSON** | Текстов формат за данни, който прилича на речниците и списъците в Python. API-тата отговарят в JSON. |
| **грешка** (изключение, exception) | Сигналът на Python, че „нещо се е объркало“. `raise` изпраща такъв сигнал; `try:` … `except:` го хваща, за да може програмата да реагира. `finally:` се изпълнява винаги — с грешка или без. |
| **`_`** | Име за стойност, която **не ни трябва**: `kind, table = …` срещу `_, table = …`. |
| **декоратор** (`@cache`) | Етикет над функция, който ѝ дава допълнителна способност. `@cache` ѝ дава памет. |
| **генератор** (`yield`) | Функция, която връща резултатите **на части**, а не наведнъж с `return`. Използва се, за да се показва текстът на ИИ дума по дума. |
| **вътрешна функция** | Функция, написана вътре в друга функция. |
| **събитие** (event) | Нещо, което се случва на уеб страницата (щракване, нов избор). Тогава Gradio извиква функция. |
| **константа** | Настройка, написана с ГЛАВНИ букви в началото на файла, напр. `TOP = 5`. Не се променя, докато програмата работи. |
| **състояние** (`gr.State`) | Стойност, която Gradio **помни** за всеки посетител на страницата, без да я показва. Тук: кой от трите изгледа на картата сте избрали. |
| **медиана** | Средната по ред стойност: половината числа са по-малки, половината — по-големи. При четен брой числа е средното на двете в средата. За разлика от обикновената средна стойност, едно крайно число почти не я мести. |
| **импортиране** (`import`) | Взема имена от друг файл на Python. `from translations import translate` позволява на този файл да използва функцията `translate()`, написана в `translations.py`. |
| **ключ за превод** | Името на един текст в `translations.py`, като `"check_button"`. Кодът иска текст по ключа и езика му: `translate("check_button", "bg")` дава „Провери за нови резултати“. |
| **заместител** `{name}` | Празно място в текст, във фигурни скоби, което се попълва със стойност: `"Училища: {count}"` става „Училища: 1 738“. |
| **код на език** | Две букви за език: `en` английски, `bg` български, `ru` руски, `ro` румънски. Всяка функция на страницата получава такъв код в параметъра си `language`. |
| **двойка (етикет, стойност)** | Елемент от списък, направен от две части: **етикетът**, който виждате, и **стойността**, която получава кодът. На български списъкът показва „НВО 7. клас - 2025/2026“, но кодът пак получава „NVO 7th grade - 2025/2026“. Така кодът работи еднакво на всеки език. |
| **маршрут** (route) | Още една страница на приложение на Gradio, на собствен адрес. `/en` е маршрутът на английската страница. |

---

## 3. Настройките в началото на файла (редове 60–204)

| Настройка | Какво е |
|---|---|
| `from translations import …` | Взема настройките за езиците и трите функции за текстове от `translations.py` (вижте Група 8). Този файл трябва да е до скрипта |
| `MON_OPEN_DATA_PAGE` | Страницата на министерството, която ни казва къде са данните |
| `PORTAL_API` | Адресът на API-то на Портала за отворени данни (data.egov.bg) |
| `KNOWN_MINISTRY_ID` | Идентификаторът (ID) на министерството в портала, за случая, когато mon.bg не работи |
| `headers` | Казва честно на сайтовете кой пита |
| `MODEL`, `THINK` | Моделът на ИИ (`gemma4`) и „не мисли на глас“, за да е по-бърз |
| `EXAMS` | Четирите изпита, с вида им (`"nvo"` или `"dzi"`) и името на набора им от данни в портала |
| `RESULT_COLUMNS` | Имената на четирите колони с резултати за всеки вид изпит |
| `ALL_REGIONS`, `ALL_TOWNS`, `RANK_BY` | Стойностите, които кодът използва за „All regions“ (всички области), „All towns“ (всички населени места) и двата начина за подреждане на училищата. Остават на английски на всеки език; страницата ги показва преведени |
| `ABROAD` | `"ЧУЖБИНА"` — „областта“ на българските училища в други държави |
| `TOP` | Колко населени места и училища показва обзорът на ИИ (5) |
| `MIN_TOWN_STUDENTS`, `MIN_TOWN_STUDENTS_IN_REGION`, `MIN_SCHOOL_STUDENTS` | Минималният брой ученици (100, 30, 10), за да влезеш в класацията, така че малки села да не печелят |
| `BOM` | Невидим символ, с който започват някои файлове |
| `DATABASE_FILE` | Къде е базата данни: файлът `school_results.db` до скрипта |
| `DATABASE_TABLES` | Трите таблици на базата, написани на SQL: `files`, `results` и `checks`. Създават се, когато файлът се отвори за първи път |
| `DATABASE_COLUMNS` | Имената на колоните с резултати в базата (`region`, `school`, `bel_average`…) |
| `REGION_MAP_FILE` | Къде са границите на областите за картата: файлът `bulgaria_regions.geojson` до скрипта |
| `MAP_SUBJECTS` | По какво може да се оцвети картата: двата предмета, български език или математика / втори изпит. На английски, като `RANK_BY`: страницата ги показва преведени |
| `MAP_COLOURS` | Цветовете на картата — от тъмночервено (много под средното) до светлозелено (много над). Освен това стават все по-светли, така че по-тъмно винаги означава по-слабо |
| `MAP_VIEWS` | Имената на трите изгледа в раздела с картата: `"difference"`, `"change"` и `"trends"`. Надписът на всеки бутон е текстът `"view_<name>"` в `translations.py`, като `"view_change"` → „Промяна спрямо предходната година“ |
| `overview_system_prompt` | Правилата, които ИИ трябва да спазва, когато пише обзора. Има три заместителя, които попълва `overview_messages()`: `{language}` (езикът, на който да пише) и `{towns_heading}`, `{schools_heading}` (двете заглавия, преведени) |

---

## 4. Голямата картина: как са свързани функциите

Как да четете диаграмата:
- **Стрелка** `A → B` означава „A **извиква** B“.
- **Пунктирна стрелка** означава „създава“ или „после Gradio изпълнява“.
- **Цилиндър** е нещо извън кода: уебсайт, файл или ИИ на вашия компютър.
- Почти всяка функция, която пише текст на страницата, извиква `translate()` (група 8). За да
  остане диаграмата четима, стрелка към нея имат само малките помощници, направени за преводите.

> Диаграмата се вижда като картинка **в GitHub**. Във VS Code инсталирайте разширението
> *„Markdown Preview Mermaid Support“* или прочетете текстовата версия под диаграмата.

```mermaid
flowchart TD
    START(["Стартирате скрипта"]) --> n_main["main()"]

    subgraph g_helpers ["1 - Малки помощници"]
        n_tidy["tidy()"]
        n_tidy_town["tidy_town()"]
        n_to_number["to_number()"]
        n_exam_name["exam_name()"]
        n_choice_label["choice_label()"]
        n_choice_list["choice_list()"]
        n_subject_name["subject_name()"]
        n_shown_table["shown_table()"]
        n_weighted["weighted_average()"]
        n_town_label["town_label()"]
        n_split_label["split_town_label()"]
    end

    subgraph g_internet ["2 - Получаване на данните от интернет"]
        n_find_ministry["find_ministry_on_portal()"]
        n_find_datasets["find_exam_datasets()"]
        n_list_files["list_exam_files()"]
        n_download["download_results()"]
        n_call_portal["call_portal()"]
    end

    subgraph g_db ["3 - Базата данни"]
        n_update["update_database()"]
        n_save["save_results()"]
        n_stored["stored_files()"]
        n_read["read_results()"]
        n_status["database_status()"]
        n_open["open_database()"]
        n_load_choice["load_choice()"]
    end

    subgraph g_rank ["4 - Избор и класиране"]
        n_town_choices["town_choices()"]
        n_show_results["show_results()"]
        n_rank_towns["rank_towns()"]
        n_rank_schools["rank_schools()"]
    end

    subgraph g_ai ["5 - Обзор от ИИ"]
        n_write_overview["write_overview()"]
        n_overview_messages["overview_messages()"]
        n_template["template_overview()"]
        n_ollama_problem["ollama_problem()"]
    end

    subgraph g_map ["6 - Картата и трите ѝ изгледа"]
        n_show_map["show_map()"]
        n_show_change["show_change()"]
        n_show_trends["show_trends()"]
        n_exam_years["exam_years()"]
        n_region_gaps["region_gaps()"]
        n_schools_in_bulgaria["schools_in_bulgaria()"]
        n_subject_score["subject_score()"]
        n_school_spread["school_spread()"]
        n_drift_words["drift_words()"]
        n_load_region_map["load_region_map()<br/>с памет: @cache"]
        n_region_map["region_map()"]
        n_region_bars["region_bars()"]
        n_unit_word["unit_word()"]
        n_region_list["region_list()"]
        n_trend_heatmap["trend_heatmap()"]
        n_gap_trend_chart["gap_trend_chart()"]
        n_colour_key["colour_key()"]
        n_signed["signed()"]
        n_year_labels["year_labels()"]
    end

    subgraph g_page ["7 - Уеб страницата, направена от build_language_page() за всеки език"]
        n_build_app["build_app()"]
        n_build_language_page["build_language_page()"]
        n_language_buttons["language_buttons()"]
        n_api["api()"]
        n_show["show()"]
        n_refresh["refresh_towns()"]
        n_tab["show_schools_tab()"]
        n_overview["overview()"]
        n_map_view["map_view()"]
        n_difference_view["difference_view()"]
        n_change_view["change_view()"]
        n_trends_view["trends_view()"]
        n_check["check_for_new_results()"]
    end

    subgraph g_texts ["8 - Текстовете на 4 езика, в translations.py"]
        n_translate["translate()"]
        n_whole_number["whole_number()"]
        n_missing["missing_translations()"]
    end

    MON[("mon.bg")]
    PORTAL[("data.egov.bg")]
    DBFILE[("school_results.db")]
    OLLAMA[("Ollama с gemma4")]
    MAPFILE[("bulgaria_regions.geojson")]
    YOU(["Вие, в браузъра"])

    %% Стартиране на програмата
    n_main --> n_missing
    n_main --> n_stored
    n_main -->|само ако базата е празна| n_update
    n_main --> n_read
    n_main --> n_build_app
    n_main --> n_ollama_problem

    %% Базата данни
    n_update --> n_find_ministry
    n_update --> n_find_datasets
    n_update --> n_list_files
    n_update --> n_stored
    n_update --> n_download
    n_update --> n_save
    n_update --> n_open
    n_save --> n_open
    n_stored --> n_open
    n_read --> n_open
    n_status --> n_open
    n_open --> DBFILE
    n_load_choice --> n_read

    %% Получаване на данните от интернет
    n_find_ministry --> MON
    n_find_datasets --> n_call_portal
    n_find_datasets --> n_tidy
    n_list_files --> n_call_portal
    n_download --> n_call_portal
    n_download --> n_to_number
    n_download --> n_tidy_town
    n_call_portal --> PORTAL

    %% Уеб страницата
    n_build_app -->|по веднъж за всеки от 4-те езика| n_build_language_page
    n_build_language_page --> n_language_buttons
    n_build_language_page --> n_status
    n_build_language_page --> n_choice_list
    n_build_language_page --> n_town_choices
    n_build_language_page --> n_subject_name
    n_build_language_page -.->|създава| n_api
    n_build_language_page -.->|създава| n_show
    n_build_language_page -.->|създава| n_refresh
    n_build_language_page -.->|създава| n_tab
    n_build_language_page -.->|създава| n_overview
    n_build_language_page -.->|създава| n_map_view
    n_build_language_page -.->|създава| n_difference_view
    n_build_language_page -.->|създава| n_change_view
    n_build_language_page -.->|създава| n_trends_view
    n_build_language_page -.->|създава| n_check
    YOU -->|отваряне, ново място или класиране| n_show
    YOU -->|нов изпит или област| n_refresh
    YOU -->|Покажи резултатите или Enter| n_tab
    YOU -->|ИИ обзор на първите 5| n_overview
    YOU -->|раздел Карта и тенденции на областите, нов изпит или Оцвети по| n_map_view
    YOU -->|Разлика от България| n_difference_view
    YOU -->|Промяна спрямо предходната година| n_change_view
    YOU -->|Тенденции през годините| n_trends_view
    YOU -->|Провери за нови резултати| n_check
    n_refresh -.->|после| n_show
    n_tab -.->|после| n_show
    n_check --> n_update
    n_check --> n_stored
    n_check --> n_status
    n_check --> n_choice_list

    %% Избор и класиране
    n_show --> n_show_results
    n_refresh --> n_town_choices
    n_town_choices --> n_load_choice
    n_town_choices --> n_town_label
    n_show_results --> n_load_choice
    n_show_results --> n_split_label
    n_show_results --> n_weighted
    n_show_results --> n_rank_towns
    n_show_results --> n_choice_label
    n_show_results --> n_whole_number
    n_show_results --> n_shown_table
    n_rank_towns --> n_weighted

    %% Текстовете на 4 езика
    n_choice_list --> n_choice_label
    n_choice_label --> n_exam_name
    n_exam_name --> n_translate
    n_subject_name --> n_translate
    n_shown_table --> n_translate
    n_unit_word --> n_translate
    n_region_list --> n_translate

    %% Обзор от ИИ
    n_overview --> n_write_overview
    n_write_overview --> n_load_choice
    n_write_overview --> n_rank_towns
    n_write_overview --> n_rank_schools
    n_write_overview --> n_weighted
    n_write_overview --> n_ollama_problem
    n_write_overview --> n_overview_messages
    n_write_overview -->|без ИИ| n_template
    n_write_overview --> n_shown_table
    n_write_overview --> OLLAMA
    n_ollama_problem --> OLLAMA

    %% Картата и трите ѝ изгледа
    n_difference_view --> n_map_view
    n_change_view --> n_map_view
    n_trends_view --> n_map_view
    n_map_view --> n_show_map
    n_map_view --> n_show_change
    n_map_view --> n_show_trends
    n_show_map --> n_load_choice
    n_show_map --> n_schools_in_bulgaria
    n_show_map --> n_load_region_map
    n_show_map --> n_subject_score
    n_show_map --> n_region_map
    n_show_map --> n_region_bars
    n_show_map --> n_unit_word
    n_show_map --> n_subject_name
    n_show_map --> n_choice_label
    n_show_change --> n_load_choice
    n_show_change --> n_exam_years
    n_show_change --> n_load_region_map
    n_show_change --> n_region_gaps
    n_show_change --> n_region_map
    n_show_change --> n_region_bars
    n_show_change --> n_unit_word
    n_show_change --> n_region_list
    n_show_change --> n_exam_name
    n_show_change --> n_subject_name
    n_show_change --> n_choice_label
    n_show_trends --> n_load_choice
    n_show_trends --> n_exam_years
    n_show_trends --> n_region_gaps
    n_show_trends --> n_trend_heatmap
    n_show_trends --> n_gap_trend_chart
    n_show_trends --> n_drift_words
    n_show_trends --> n_unit_word
    n_show_trends --> n_region_list
    n_show_trends --> n_exam_name
    n_show_trends --> n_subject_name
    n_region_gaps --> n_load_choice
    n_region_gaps --> n_schools_in_bulgaria
    n_region_gaps --> n_subject_score
    n_region_gaps --> n_school_spread
    n_region_map --> n_colour_key
    n_region_bars --> n_colour_key
    n_region_bars --> n_signed
    n_trend_heatmap --> n_colour_key
    n_trend_heatmap --> n_signed
    n_trend_heatmap --> n_year_labels
    n_trend_heatmap --> n_unit_word
    n_gap_trend_chart --> n_year_labels
    n_gap_trend_chart --> n_unit_word
    n_subject_score --> n_weighted
    n_load_region_map --> MAPFILE
```

### Същото като текст: пет пътя

**Път А: стартирате програмата** (`uv run education_bulgaria/alex_school_results.py`)

```text
main()
 ├─ missing_translations()                    има ли всеки текст и на 4-те езика? Ако не: спира
 ├─ stored_files() → open_database()          списъкът с файлове в school_results.db
 ├─ update_database()                         САМО ако базата е празна: вижте Път Д
 ├─ read_results() → open_database()          първия файл, само за да вземе списъка с области
 ├─ build_app()                               изгражда цялото приложение
 │    └─ build_language_page()                4 пъти: BG на „/“, после EN, RU, RO на /en, /ru, /ro
 │         ├─ language_buttons()              четирите сини бутона до заглавието
 │         ├─ database_status() → open_database()  редът „Данни: 25 файла с резултати...“
 │         ├─ choice_list() → choice_label() → exam_name()   списъкът „Изпит и учебна година“
 │         ├─ town_choices()                  попълва списъка с населени места
 │         │    ├─ load_choice() → read_results()
 │         │    └─ town_label()
 │         └─ subject_name()                  преведените етикети на „Подреди училищата по“ и „Оцвети по“
 ├─ ollama_problem()                          готов ли е ИИ? (само предупреждение, на английски)
 └─ page.launch()                             отваря браузъра, на българската страница
```

Тук не е нужен интернет: всичко идва от базата данни. Всяка функция отгоре, която показва текст,
получава езика на страницата и иска текстовете си от `translate()`.

**Път Б: разделът „Училища“** (страницата се отваря, променяте нещо или щраквате „Покажи резултатите“)

```text
show_schools_tab()                 само при „Покажи резултатите“ и Enter: отива на раздела „Училища“
refresh_towns()                    само при смяна на изпита или областта: нов списък с места
 └─ town_choices() → load_choice() → read_results(), town_label()
show()
 └─ show_results()                 обобщението + таблицата, на езика на страницата
      ├─ load_choice() → read_results()     (около 20 милисекунди, от базата данни)
      ├─ split_town_label()                 (ако е избрано населено място)
      ├─ choice_label(), whole_number()     името на изпита и „Училища: 1 738“ в обобщението
      ├─ weighted_average()                 (средните стойности в обобщението)
      ├─ rank_towns() → weighted_average()  (мястото на населеното място в класацията)
      └─ shown_table()                      имената на колоните на таблицата, преведени
```

**Път В: щраквате „ИИ обзор на първите 5 (gemma4)“**

```text
(страницата преминава към втория раздел)
overview()
 └─ write_overview()
      ├─ load_choice() → read_results()
      ├─ rank_towns() → weighted_average()   първите 5 населени места
      ├─ rank_schools()                      първите 5 училища
      ├─ weighted_average()                  средната стойност за района и „Vs area average“
      ├─ shown_table()                       имената на колоните на двете таблици, преведени
      ├─ ollama_problem()                    готов ли е Ollama?
      ├─ template_overview()                 ако не е, или ако ИИ се провали: пише го програмата
      ├─ overview_messages()                 указанията + фактите в JSON (на английски)
      └─ ollama.chat()                       gemma4 пише, дума по дума, на езика на страницата
```

**Път Г: отваряте раздела „Карта и тенденции на областите“** (или щраквате един от трите му бутона, сменяте
изпита или „Оцвети по“)

Трите бутона извикват `difference_view()`, `change_view()` или `trends_view()`. Всяка от тях
извиква `map_view()` със своя изглед. Отварянето на раздела, нов изпит или „Оцвети по“ извикват
`map_view()` направо, с изгледа, който сте избрали последно (в началото — „Разлика от
България“).

```text
map_view()
 ├─ show_map()                     „Разлика от България“: обобщението на разликите + картата + стълбовете
 │    ├─ load_choice() → read_results()
 │    ├─ schools_in_bulgaria()                  маха училищата в чужбина
 │    ├─ load_region_map()                      чете bulgaria_regions.geojson (само първия път)
 │    ├─ unit_word()                            „точки“ или „успех“, на езика на страницата
 │    ├─ subject_score() → weighted_average()   България, всяка област, градове, села
 │    ├─ choice_label(), subject_name()         изпитът и предметът, в обобщението
 │    ├─ region_map() → colour_key()            оцветената карта
 │    └─ region_bars() → colour_key(), signed() стълбовата диаграма, най-добрите отгоре
 ├─ show_change()                  „Промяна спрямо предходната година“
 │    ├─ load_choice() → read_results()
 │    ├─ unit_word()
 │    ├─ exam_years()                           годините на този изпит, за да намери предходната
 │    ├─ load_region_map()
 │    ├─ region_gaps()                          разстоянието на всяка област от средното за страната
 │    │    ├─ load_choice() → read_results()    (за двете години)
 │    │    ├─ schools_in_bulgaria()
 │    │    ├─ subject_score() → weighted_average()
 │    │    └─ school_spread()                   колко са разпръснати резултатите на училищата
 │    ├─ exam_name(), subject_name(), region_list()   думите на обобщението
 │    ├─ region_map() → colour_key()            картата на промените
 │    └─ region_bars() → colour_key(), signed() стълбовата диаграма, най-подобрилите се отгоре
 └─ show_trends()                  „Тенденции през годините“
      ├─ load_choice() → read_results()
      ├─ unit_word(), exam_name()
      ├─ exam_years()                           всички години на този изпит
      ├─ region_gaps()                          както по-горе, за всяка година
      ├─ drift_words()                          „областите се раздалечиха“, „областите се сближиха“ или „почти без промяна“
      ├─ subject_name(), region_list()          думите на обобщението
      ├─ trend_heatmap() → colour_key(), signed(), year_labels(), unit_word()   решетката от области и години
      └─ gap_trend_chart() → year_labels(), unit_word()   линията на разликата между най-добрата и най-слабата област
```

**Път Д: щраквате зеления бутон „Провери за нови резултати“**

```text
check_for_new_results()
 ├─ update_database()
 │    ├─ find_ministry_on_portal()           чете mon.bg (ако не работи: KNOWN_MINISTRY_ID)
 │    ├─ find_exam_datasets()                намира четирите набора от данни за изпитите
 │    │    ├─ call_portal()                  пита data.egov.bg
 │    │    └─ tidy()
 │    ├─ list_exam_files()                   списъкът с файлове в портала
 │    │    └─ call_portal()
 │    ├─ stored_files()                      списъкът в базата, за сравнение
 │    ├─ download_results()                  само за всеки нов или заменен файл
 │    │    ├─ call_portal()
 │    │    ├─ to_number()
 │    │    └─ tidy_town()
 │    ├─ save_results() → open_database()    записва файла в една транзакция
 │    └─ open_database()                     записва проверката в таблицата „checks“
 ├─ stored_files()                           обновява общия списък с файлове
 ├─ choice_list()                            новият списък „Изпит и учебна година“, на езика на страницата
 └─ database_status()                        новият ред „Данни: ...“
```

### Кои функции общуват с външния свят

| Функция | Общува с |
|---|---|
| `find_ministry_on_portal()` | **mon.bg**, сайта на министерството — само когато базата се попълва или обновява |
| `call_portal()` | **data.egov.bg**, Портала за отворени данни — само когато базата се попълва или обновява. Всеки въпрос към портала минава през тази единствена функция. |
| `open_database()` | Файла **school_results.db** до скрипта, на вашия компютър. Всяко използване на базата минава през тази единствена функция. |
| `ollama_problem()` и `write_overview()` | **Ollama** на вашия компютър: ИИ gemma4 |
| `load_region_map()` | Файла **bulgaria_regions.geojson** до скрипта, на вашия компютър |
| `main()`, чрез `page.launch()` | **вашия браузър** |

Всички останали функции работят само с данни, които вече са в паметта.

---

## 5. Всяка функция, една по една

### Група 1: Малки помощници

#### `tidy(text)`: [ред 207](../alex_school_results.py#L207)
- **С едно изречение:** прави едно име лесно за сравняване с друго име.
- **Получава:** текст. **Връща:** същия текст с малки букви, с единични интервали и без точка
  накрая.
- **Пример:** `"Резултати  от ДЗИ."` → `"резултати от дзи"`
- **Защо:** министерството понякога пише името на набор от данни с двоен интервал или с точка
  накрая. След `tidy()` „едно и също име, написано малко по-различно“ се смята за еднакво.
- **Как:** `text.split()` разрязва текста на думи и премахва всички интервали; `" ".join(...)`
  залепва думите обратно с точно един интервал; `.lower()` прави буквите малки; `.rstrip(".")`
  маха точката накрая.
- **Извиква се от:** `find_exam_datasets()`.

#### `tidy_town(town)`: [ред 214](../alex_school_results.py#L214)
- **С едно изречение:** прави така, че едно и също населено място да изглежда еднакво във всеки
  файл.
- **Примери:** `"ГР. СОФИЯ"` → `"ГР.СОФИЯ"` · `"Прага"` → `"ПРАГА"` ·
  `"СОФИЯ 11 РН КРАСНА ПОЛЯНА"` (софийски район) → `"ГР.СОФИЯ"`
- **Как:**
  1. Единични интервали и ГЛАВНИ букви (`.upper()`).
  2. **Регулярен израз** (`re.sub`, шаблон за търсене в текст) маха интервала след „ГР.“ или
     „С.“.
  3. Ако името започва със „СОФИЯ, число, РН“, това е район на София, затова става „ГР.СОФИЯ“.
- **Извиква се от:** `download_results()`, за всяко училище.

#### `to_number(text)`: [ред 311](../alex_school_results.py#L311)
- **С едно изречение:** превръща клетка от файла в число или в `None`, когато няма резултат.
- **Примери:** `"52.4"` → `52.4` · `"3,09"` → `3.09` (десетична запетая) · `""` → `None` ·
  `"0"` → `None` (нула означава, че никой не е държал този изпит) · `"Област"` → `None`
- **Как:** заменя запетаята с точка и опитва `float()`. Ако Python не може да направи число, той
  вдига `ValueError`; частта `except` го хваща и връща `None`. Последният ред,
  `return value or None`, превръща `0` в `None`.
- **Извиква се от:** `download_results()`, за всяка клетка.

Следващите пет помощника са за **4-те езика**. Кодът винаги работи с английските имена (на
изпитите, предметите и колоните). Тези помощници ги превеждат само за това, което виждате.

#### `exam_name(exam, language)`: [ред 474](../alex_school_results.py#L474)
- **С едно изречение:** името на изпит на езика на страницата.
- **Пример:** `exam_name("NVO 7th grade", "bg")` → `"НВО 7. клас"`
- **Как:** иска от `translate()` ключа `"exam: NVO 7th grade"`. Всеки изпит има по един такъв ключ
  в `translations.py`.
- **Извиква се от:** `choice_label()`, `show_change()` и `show_trends()`.

#### `choice_label(choice, language)`: [ред 481](../alex_school_results.py#L481)
- **С едно изречение:** как изглеждат изпитът и годината на страницата, на езика на страницата.
- **Пример:** `choice_label("NVO 7th grade - 2025/2026", "bg")` → `"НВО 7. клас - 2025/2026"`
- **Как:** `rsplit(" - ", 1)` разрязва избора на изпит и година. Изпитът минава през
  `exam_name()`; годината остава същата.
- **Добре е да знаете:** кодът продължава да използва английския избор. Преведен е само етикетът,
  който виждате.
- **Извиква се от:** `choice_list()`, `show_results()`, `show_map()`, `show_change()` и
  `check_for_new_results()`.

#### `choice_list(exam_files, language)`: [ред 491](../alex_school_results.py#L491)
- **С едно изречение:** елементите на списъка „Изпит и учебна година“.
- **Връща:** списък от **двойки (етикет, стойност)**, напр.
  `[("НВО 7. клас - 2025/2026", "NVO 7th grade - 2025/2026"), ...]`.
- **Защо двойки:** Gradio показва етикета (първата част) и дава на кода стойността (втората част).
  Така всички останали функции пак получават английския избор, на какъвто и език да е страницата.
- **Извиква се от:** `build_language_page()` и `check_for_new_results()`.

#### `subject_name(subject, language)`: [ред 499](../alex_school_results.py#L499)
- **С едно изречение:** „Both subjects“, „Bulgarian (BEL)“ или „Maths / 2nd exam“ на езика на
  страницата.
- **Пример:** `subject_name("Both subjects", "ro")` → `"Ambele materii"`
- **Как:** иска от `translate()` ключа `"subject: Both subjects"`.
- **Извиква се от:** `build_language_page()` (етикетите на „Подреди училищата по“ и „Оцвети по“),
  `show_map()`, `show_change()` и `show_trends()`.

#### `shown_table(table, language)`: [ред 506](../alex_school_results.py#L506)
- **С едно изречение:** копие на таблица с имената на колоните на езика на страницата, готово за
  показване.
- **Пример:** на български колоната `"BEL points"` става `"БЕЛ точки"`, а `"Town"` става
  `"Населено място"`.
- **Как:** `table.rename(columns=...)` преименува всяка колона с малка функция `lambda`: тя иска от
  `translate()` текста `"column: <name>"`. Колоната `#` запазва името си. Стойностите в таблицата
  (имената на училищата и населените места, числата) не се променят.
- **Защо копие:** кодът работи с английските имена на колоните. Само таблицата на страницата
  получава преведените.
- **Извиква се от:** `show_results()` и `write_overview()`.

#### `weighted_average(table, count_column, average_column)`: [ред 528](../alex_school_results.py#L528)
- **С едно изречение:** средната стойност за всички **ученици**, а не за училищата.
- **Защо:** училище със 100 ученици трябва да тежи повече от училище с 5.
- **Пример:** училище А има 100 ученици със среден резултат 60; училище Б има 5 ученици с 90.
  - Средното на двете училища е (60 + 90) / 2 = **75**, което подвежда.
  - Претеглената средна стойност е (100 × 60 + 5 × 90) / 105 = **61,43**, което е честно.
- **Връща две стойности:** средната стойност и броя на учениците. Ако никой не е държал изпита:
  `(None, 0)`.
- **Как:** маха редовете с празни стойности (`dropna`), умножава ученици × среден резултат за
  всяко училище, събира всичко и дели на общия брой ученици.
- **Извиква се от:** `rank_towns()`, `show_results()`, `write_overview()`, `subject_score()`.

#### `town_label(town, region)`: [ред 540](../alex_school_results.py#L540)
- **С едно изречение:** съставя текста, който се показва в списъка с населени места.
- **Пример:** `town_label("ГР.ВАРНА", "ВАРНА")` → `"ГР.ВАРНА (ВАРНА)"`
- **Защо областта:** много села имат едно и също име в различни области.
- **Извиква се от:** `town_choices()`.

#### `split_town_label(label)`: [ред 548](../alex_school_results.py#L548)
- **С едно изречение:** обратното на `town_label()`: отново разделя населеното място и областта.
- **Пример:** `"ГР.ВАРНА (ВАРНА)"` → `("ГР.ВАРНА", "ВАРНА")`
- **Как:** `rsplit(" (", 1)` разрязва текста веднъж, при последното `" ("`; `rstrip(")")` маха
  затварящата скоба.
- **Извиква се от:** `show_results()`.

---

### Група 2: Получаване на данните от интернет

Тези функции се използват **само за попълване или обновяване на базата данни**: първия път и когато
щракнете зеления бутон **Провери за нови резултати**.

#### `call_portal(method, payload)`: [ред 228](../alex_school_results.py#L228)
- **С едно изречение:** изпраща един въпрос до Портала за отворени данни (data.egov.bg) и връща
  отговора.
- **Получава:** името на въпроса (`method`), напр. `"listResources"`, и подробностите му
  (`payload`) като речник. **Връща:** отговора като речник.
- **Пример:** `call_portal("getOrganisationDetails", {"org_uri": "a57a2273-..."})` →
  `{"success": True, "data": {"id": 117, "name": "Министерство на образованието и науката", ...}}`
- **Как:**
  1. `requests.post(...)` изпраща въпроса.
  2. `raise_for_status()` спира с грешка, ако сайтът отговори с код за грешка, напр. 404 или 500.
  3. `.json()` превръща JSON текста в речник на Python.
  4. Порталът казва `"success": false`, когато нещо не е наред. Тогава функцията вдига собствена
     грешка (`RuntimeError`) със съобщението на портала.
- **Добре е да знаете:** това е **единствената врата към портала**. Ако порталът някога се
  промени, има само едно място за поправка.
- **Извиква се от:** `find_exam_datasets()`, `list_exam_files()`, `download_results()`.

#### `find_ministry_on_portal()`: [ред 241](../alex_school_results.py#L241)
- **С едно изречение:** чете страницата „Отворени данни“ на mon.bg и намира идентификатора (ID) на
  министерството в портала.
- **Получава:** нищо. **Връща:** ID-то, текст като `"a57a2273-6b21-4a7a-99ee-05ec4f67ebe4"`.
- **Как:** това е частта за **извличане на данни от уеб страници** (web scraping), с
  BeautifulSoup:
  1. `requests.get` изтегля страницата.
  2. `BeautifulSoup` чете нейния HTML.
  3. Цикъл минава през всяка връзка (`<a href="...">`).
  4. Когато връзката съдържа `data.egov.bg/organisation/profile/`, изрязва ID-то между
     `/profile/` и `?` и го връща.
  5. Ако не намери такава връзка, вдига грешка.
- **Извиква се от:** `update_database()`. Ако mon.bg не работи, `update_database()` използва
  `KNOWN_MINISTRY_ID`.

#### `find_exam_datasets(ministry_id)`: [ред 257](../alex_school_results.py#L257)
- **С едно изречение:** намира четирите набора от данни за изпитите (НВО в 4., 7. и 10. клас и
  ДЗИ) сред около 350-те набора на министерството.
- **Връща:** речник *изпит → ID на набора*, напр. `{"NVO 7th grade": "b56288b6-...", ...}`
- **Как:**
  1. Пита портала за номера на министерството (117).
  2. Иска наборите от данни на министерството **страница по страница**, по 100 наведнъж.
     Цикълът `while True:` се повтаря, докато страница не съдържа по-малко от 100 (`break`).
  3. За всеки изпит в `EXAMS` запазва наборите, чието име след `tidy()` е равно на очакваното.
  4. Ако няколко имат това име, взема най-новия (`max` по `updated_at`).
- **Знакът `_`:** в `for exam, (_, dataset_name) in EXAMS.items():` всяка стойност в `EXAMS` е
  двойка (вид, име). Тук ни трябва само името, затова видът получава името „не ни трябва“ — `_`.
- **Извиква се от:** `update_database()`.

#### `list_exam_files(exam_datasets)`: [ред 287](../alex_school_results.py#L287)
- **С едно изречение:** изброява годишните файлове на всеки изпит в портала и дава на всеки четимо
  име като `"NVO 7th grade - 2025/2026"`.
- **Връща:** речник *„изпит - година“ → (вид, ID на файла)*, напр.
  `{"NVO 7th grade - 2025/2026": ("nvo", "08157f0e-..."), ...}`.
- **Как:**
  1. Пита портала за файловете на всеки набор.
  2. **Регулярен израз** (`re.search`) намира учебната година в името на файла
     („учебна 2025/2026“). Файловете без нея са в стар формат, затова `continue` ги прескача.
  3. За ДЗИ запазва само основната сесия (май–юни) на задължителните изпити.
  4. Подрежда файловете с най-новата година първа.
- **Извиква се от:** `update_database()`, която сравнява този списък със списъка в базата.

#### `download_results(kind, resource_id)`: [ред 323](../alex_school_results.py#L323)
- **С едно изречение:** изтегля един файл с резултати от портала и го превръща в чиста таблица, по
  един ред за училище.
- **Получава:** вида (`"nvo"` или `"dzi"`) и ID-то на файла. **Връща:** таблица с колоните Region,
  Municipality, Town, School, School code и 4 колони с резултати.
- **Най-важната функция за почистване:** тя поправя всички проблеми в държавните файлове:
  - заглавен ред над имената на колоните;
  - колони в различен ред в някои години;
  - кодове на училища, написани с интервали;
  - десетични запетаи;
  - „В ЧУЖБИНА“ вместо „ЧУЖБИНА“;
  - няколко колони по предмети за втория изпит на матурите.
- **Как:**
  1. Изтегля редовете — списъци от текстове — чрез `call_portal("getResourceData", ...)`.
  2. Намира заглавния ред: реда, който започва с „Област“.
  3. Намира по имената им кои колони са „Училище“ и „Код“.
  4. За всяко училище извиква `to_number()` за всяка клетка.
     - **НВО:** взема последните 4 числа.
     - **ДЗИ:** българският език е в колони 5 и 6 (Python брои от 0, така че това са 6-ата и
       7-ата колона). Вторият изпит е претеглената средна стойност от всички останали колони по
       предмети.
     - Подрежда областта, кода, името и населеното място (`tidy_town()`).
  5. Изгражда таблицата (`pd.DataFrame`). Броят на учениците става цели числа (`Int64`), а
     средните стойности се закръгляват до 2 знака след десетичната запетая.
- **Добре е да знаете:** чистата таблица отива направо в базата данни (`save_results()`), така че
  почистването става **веднъж за файл**, а не всеки път, когато разглеждате резултатите.
- **Извиква се от:** `update_database()`.

---

### Група 3: Базата данни

#### `open_database()`: [ред 369](../alex_school_results.py#L369)
- **С едно изречение:** отваря файла с базата данни `school_results.db` и го създава заедно с
  таблиците му, ако още ги няма.
- **Връща:** отворена **връзка** (connection) с базата — линията, по която Python разговаря с нея.
- **Как:**
  1. `sqlite3.connect(DATABASE_FILE)` отваря файла или го създава, ако липсва.
  2. `executescript(DATABASE_TABLES)` изпълнява SQL кода в `DATABASE_TABLES`.
     `CREATE TABLE IF NOT EXISTS` създава всяка таблица само ако още я няма.
- **Добре е да знаете:** който отвори базата, трябва да я затвори отново с `.close()`. Затова
  другите функции използват `try:` … `finally: database.close()`: `finally` се изпълнява дори ако
  нещо се провали по средата.
- **Извиква се от:** `save_results()`, `stored_files()`, `read_results()`, `update_database()`,
  `database_status()`.

#### `save_results(choice, kind, resource_id, table)`: [ред 379](../alex_school_results.py#L379)
- **С едно изречение:** записва един изтеглен файл с резултати в базата, като заменя по-старото му
  копие.
- **Получава:** името на файла (`choice`, като `"NVO 7th grade - 2025/2026"`), вида му, ID-то му в
  портала и чистата таблица от `download_results()`.
- **Как:**
  1. Преименува колоните на таблицата с имената в базата (`DATABASE_COLUMNS`) и добавя колона
     `choice`, така че всеки ред да знае към кой файл принадлежи.
  2. Вътре в `with database:`, което е **транзакция**:
     - изтрива старите редове на файла (`DELETE FROM results WHERE choice = ?`);
     - добавя новите (`to_sql`);
     - записва реда на файла в таблицата `files` с днешната дата (`INSERT OR REPLACE`).
  3. Благодарение на транзакцията или се записва всичко, или нищо: обновяване, което се провали
     по средата, никога не оставя половин файл.
- **Знакът `?` в SQL:** заместител, който sqlite3 попълва със стойността по безопасен начин. Никога
  не слагайте стойности направо в текста на SQL.
- **Извиква се от:** `update_database()`.

#### `stored_files()`: [ред 397](../alex_school_results.py#L397)
- **С едно изречение:** изброява всички файлове с резултати в базата.
- **Връща:** същия вид речник като `list_exam_files()`: *„изпит - година“ → (вид, ID на файла)*.
  Този речник попълва списъка „Изпит и учебна година“ на страницата.
- **Как:** `SELECT … FROM files` чете таблицата `files`. После две сортирания подреждат файловете
  изпит по изпит (в реда на `EXAMS`), с най-новата година първа. Сортирането в Python е
  **стабилно**: когато сортира по изпит, файловете от един и същ изпит запазват реда по години от
  първото сортиране.
- **Извиква се от:** `main()`, `update_database()`, `check_for_new_results()`.

#### `read_results(choice, kind)`: [ред 414](../alex_school_results.py#L414)
- **С едно изречение:** чете един изпит и година от базата като таблица с имената на колоните от
  страницата.
- **Пример:** `read_results("NVO 7th grade - 2025/2026", "nvo")` дава 1702-те училища за около
  20 милисекунди.
- **Как:**
  1. `pd.read_sql("SELECT … FROM results WHERE choice = ? ORDER BY rowid", …)` пита базата.
     `ORDER BY rowid` запазва реда, в който редовете са били записани.
  2. Преименува колоните с имената от страницата (`RESULT_COLUMNS`) и превръща броя на учениците в
     цели числа (`Int64`).
- **Извиква се от:** `load_choice()`, `main()`.

#### `update_database()`: [ред 431](../alex_school_results.py#L431)
- **С едно изречение:** пита портала за списъка му с файлове и изтегля само тези, които базата още
  няма или които министерството е заменило.
- **Връща:** списъка с добавените или заменените файлове. Празен е, ако няма нищо ново.
- **Как:**
  1. `find_ministry_on_portal()` (или `KNOWN_MINISTRY_ID`, ако mon.bg не работи), после
     `find_exam_datasets()` и `list_exam_files()`: списъкът в портала (около 15–20 секунди).
  2. Сравнява го със `stored_files()`. Файлът се смята за нов, ако изпитът и годината му липсват
     или ако ID-то му е различно — това означава, че министерството го е заменило с коригирана
     версия.
  3. За всеки нов файл: `download_results()`, после `save_results()`.
  4. Записва проверката в таблицата `checks` с датата и броя на новите файлове.
- **Извиква се от:** `main()` (само когато базата е празна) и `check_for_new_results()` (зеления
  бутон).

#### `database_status(language)`: [ред 460](../alex_school_results.py#L460)
- **С едно изречение:** пише реда в горната част на страницата, като *„Данни: 25 файла с
  резултати в локалната база данни (school_results.db) · последна проверка в data.egov.bg:
  2026-11-25 13:22“*.
- **Получава:** езика на страницата. На английската страница редът започва с *„Data: 25 results
  files…“*.
- **Как:** задава на базата два въпроса на SQL: `SELECT COUNT(*) FROM files` (колко файла) и
  `SELECT MAX(checked_at) FROM checks` (последната проверка). После `translate("data_status", …)`
  ги вмъква в текста на езика на страницата. Ако порталът никога не е проверяван, пише „никога“
  (текстът `"never"`, също преведен).
- **Извиква се от:** `build_language_page()` и `check_for_new_results()`.

#### `load_choice(exam_files, choice, language)`: [ред 514](../alex_school_results.py#L514)
- **С едно изречение:** превръща това, което сте избрали в списъка „Изпит и учебна година“, в
  таблица с резултати от базата данни или показва съобщение за грешка на страницата.
- **Получава:** речника с файловете, вашия избор, напр. `"DZI (matura) - 2025/2026"` (винаги
  английската стойност, вижте `choice_list()`), и езика на страницата — за съобщенията за грешки.
  **Връща две стойности:** вида (`"dzi"`) и таблицата.
- **Как:**
  1. Ако изборът ви не е в речника, вдига `gr.Error(...)`, което Gradio показва като червено
     изскачащо съобщение на страницата, на езика на страницата.
  2. Намира вида.
  3. Извиква `read_results()` вътре в `try:`. Ако базата не може да се прочете, получавате
     разбираемо `gr.Error` вместо срив.
- **Извиква се от:** `town_choices()`, `show_results()`, `write_overview()`, `show_map()`,
  `region_gaps()`, `show_change()` и `show_trends()`.

---

### Група 4: Избор и класиране

#### `town_choices(exam_files, choice, region, language)`: [ред 556](../alex_school_results.py#L556)
- **С едно изречение:** съставя списъка с населени места за падащото меню „Населено място“.
- **Връща:** списък, който започва с „Всички населени места“, после населените места по азбучен
  ред, напр. `"ГР.ВАРНА (ВАРНА)"`.
  - Първият елемент е **двойка (етикет, стойност)**: етикетът е преведен, стойността остава на
    английски. На български това е `("Всички населени места", "All towns")`.
  - Самите населени места остават на кирилица на всеки език, както са в данните.
- **Защо градовете са първи:** в азбуката Г е преди С, затова „ГР.“ (градове) са преди „С.“
  (села).
- **Как:** зарежда таблицата (`load_choice()`), запазва само училищата от избраната област, маха
  повторенията (`drop_duplicates()`), прави етикетите (`town_label()`) и ги подрежда.
- **Извиква се от:** `build_language_page()` (първия списък) и `refresh_towns()` (при смяна на
  изпита или областта).

#### `rank_towns(table, kind, min_students)`: [ред 570](../alex_school_results.py#L570)
- **С едно изречение:** прави класация на населените места, най-добрите първи.
- **Връща:** таблица с по един ред за населено място: `#`, Town, Region, Schools, Students, двете
  средни стойности и „Both subjects“.
- **Как:**
  1. `groupby(["Region", "Town"])` събира заедно училищата от едно и също място.
  2. За всяко място извиква `weighted_average()` за български език и за математика (или втория
     изпит).
  3. Прескача местата с твърде малко ученици (по-малко от `min_students`), за да не може малко
     село да спечели.
  4. „Both subjects“ = (български + математика) / 2.
  5. Подрежда по „Both subjects“, от най-високото, и добавя колоната за място `#`: 1, 2, 3…
- **`min_students`:** 100 за цяла България, 30 в рамките на една област.
- **Извиква се от:** `show_results()` (мястото на вашето населено място) и `write_overview()`
  (първите 5).

#### `rank_schools(table, kind)`: [ред 594](../alex_school_results.py#L594)
- **С едно изречение:** същото като `rank_towns()`, но за училища.
- **Как:**
  1. Запазва само училищата с поне 10 ученици на всеки изпит (`MIN_SCHOOL_STUDENTS`).
     - `big_enough` е списък от `True`/`False`, по едно за всяко училище (**маска**);
       `table[big_enough]` запазва само редовете с `True`.
     - `fillna(0)` означава, че празен брой ученици се брои като 0, тоест твърде малко.
  2. Изчислява „Both subjects“, подрежда училищата и ги номерира.
- **Извиква се от:** `write_overview()`.

#### `show_results(exam_files, choice, region, town, search, rank_by, language)`: [ред 611](../alex_school_results.py#L611)
- **С едно изречение:** прави всичко в раздела „Училища“: обобщението и таблицата.
- **Получава:** петте ви избора от страницата: изпит, област, населено място, текст за търсене и
  „подреди по“, и езика на страницата. **Връща две стойности:** обобщението (текст в Markdown) и
  таблицата.
- **Как:**
  1. **Зареждане:** взема таблицата с `load_choice()`.
  2. **Филтриране:** запазва училищата от вашето населено място или от вашата област.
     - Ако сте избрали населено място, запазва и неговата област и цялата страна, за сравнение.
     - Разделя етикета на мястото със `split_town_label()`.
  3. **Търсене:** запазва редовете, в които училището, населеното място или общината съдържат
     вашия текст. `case=False` означава, че главните и малките букви нямат значение.
  4. **Подреждане:** по български или по математика, най-добрите първи, и добавя колоната `#`.
  5. **Обобщение:** броят на училищата и средните стойности (`weighted_average()`), сравнени с
     областта и България. Ако сте избрали населено място, добавя мястото му в класацията за
     България и за неговата област (`rank_towns()`).
  6. **Език:** всеки ред от обобщението идва от `translate()`. Името на изпита идва от
     `choice_label()`. Големите цели числа идват от `whole_number()`: „Schools: 1,738“ на английски,
     „Училища: 1 738“ на български. Средните стойности запазват десетичната точка на всеки език,
     като „52.40“. Таблицата получава преведени имена на колоните от `shown_table()`.
- **Пример за първия ред:** `**НВО 7. клас - 2025/2026** · Всички области · **Училища: 1 702**`
- **Извиква се от:** `show()` на страницата.

---

### Група 5: Обзорът от ИИ

#### `ollama_problem(language)`: [ред 686](../alex_school_results.py#L686)
- **С едно изречение:** проверява дали ИИ е готов: Ollama работи и gemma4 е изтеглен.
- **Връща:** `None`, ако всичко е наред („няма проблем“), иначе съобщение какво не е наред, на
  дадения език. `main()` иска английски (`"en"`), защото предупреждението му отива в терминала.
- **Как:**
  1. Пита Ollama на вашия компютър (`http://localhost:11434/api/tags`) за списъка му с модели.
     - **Няма отговор:** „Ollama не работи…“.
     - **gemma4 не е в списъка:** „gemma4 не е изтеглен…“.
  2. За Ollama `gemma4` и `gemma4:latest` са един и същ модел, затова кодът добавя `:latest`,
     преди да сравни.
- **Защо това име:** функцията отговаря на въпроса *„какъв е проблемът?“*, а `None` означава, че
  няма проблем. Затова кодът гласи `if problem:`.
- **Извиква се от:** `main()` (предупреждение при старта) и `write_overview()` (преди да пита ИИ).

#### `overview_messages(choice, kind, area, area_averages, towns, schools, min_town_students, language)`: [ред 702](../alex_school_results.py#L702)
- **С едно изречение:** пише „писмото“ до ИИ: нашите правила плюс фактите.
- **Връща:** списък от две съобщения:
  - `{"role": "system", ...}`: правилата, от `overview_system_prompt` в началото на файла.
  - `{"role": "user", ...}`: изпитът, районът, средните стойности и първите 5 населени места и
    училища като JSON.
- **Езикът:** `overview_system_prompt.format(...)` попълва трите заместителя в указанията:
  - `{language}` получава английското име на езика от `LANGUAGE_NAMES`, напр. „Bulgarian“.
    Правилото става „Write the whole answer in Bulgarian“ (напиши целия отговор на български).
  - `{towns_heading}` и `{schools_heading}` получават двете заглавия, преведени, напр.
    „Най-добри населени места“. Така текстът на ИИ има същите заглавия като собствения обзор на
    програмата.
- **Фактите остават на английски,** защото моделът чете най-добре английски. Само отговорът му е
  на езика на страницата.
- **JSON:** `json.dumps(...)` превръща таблиците в текст, който ИИ може да чете.
  `ensure_ascii=False` запазва кирилицата четима.
- **Извиква се от:** `write_overview()`.

#### `template_overview(area, towns, schools, language)`: [ред 732](../alex_school_results.py#L732)
- **С едно изречение:** пише обзора **без ИИ**, от същите числа, които получава ИИ.
- **Кога:** ако Ollama не работи, ако моделът не е изтеглен или ако ИИ се провали по средата.
- **Връща:** текст в Markdown на езика на страницата, със същото оформление като на ИИ:
  „## Най-добри населени места“, номериран списък, „## Най-добри училища“, номериран списък и
  заключителен ред, ако повечето от най-добрите училища са в едно и също населено място.
- **Пример за ред:** `1. **ГР.ВАРНА**: 60.04, 6.75 above the area's average`. На български:
  `1. **ГР.ВАРНА**: 60.04, с 6.75 над средното`.
- **Как:**
  1. `to_dict(orient="records")` превръща всяка таблица в списък от речници, по един за ред.
     `translate("town_item", …)` и `translate("school_item", …)` пишат по един ред за всеки.
  2. `value_counts()` брои населените места на най-добрите училища. Ако в едно място са всички
     или повече от половината, заключителният ред го казва.
- **Добре е да знаете:** текстът е по-прост от този на ИИ, но е **мигновен и винаги точен**.
- **Извиква се от:** `write_overview()`.

#### `write_overview(exam_files, choice, region, language)`: [ред 763](../alex_school_results.py#L763)
- **С едно изречение:** изчислява първите 5 населени места и училища, показва ги и после оставя
  gemma4 да напише обзора дума по дума.
- **Особеност:** това е **генератор**. Използва `yield` вместо `return` и всяко `yield` изпраща
  обновление към страницата: двете таблици и текста дотук. Така текстът се появява дума по дума.
- **Как:**
  1. Зарежда таблицата и запазва избраната област.
  2. Извиква `rank_towns()` и `rank_schools()` и запазва първите 5 (`head(TOP)`).
  3. Изчислява средната стойност за района и колко се отдалечава от нея всяко място и училище
     („Vs area average“).
     - **Това го изчислява кодът, не ИИ**, защото моделите на ИИ се справят зле с аритметиката.
       В нашите тестове gemma4 написа 13,04 вместо 14,04.
     - Текстът вече е на езика на страницата, като „6.75 above“ или „с 6.75 над“.
  4. `shown_table()` прави копия на двете таблици с преведени имена на колоните, за страницата.
  5. Проверява Ollama (`ollama_problem()`). Ако има проблем, програмата сама пише обзора
     (`template_overview()`) и казва защо.
  6. `ollama.chat(..., stream=True)` пита gemma4 със съобщенията от `overview_messages()`. За
     всяко малко парче текст (**chunk**) добавя парчето и подава (`yield`) по-дългия текст.
  7. Ако нещо се провали, докато ИИ пише, `try`/`except` заменя текста с обзора на програмата и
     казва какво се е объркало.
- **Настройки в извикването:**
  - `temperature 0.3`: да се придържа към фактите.
  - `num_predict 900`: максимална дължина.
  - `think=False`: без скрито „мислене“, което е по-бързо.
- **Извиква се от:** `overview()` на страницата.

---

### Група 6: Картата и трите ѝ изгледа

#### `schools_in_bulgaria(table)`: [ред 829](../alex_school_results.py#L829)
- **С едно изречение:** маха училищата в чужбина, които нямат област на картата.
- **Как:** в България всяко населено място започва с „ГР.“ (град) или „С.“ (село).
  `str.startswith(("ГР.", "С."))` дава `True` за тях, а областта не трябва да е „ЧУЖБИНА“.
  Таблицата запазва само тези редове.
- **Защо:** някои файлове изброяват училищата в чужбина под ЧУЖБИНА, други — под българска област.
  Училището в БРАТИСЛАВА например е под СОФИЯ-ГРАД и иначе би влязло в средното за София.
- **Извиква се от:** `show_map()` и `region_gaps()`.

#### `subject_score(schools, kind, subject)`: [ред 838](../alex_school_results.py#L838)
- **С едно изречение:** средната стойност на група училища по избрания предмет, претеглена по броя
  на учениците.
- **Получава:** група училища (една област, всички градове, всички села или цялата страна), вида на
  изпита и предмета: „Both subjects“, „Bulgarian (BEL)“ или „Maths / 2nd exam“. **Връща:** едно
  число или `None`, ако няма резултати.
- **Как:** извиква `weighted_average()` за български език и за математика (или втория изпит) и
  връща този, който сте поискали. „Both subjects“ е средното на двата.
- **Пример:** НВО 7. клас 2025/2026, двата предмета: за цялата страна дава 46,87, а за СОФИЯ-ГРАД —
  60,22.
- **Извиква се от:** `show_map()` и `region_gaps()`.

#### `school_spread(schools, kind, subject)`: [ред 855](../alex_school_results.py#L855)
- **С едно изречение:** колко са разпръснати резултатите на училищата по избрания предмет.
- **Връща:** едно число — **стандартното отклонение**: грубо казано, колко далеч от средното е едно
  обикновено училище. Малко число означава, че повечето училища имат горе-долу еднакви резултати;
  голямо — че са далеч едно от друго.
- **Как:** взема колоната на избрания предмет (за „Both subjects“ — средното на двете колони,
  училище по училище), а `.std()` на pandas прави останалото.
- **Защо:** сравнението със средното за страната премахва ефекта от това колко *лесен* е бил
  тестът, но не и колко той *раздалечава учениците*. Тест, който раздалечава учениците повече,
  увеличава и разликата между областите, дори ако реално нищо не се е променило. Делението на
  разликата на това число премахва този ефект.
- **Пример:** НВО 7. клас, двата предмета: 15,01 точки през 2018/2019, 17,55 през 2025/2026.
- **Извиква се от:** `region_gaps()`.

#### `load_region_map()`: [ред 873](../alex_school_results.py#L873)
- **С едно изречение:** чете границите на 28-те области от файла `bulgaria_regions.geojson`.
- **Връща:** съдържанието на файла като речник. За всяка област има името, както е в данните (напр.
  „ВАРНА“), кода (BG-03), английското име и границата като списък от точки.
- **`@cache`:** чете файла само веднъж — първия път, когато се покаже картата — и го запомня.
- **Файлът:** направен от световната карта на Natural Earth, която е обществено достояние (public
  domain), като е запазена само България (66 KB).
- **Извиква се от:** `show_map()` и `show_change()`.

#### `colour_key(values, zero_label)`: [ред 881](../alex_school_results.py#L881)
- **С едно изречение:** изчислява цветовата скала за набор от числа над и под 0: двата ѝ края и
  надписите на легендата ѝ.
- **Получава:** числата (колона от таблица) и текста за средата на легендата, като „0 = средното“
  или „0 = без промяна“. **Връща три стойности:** `limit` — най-голямото разстояние от 0; петте
  места на надписите в легендата; и самите надписи.
- **Как:**
  1. `values.abs().max()` е най-голямото число без значение от знака му. Скалата стига от `-limit`
     до `+limit`, еднакво далеч в двете посоки, така че 0 винаги е средният цвят — жълто.
  2. Ако няма числа или всички са 0, използва много малък `limit` (0,01), за да може диаграмата пак
     да работи.
  3. По-малко знаци след запетаята за големите числа: „+13“ за точки, „+0.41“ за оценки.
- **Пример:** за разликите в 7. клас (−13,45 … +13,34) дава надписите „−13“, „−7“, „0 = средното“,
  „+7“, „+13“.
- **Извиква се от:** `region_map()`, `region_bars()` и `trend_heatmap()`.

#### `signed(value, decimals=2)`: [ред 897](../alex_school_results.py#L897)
- **С едно изречение:** пише число със знака му, като „+2.14“ или „−4.99“ — за числата, които се
  показват на диаграмите.
- **`decimals=2`:** параметър със **стойност по подразбиране**. Ако не я подадете, тя е 2.
- **Как:** `f"{value:+.2f}"` пише числото със знак и 2 знака след десетичната точка. Число, което
  се закръглява до нула, би излязло като „-0.00“, затова при тях функцията маха знака: `text[1:]` е
  текстът без първия му символ.
- **Пример:** `signed(2.141)` дава „+2.14“, `signed(-0.004)` дава „0.00“, а `signed(-0.04, 1)` дава
  „0.0“.
- **Извиква се от:** `region_bars()` и `trend_heatmap()`.

#### `year_labels(years)`: [ред 906](../alex_school_results.py#L906)
- **С едно изречение:** пише учебните години на два реда, като „2018/“ над „2019“, за да се побират
  под тесните колони на диаграмите с тенденции, без да са наклонени.
- **Как:** `year.replace("/", "/<br>")`. В надписите на Plotly `<br>` означава „нов ред“.
- **Извиква се от:** `trend_heatmap()` и `gap_trend_chart()`.

#### `region_map(regions, borders, column, key_title, zero_label)`: [ред 914](../alex_school_results.py#L914)
- **С едно изречение:** рисува картата, като оцветява всяка област според числата в една колона на
  таблицата: разликата ѝ от средното за страната или колко се е променила тази разлика.
- **Получава:** таблицата с областите, границите, колоната, по която се оцветява (`"Vs Bulgaria"`
  или `"Change"`), заглавието на цветовата легенда и текста за средата ѝ („0 = средното“ или
  „0 = без промяна“). Таблицата има и колона `"Hover"`: текстът, който се показва, когато мишката е
  над област. **Връща:** фигура на Plotly, която Gradio показва на страницата.
- **Как:**
  1. `colour_key()` дава двата края на скалата и надписите на легендата.
  2. `go.Choropleth(...)` е картата на Plotly с „оцветени площи“.
     `featureidkey="properties.region"` ѝ казва да свърже всяка граница с данните по българското име
     на областта.
  3. `zmin=-limit, zmax=limit`: цветовете стигат еднакво далеч в двете посоки, така че 0 винаги е
     средният цвят — жълто.
  4. `fitbounds="locations", visible=False` приближава България и скрива останалия свят.
- **Защо една функция за две карти:** изгледите „Разлика от България“ и „Промяна спрямо предходната година“ рисуват един и същ вид
  карта от различна колона, затова използват тази функция, вместо да имат две нейни копия.
- **Извиква се от:** `show_map()` и `show_change()`.

#### `region_bars(regions, column, axis_title)`: [ред 942](../alex_school_results.py#L942)
- **С едно изречение:** същите 28 области като стълбова диаграма, най-високото отгоре, с точното
  число на всяка област, написано до стълба ѝ.
- **Защо:** картата е добра за *къде*, а стълбовете — за *колко*. Написаните числа (като `+13.34`
  или `−13.45`, направени от `signed()`) позволяват диаграмата да се чете и без цветовете.
- **Как:**
  1. `go.Bar(..., orientation="h")` прави хоризонтални стълбове, със същите `MAP_COLOURS` и
     същата скала (`colour_key()`) като картата.
  2. Оста стига еднакво далеч в двете посоки, с 0 в средата. Тя е 1,6 пъти по-дълга от
     най-голямото число, за да се побират числата до стълбовете.
  3. Таблицата трябва вече да е подредена от най-ниското нагоре, защото Plotly рисува първия ред
     най-отдолу.
- **Извиква се от:** `show_map()` и `show_change()`.

#### `unit_word(kind, language)`: [ред 977](../alex_school_results.py#L977)
- **С едно изречение:** мерната единица на резултатите от изпита, на езика на страницата: „точки“
  за НВО, „успех“ за ДЗИ.
- **Пример:** `unit_word("nvo", "bg")` → `"точки"`
- **Как:** иска от `translate()` текста `"unit_points"` или `"unit_grade"` според вида.
- **Извиква се от:** `show_map()`, `show_change()`, `show_trends()`, `trend_heatmap()` и
  `gap_trend_chart()`.

#### `show_map(exam_files, choice, subject, language)`: [ред 984](../alex_school_results.py#L984)
- **С едно изречение:** прави всичко в раздела „Карта и тенденции на областите“: обобщението на разликите,
  картата и стълбовата диаграма.
- **Получава:** избрания изпит и година, предмета от „Оцвети по“ и езика на страницата. **Връща
  три стойности:** текста на обобщението, картата и стълбовата диаграма.
- **Как:**
  1. Зарежда таблицата (`load_choice()`) и маха училищата в чужбина (`schools_in_bulgaria()`).
  2. Чете границите (`load_region_map()`). Ако файлът липсва, връща ясно съобщение, вместо да се
     срине.
  3. Изчислява средното за страната и средното на всяка област със `subject_score()` — по една
     област наведнъж благодарение на `groupby("Region")` — и разликата на всяка област
     („Vs Bulgaria“).
  4. Подрежда областите и пише текста `"Hover"` за всяка. Името на областта остава на кирилица.
     Страниците с латински букви (английската и румънската) добавят и английското ѝ име от файла
     с границите, като „ВАРНА (Varna)“. Намира най-добрата и най-слабата област и сравнява
     градовете („ГР.“) със селата („С.“).
  5. Рисува картата (`region_map()`) и стълбовете (`region_bars()`), оцветени по колоната
     „Vs Bulgaria“.
  6. Всички думи са на езика на страницата: мерната единица от `unit_word()`, изпитът от
     `choice_label()`, предметът от `subject_name()`, а останалото от `translate()`.
- **Пример за обобщението:** „Най-добра област: СОФИЯ-ГРАД 60.22 (+13.34) · най-слаба област:
  СЛИВЕН 33.43 (−13.45) · разлика: 26.79 точки“, после „Градове (ГР.): 49.68 · села (С.): 30.95 ·
  разлика: 18.73 точки“.
- **Извиква се от:** `map_view()` на страницата, за изгледа „Разлика от България“.

#### `exam_years(exam_files, choice)`: [ред 1041](../alex_school_results.py#L1041)
- **С едно изречение:** намира всички години на избрания изпит, от най-старата.
- **Как:** изборът изглежда като „NVO 7th grade - 2025/2026“. `rsplit(" - ", 1)` го разрязва при
  **последното** „ - “ на изпит („NVO 7th grade“) и година. Функцията запазва файловете от същия
  изпит и ги подрежда. Подреждането на текста работи, защото всяка година започва с 4-те си цифри.
- **Пример:** за „NVO 7th grade - 2025/2026“ дава 8-те избора от „NVO 7th grade - 2018/2019“ до
  „NVO 7th grade - 2025/2026“.
- **Извиква се от:** `show_change()` и `show_trends()`.

#### `region_gaps(exam_files, choices, subject, language)`: [ред 1050](../alex_school_results.py#L1050)
- **С едно изречение:** за всяка от дадените години на изпита — колко далеч е всяка област от
  средното за страната през тази година.
- **Получава:** файловете, списък от избори (2 години за промяната, всички години за тенденциите),
  предмета и езика на страницата (само за съобщенията за грешки на `load_choice()`).
  **Връща три стойности:** таблица с по един ред за област и по една колона за учебна
  година, средните стойности за страната и колко разпръснати са били резултатите на училищата
  всяка година (`school_spread()`). На `show_change()` третата стойност не ѝ трябва, затова пише
  `_` за нея.
- **Как:**
  1. За всяка година зарежда таблицата, маха училищата в чужбина и изчислява средното за страната и
     средното на всяка област със `subject_score()`, а разпръснатостта — със `school_spread()`.
  2. `pd.DataFrame(scores)` прави таблицата: областите стават редове, а годините — колони.
  3. `.sub(national, axis=1)` изважда средното за страната за всяка година от цялата колона на
     тази година.
- **Защо средното за страната:** тестът е различен всяка година. Средното за страната в 7. клас
  падна от 49,33 на 46,87 за една година — главно защото тестът беше по-труден, а не защото всяко
  училище се е влошило. Разстоянието на областта от средното за страната премахва този ефект, така
  че годините могат да се сравняват.
- **Извиква се от:** `show_change()` и `show_trends()`.

#### `region_list(regions_and_changes, language)`: [ред 1071](../alex_school_results.py#L1071)
- **С едно изречение:** пише няколко области с техните промени, за един ред от обобщение.
- **Получава:** двойки (област, промяна) и езика на страницата.
- **Пример:** `"**ДОБРИЧ** +2.14, **ПЕРНИК** +1.76"`. Ако няма области, дава „няма“ на езика на
  страницата („none“ на английски).
- **Как:** f-низ пише всяка двойка, а `", ".join(...)` слага запетаи между тях. Празен списък дава
  празен текст и тогава `or` избира преведеното „няма“.
- **Извиква се от:** `show_change()` и `show_trends()`.

#### `show_change(exam_files, choice, subject, language)`: [ред 1079](../alex_school_results.py#L1079)
- **С едно изречение:** прави изгледа „Промяна спрямо предходната година“: колко се е преместила всяка
  област спрямо средното за страната от предходната година насам.
- **Връща три стойности,** като `show_map()`: обобщението, картата и стълбовата диаграма.
- **Как:**
  1. Намира мястото на избраната година в `exam_years()`. Ако това е първата година, няма с какво
     да се сравни, затова връща съобщение и `None` за двете диаграми.
  2. `region_gaps()` дава разстоянието на всяка област от средното за страната и в двете години.
  3. `.dropna()` запазва само областите с резултати и в двете години. Промяната е „сега“ минус
     „преди“.
  4. Пише обобщението и рисува картата и стълбовете с `region_map()` и `region_bars()`, оцветени
     по колоната „Change“.
  5. Обобщението е на езика на страницата: изпитът от `exam_name()`, предметът от
     `subject_name()`, мерната единица от `unit_word()`, а списъците с области от `region_list()`.
- **Обобщението:** трите области, които са се подобрили най-много, и трите, които са изостанали
  най-много, **типичното преместване** (медианата на промените, без значение от знака им) и как се
  е променило самото средно за България.
- **Пример:** НВО 7. клас 2024/2025 → 2025/2026, двата предмета: най-много се подобрява ДОБРИЧ
  +2,14, най-много изостава ЯМБОЛ −4,99, типично преместване 0,98 точки.
- **Извиква се от:** `map_view()` на страницата.

#### `show_trends(exam_files, choice, subject, language)`: [ред 1126](../alex_school_results.py#L1126)
- **С едно изречение:** прави изгледа „Тенденции през годините“: разстоянието на всяка област от
  средното за страната във всяка година на избрания изпит.
- **Връща три стойности:** обобщението, решетката от области и години (`trend_heatmap()`) и
  линейната диаграма на разликата между най-добрата и най-слабата област (`gap_trend_chart()`).
- **Как:**
  1. `exam_years()` дава всички години, а `region_gaps()` — таблицата с разстоянията.
  2. Подрежда областите по последната година. Plotly рисува първия ред най-отдолу, така че
     най-добрата област излиза най-отгоре.
  3. `gaps.max() - gaps.min()` дава за всяка година (всяка колона) разстоянието на най-добрата
     област минус това на най-слабата: **разликата между областите**.
  4. `spread / school_spreads` дели разликата за всяка година на това колко разпръснати са били
     резултатите на училищата през тази година (`school_spread()`). Това е по-честната мярка, а
     `drift_words()` описва промяната ѝ с думи.
  5. Сравнява последната година на всяка област с първата, за да намери кои са наваксали и кои са
     изостанали. Обобщението предупреждава, че тук се използват само тези две години.
  6. Като `show_change()`, пише обобщението на езика на страницата с `exam_name()`,
     `subject_name()`, `unit_word()` и `region_list()`. Подава вида на изпита и езика на двете
     диаграми.
- **Пример:** НВО 7. клас, двата предмета: разликата нараства от 20,58 точки през 2018/2019 до
  26,79 през 2025/2026 (+30%). Спрямо разпръснатостта тя се променя от 1,37 на 1,53 (+12%):
  областите наистина са се раздалечили, но по-малко, отколкото подсказват точките. 20 области са
  под средното за страната във всяка година.
- **Извиква се от:** `map_view()` на страницата.

#### `drift_words(change, language)`: [ред 1168](../alex_school_results.py#L1168)
- **С едно изречение:** описва с думи промяната в разликата (спрямо разпръснатостта), на езика на
  страницата: „областите се раздалечиха“, „областите се сближиха“ или „почти без промяна“.
- **Как:** две проверки с `if` избират един от три ключа за превод (`"drift_apart"`,
  `"drift_closer"` или `"drift_same"`). Промяна, по-малка от 0,05 в която и да е посока, се смята
  за „почти без промяна“, защото е твърде малка, за да означава нещо.
- **Пример:** разликата в 10. клас нараства с 1,07 точки, но спрямо разпръснатостта се променя от
  1,28 на 1,21, така че `drift_words(-0.07, "en")` дава „the regions came closer“, а
  `drift_words(-0.07, "bg")` дава „областите се сближиха“.
- **Извиква се от:** `show_trends()`.

#### `trend_heatmap(gaps, kind, language)`: [ред 1180](../alex_school_results.py#L1180)
- **С едно изречение:** рисува решетката с по един ред за област и по една колона за учебна година;
  всяка клетка е оцветена според разстоянието на областта от средното за страната и в нея е
  написано числото.
- **Получава:** таблицата с разстоянията от `region_gaps()`, вида на изпита (`"nvo"` или `"dzi"`)
  и езика на страницата. От вида взема мерната единица (`unit_word()`) и броя на знаците след
  запетаята: един за точки, два за оценки. Заглавието на легендата и текстът на изскачащия прозорец
  идват от `translate()`.
- **Как:**
  1. `go.Heatmap(...)` е решетката на Plotly от оцветени клетки, със същите цветове и скала като на
     картата (`colour_key()`).
  2. `texttemplate="%{text}"` пише числото на всяка клетка (от `signed()`). Plotly избира бял или
     черен текст, така че се чете и на тъмни, и на светли клетки.
  3. `xgap=2, ygap=2` оставя тънка пролука между клетките. Годините са отгоре, написани от
     `year_labels()`.
- **Извиква се от:** `show_trends()`.

#### `gap_trend_chart(spread, relative, kind, language)`: [ред 1219](../alex_school_results.py#L1219)
- **С едно изречение:** линейна диаграма на разликата между най-добрата и най-слабата област,
  година по година. Линия, която се качва, означава, че областите се раздалечават.
- **Получава:** разликите в точки или оценки (`spread`), същите разлики, разделени на
  разпръснатостта на резултатите на училищата (`relative`), вида на изпита и езика на страницата.
  `unit_word()` превръща вида в мерна единица, като „points“ или „точки“.
- **Как:**
  1. `go.Scatter(mode="lines+markers+text")` рисува линия с точки. Само първата и последната
     година получават написано число, за да се чете линията лесно.
  2. Оста започва от 0, за да не се преувеличава покачването на линията, и стига 20% над най-високата
     точка, за да се побере числото ѝ.
  3. `customdata=relative.values` дава на всяка точка допълнително число, което изскачащият прозорец
     показва: „Разлика: 26.79 точки = 1.53 пъти разсейването на резултатите на училищата“.
- **Извиква се от:** `show_trends()`.

---

### Група 7: Уеб страницата и стартът

#### `language_buttons(language)`: [ред 1255](../alex_school_results.py#L1255)
- **С едно изречение:** прави четирите сини бутона за език до заглавието: EN, BG, RU и RO.
- **Получава:** езика на страницата. **Връща:** парче HTML, което `gr.HTML(...)` слага на
  страницата.
- **Как:**
  1. Цикъл минава през `LANGUAGES`, в реда на бутоните.
  2. Всеки бутон е **връзка** (`<a href="...">`) към страницата на този език: `/` за български
     (`FIRST_LANGUAGE`), `/en`, `/ru` и `/ro` за останалите.
  3. Собственият език на страницата получава `class="current"`, което CSS прави по-тъмно и
     подчертано, и `aria-current="page"`, което казва на екранните четци „това е страницата, на
     която сте“.
  4. `<nav aria-label="Language">` събира четирите връзки заедно, като меню.
- **Пример:** на английската страница бутонът EN е тъмносин и подчертан, а другите три са
  по-светлосини.
- **Извиква се от:** `build_language_page()`.

#### `build_language_page(page, exam_files, regions, language)`: [ред 1268](../alex_school_results.py#L1268)
- **С едно изречение:** изгражда версията на уеб страницата на един език (списъци, бутони, раздели,
  таблици) и решава коя функция да се изпълни, когато щракнете или промените нещо.
- **Получава:** приложението, което държи четирите страници (`page`), речника с файловете, списъка
  с области и езика. **Връща:** нищо: всичко, което прави, отива направо в приложението.
  `build_app()` я извиква 4 пъти, по веднъж за всеки език.
- **Как:**
  1. Създава малки **вътрешни функции**: `api`, `show`, `overview`, `refresh_towns`, `map_view`,
     `difference_view`, `change_view`, `trends_view` и `check_for_new_results`. Те помнят
     `exam_files` и `language`, така че Gradio трябва да им подаде само вашите избори.
  2. Всичко, което прави, се създава вътре в блок `with` на `build_app()`, затова става част от
     тази страница. `gr.Row()` слага нещата едно до друго; `gr.Tabs()` и `gr.Tab()` правят трите
     раздела.
  3. **Всеки текст идва от `translate()`,** на езика на страницата: заглавието, въведението,
     етикетите, бутоните и разделите.
  4. **Редът със заглавието:** заглавието отляво, а отдясно тясна колона
     (`gr.Column(scale=0, min_width=260)`) с бутоните за език от `language_buttons()`.
  5. **Списъците използват двойки (етикет, стойност):** „Изпит и учебна година“ получава
     `choice_list()`, първият елемент на „Област“ е `(преведеното "All regions", "All regions")` (на български `("Всички области", "All regions")`), а
     „Подреди училищата по“ и „Оцвети по“ получават `(subject_name(value), value)`. Така страницата
     показва преведени думи, а кодът пак получава английските стойности.
  6. **Цветовете на бутоните:** `elem_id="check-button"` дава име на зеления бутон, а
     `elem_classes="grey-button"` събира останалите бутони в група. CSS правилата, които ги
     оцветяват, са в `build_app()`. `gr.Tabs(elem_id="main-tabs")` дава име на лентата с разделите
     по същата причина.
  7. **`gr.State("difference")`** помни кой от трите изгледа на картата сте избрали последно. Не се
     рисува на страницата: това е малка памет, по една за всеки посетител.
  8. Свързва **събитията**: `нещо.събитие(функция, входове, изходи)` означава „когато това се
     случи, извикай тази функция със стойностите на тези входове и сложи резултатите ѝ в тези
     изходи“. `.then(...)` означава „след това направи и това“.
  9. **Имена в API:** Gradio предлага някои събития и на други програми, по име (неговото **API**).
     Две събития не може да имат едно и също име, а четирите страници имат едни и същи събития.
     Затова `api_name=api("show")` дава „show“ на българската страница, „show_en“ на английската и
     т.н. Останалите събития получават `api_name=False`: изобщо не се предлагат.

| Когато вие… | Gradio извиква |
|---|---|
| отворите страницата | `show()` |
| смените изпита или областта | `refresh_towns()`, после `show()` |
| изберете населено място или смените „Подреди училищата по“ | `show()` |
| щракнете „Покажи резултатите“ или натиснете Enter в полето за търсене | `show_schools_tab()`, после `show()` |
| щракнете „ИИ обзор на първите 5 (gemma4)“ | преминаване към втория раздел, после `overview()` |
| отворите раздела „Карта и тенденции на областите“, смените изпита или „Оцвети по“ | `map_view()`, с изгледа, който сте избрали последно |
| щракнете „Разлика от България“, „Промяна спрямо предходната година“ или „Тенденции през годините“ | `difference_view()`, `change_view()` или `trends_view()`, които извикват `map_view()` |
| щракнете зеления бутон „Провери за нови резултати“ | `check_for_new_results()` |
| щракнете EN, BG, RU или RO | никоя функция: бутонът е връзка и браузърът отваря страницата на този език |

- **Вътрешните функции** (създадени вътре в `build_language_page()`):
  - `api(name)` дава името на събитие в API: `name` на българската страница, `name_en`, `name_ru`
    или `name_ro` на останалите.
  - `show(choice, region, town, search, rank_by)` извиква `show_results(exam_files, …, language)`.
  - `overview(choice, region)` извиква `write_overview(exam_files, …, language)`. `yield from`
    предава всяко обновление, затова и тя е генератор.
  - `refresh_towns(choice, region, current_town)` извиква `town_choices()` и връща ново падащо
    меню с новия списък. Запазва вашето населено място, ако то все още е в списъка. Първият
    елемент на списъка е двойка (етикет, стойност), затова сравнява мястото ви само със
    **стойностите**.
  - `map_view(choice, subject, view)` извиква `show_map()`, `show_change()` или `show_trends()` —
    според изгледа. Връща изгледа (за `gr.State`), обобщението, двете диаграми с преведените им
    имена и трите бутона, като избраният е с отметка „✓“. Надписите на бутоните са текстовете
    `"view_<name>"` за всяко име в `MAP_VIEWS`. Картата се рисува, когато отворите раздела ѝ,
    защото диаграма, нарисувана в скрит раздел, може да излезе с грешен размер.
  - `difference_view`, `change_view` и `trends_view` са по един ред всяка: извикват `map_view()`
    със своя изглед. Бутонът не може да подаде фиксирана дума на функция, затова всеки получава
    своя малка функция.
  - `check_for_new_results(current_choice)` също е генератор:
    1. Първо показва „Проверка в data.egov.bg…“, после извиква `update_database()`.
    2. Попълва наново общия речник `exam_files` (`clear()`, после `update()`). Четирите страници
       използват този един речник, така че всяка част от всяка страница вижда новите години.
    3. Връща новия ред „Данни“ (`database_status()`) и нов списък „Изпит и учебна година“
       (`choice_list()`), като запазва текущия ви избор. Имената на новите файлове идват от
       `choice_label()`.
    4. Ако проверката се провали, например без интернет, показва грешката.
  - `show_schools_tab()` връща `gr.Tabs(selected="schools")`, което означава „отиди на раздела
    Училища“.
  - Малка `lambda`, функция от един ред без име, превключва към втория раздел.
- **`.input` или `.change`?**
  - `.input` реагира само на **вас**.
  - `.change` реагира и когато **кодът** промени стойността.
  - Списъкът с населени места използва `.input`, за да не се показват резултатите два пъти,
    когато `refresh_towns()` нулира избраното място.

#### `build_app(exam_files, regions)`: [ред 1434](../alex_school_results.py#L1434)
- **С едно изречение:** изгражда цялото приложение: българската страница на основния адрес и
  английската, руската и румънската страница на `/en`, `/ru` и `/ro`.
- **Получава:** речника с файловете и списъка с области. **Връща:** приложението, което `main()`
  после отваря.
- **Как:**
  1. `with gr.Blocks(...) as app:` създава приложението, а `build_language_page(app, …, "bg")`
     попълва главната му страница на български (`FIRST_LANGUAGE`). Заглавието на раздела в
     браузъра е българското заглавие.
  2. Цикъл минава през останалите езици. За всеки от тях `with app.route("EN", "/en"):` добавя
     **маршрут**: още една страница на собствен адрес. `build_language_page()` я попълва на този
     език.
  3. **CSS** (цветовете и размерите на страницата), подаден с `gr.Blocks(css=...)`:
     - `#check-button` оцветява зеления бутон: белият текст върху `#1a7f37` има контраст 5,1:1,
       така че се чете лесно. Става по-тъмен (`#116329`), когато мишката е над него.
     - `.grey-button` прави останалите бутони светлосиви (тъмен текст върху `#e9e9e7`, контраст
       13,6:1).
     - Правилата за `#main-tabs` превръщат трите раздела в **зелени бутони**, центрирани, с
       удебелен текст (`font-weight: 700`), един размер по-голям от обичайния (`--text-lg`, 16px,
       вместо `--text-md`, 14px). Белият текст върху `#1a7f37` има контраст 5,1:1.
       - Отвореният раздел има класа `selected`. Той получава по-тъмно зелено (`#0b4a1f`, 10,4:1)
         и подчертан текст, така че се вижда и без цветовете. Собствената оранжева линия на Gradio
         под него е скрита (`::after { display: none }`).
       - `gap: 8px` оставя малко място между бутоните. `flex-wrap: wrap` им позволява да минат на
         втори ред в тесен прозорец: иначе центрираните раздели биха се отрязали от двете страни.
     - `.language-buttons` кара връзките за език да изглеждат като сини бутони: бял текст върху
       `#0b5cad` (контраст 6,7:1). Текущият език (`a.current`) е по-тъмен, `#073d73` (10,9:1), и
       подчертан, така че се вижда и без цветовете.
     - `.nav-holder { display: none }` скрива собственото меню на Gradio със страниците, най-горе.
       Бутоните за език вършат неговата работа.
- **Извиква се от:** `main()`.

#### `main()`: [ред 1483](../alex_school_results.py#L1483)
- **С едно изречение:** началната точка: подготвя данните от базата, изгражда приложението и го
  отваря в браузъра.
- **Как:**
  1. `sys.stdout.reconfigure(...)` позволява на терминала в Windows да показва кирилица.
  2. `missing_translations()` проверява дали всеки текст го има и на 4-те езика. Ако някой липсва,
     отпечатва кои и спира, преди всичко останало.
  3. `stored_files()` чете списъка с файлове в базата.
  4. **Ако базата е празна** (първото стартиране или ако файлът е изтрит), `update_database()` я
     попълва от интернет, веднъж, за около минута. После отново `stored_files()`.
  5. `read_results()` за първия файл, само за да събере имената на областите.
  6. `build_app()` изгражда четирите страници.
  7. Ако нещо се обърка, отпечатва едно ясно съобщение и спира със `sys.exit(1)`. `1` е кодът за
     „грешка“.
  8. Предупреждава, ако липсва изпит или ако ИИ не е готов (`ollama_problem("en")`: съобщенията в
     терминала са на английски).
  9. `page.launch(inbrowser=True)` стартира уеб сървъра и отваря браузъра, на българската
     страница.
- **Не е нужен интернет:** когато в базата има данни, при старта нищо не се изтегля.
- **Последните два реда на файла:** `if __name__ == "__main__": main()` означава „изпълни
  `main()` само когато този файл е **стартиран** директно (`uv run …`), а не когато друг файл го
  **импортира**“. Благодарение на това можете да пробвате отделни функции самостоятелно (вижте
  съветите по-долу).

---

### Група 8: Текстовете на 4 езика ([translations.py](../translations.py))

Всеки текст, който страницата показва, е в този втори файл, на 4 езика. Основният скрипт иска
текст по неговия **ключ за превод** и езика на страницата. Във файла има:

| Име | Какво е |
|---|---|
| `LANGUAGES` | Четирите кода на езици и надписите на бутоните им, в реда на бутоните: `"en": "EN"`, `"bg": "BG"`, `"ru": "RU"`, `"ro": "RO"` |
| `FIRST_LANGUAGE` | `"bg"`: езикът на страницата на основния адрес, http://127.0.0.1:7860 |
| `LANGUAGE_NAMES` | Името на всеки език на английски, като `"bg": "Bulgarian"`, за да се каже на ИИ на какъв език да пише |
| `TEXTS` | Речник със 137 текста. Всеки ключ, като `"check_button"`, има малък речник със същия текст на 4-те езика |

**Какво остава същото на всеки език:**
- Имената на училищата, населените места и областите остават на кирилица, както са в данните.
  Никога не се превеждат.
- Числата с десетични знаци запазват точката, като „52.40“, както на диаграмите.
- Фактите, изпратени на ИИ, остават на английски; само отговорът му е на езика на страницата.

**Как да промените или добавите текст:**
1. Намерете ключа му в `TEXTS`. Например зеленият бутон е `"check_button"`.
2. За да го **промените**, променете го и на 4-те езика. Оставете всяко `{name}` във фигурни скоби
   както е: кодът ги попълва. Можете да ги местите в изречението.
3. За да **добавите** текст, добавете нов ключ с 4-те езика (`"en"`, `"bg"`, `"ru"`, `"ro"`), после
   го използвайте в кода с `translate("your_key", language)`.
4. Рестартирайте програмата. Ако липсва език, `missing_translations()` я спира със съобщение кой
   липсва.

#### `translate(key, language, **values)`: [ред 870](../translations.py#L870)
- **С едно изречение:** дава текста с име `key` на избрания език, с попълнени заместители.
- **Примери:** `translate("region_name", "en", region="ВАРНА")` → `"ВАРНА region"` ·
  `translate("region_name", "bg", region="ВАРНА")` → `"област ВАРНА"` ·
  `translate("never", "ru")` → `"никогда"`
- **`**values`:** двете звездички събират всички именувани стойности, които подадете, като
  `region="ВАРНА"`, в речник. Функция с `**values` може да приеме колкото са ѝ нужни.
- **Как:**
  1. `TEXTS[key][language]` намира текста: първо ключа, после езика.
  2. `text.format(**values)` попълва всяко `{name}` със стойността му.
  3. Попълва ги само ако има стойности. Някои текстове се използват в изскачащите прозорци на
     Plotly, а Plotly има свои кодове във фигурни скоби, като `%{x}`, които не бива да се пипат.
- **Извиква се от:** почти всяка функция на основния скрипт, която показва текст.

#### `whole_number(number, language)`: [ред 880](../translations.py#L880)
- **С едно изречение:** пише цяло число с разделени хиляди.
- **Примери:** `whole_number(53739, "en")` → `"53,739"` · `whole_number(53739, "bg")` → `"53 739"`
- **Защо интервал:** на български, руски и румънски запетаята е **десетична** запетая, така че
  „53,739“ би се прочело като число малко над 53, а не като почти 54 хиляди. Интервалът не може да
  се сбърка.
- **Как:** `f"{int(number):,}"` пише числото със запетаи; за всеки език освен английския
  `.replace(",", " ")` ги превръща в интервали.
- **Извиква се от:** `show_results()` (броят на училищата и на учениците).

#### `missing_translations()`: [ред 889](../translations.py#L889)
- **С едно изречение:** изброява текстовете, които липсват на някой език.
- **Връща:** списък като `["intro (ro)"]` или празен списък `[]`, когато всичко е налице.
- **Как:** едно **списъчно включване** (list comprehension — цикъл, написан вътре в `[ ]`) минава
  през всеки ключ и за всеки ключ през всеки език в `LANGUAGES`. `texts.get(language)` дава `None`,
  когато езикът липсва; тогава `not` е вярно и ключът влиза в списъка. Празен текст `""` също се
  брои за липсващ.
- **Извиква се от:** `main()`, преди всичко останало.

---

## 6. Съвети за разглеждане на кода

- **Пробвайте функция самостоятелно.** Изпълнете това от папката `education_bulgaria`, защото
  скриптът импортира `translations.py` от папката, в която сте (`-X utf8` кара терминала да
  показва кирилицата правилно):
  ```
  uv run python -X utf8 -c "from alex_school_results import tidy_town, to_number; print(tidy_town('ГР. СОФИЯ'), to_number('3,09'), to_number(''))"
  ```
  Отпечатва: `ГР.СОФИЯ 3.09 None`
- **Пробвайте текст на друг език,** от същата папка:
  ```
  uv run python -X utf8 -c "from translations import translate, whole_number; print(translate('check_button', 'bg'), whole_number(53739, 'ru'))"
  ```
  Отпечатва: `Провери за нови резултати 53 739`
- **Погледнете в базата данни** с един ред SQL, от папката на проекта:
  ```
  uv run python -X utf8 -c "import sqlite3; db = sqlite3.connect('education_bulgaria/school_results.db'); print(db.execute('SELECT choice, COUNT(*) FROM results GROUP BY choice ORDER BY choice LIMIT 3').fetchall())"
  ```
  Отпечатва първите 3 изпита и години с броя на училищата им, като започва с
  `('DZI (matura) - 2021/2022', 951)`. Ако предпочитате да щраквате, отворете файла с безплатната
  програма [DB Browser for SQLite](https://sqlitebrowser.org).
- **Погледнете във функция:** добавете `print(...)`, за да виждате стойностите ѝ, докато
  програмата работи, и после го махнете.
- **Променете настройка:** например `TOP = 10` в началото на файла дава първите 10 вместо
  първите 5. Рестартирайте програмата, за да видите промяната.
- **Четете в реда на пътищата:** започнете от `main()` и следвайте извикванията, както е показано
  в раздел 4.
