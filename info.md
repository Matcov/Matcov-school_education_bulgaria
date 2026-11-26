# Bulgarian school exam results: findings

Research notes for [alex_school_results.py](alex_school_results.py) and the [schools/](schools/) folder.
Data collected on 17 November 2026.

## In short

- **The results by school are not on mon.bg's web pages.** The Ministry of Education and Science (МОН)
  publishes them as open data on the national open data portal, **data.egov.bg**.
- There are **4 datasets** (НВО 4th, 7th and 10th grade, and ДЗИ) with **25 usable yearly files**,
  covering **2,379 schools** between 2018/2019 and 2025/2026.
- [alex_school_results.py](alex_school_results.py) shows them in a Gradio page.
  [schools/](schools/) has one CSV file per school with all its results.
- **The results are stored in a local SQLite database,** [school_results.db](school_results.db)
  (8.1 MB). The app starts in seconds, works offline, and contacts the government websites only when
  you click the green **Check for new results** button.
- **A map of the 28 regions shows strong inequality:** in the latest year, only 4 to 8 regions are
  above the national average, depending on the exam, and in the 4th and 7th grade villages score
  17–19 points below cities.
- **Over the years, the 7th grade regions drifted apart, but less than the points suggest:** the gap
  between the best and the worst region grew from 20.58 points in 2018/19 to 26.79 in 2025/26
  (+30%). The tests also spread students further apart, though. Compared with that spread, the gap
  grew by 12%, all of it by 2021/22, and has been flat since. In every exam, 20 of the 28 regions
  were below the national average in every year.

## Where the data is, and where it isn't

### mon.bg

- **robots.txt allows crawling** for everyone except YandexBot and Baiduspider.
- **The sitemap lists 10,464 pages.** The НВО and ДЗИ sections have exam papers, models, rules and
  marking scales, but **no tables of results by school**.
- **The announcements of results** ("Публикувани са резултатите…") only send students to
  **infopriem.mon.bg**, where each student checks their own result with an entry number and a code.
  That is personal data behind a login: **not used**.
- **The WordPress JSON API is switched off** (`/wp-json/` gives 404). Article text is in the HTML,
  inside `div.entry-content`.
- **The page that leads to the data** is
  [mon.bg → Отворени данни](https://www.mon.bg/mon/dostap-do-informatsiya/otvoreni-danni/). It links to
  the ministry's profile on the open data portal:
  `https://data.egov.bg/organisation/profile/a57a2273-6b21-4a7a-99ee-05ec4f67ebe4`

### data.egov.bg (national open data portal)

- **The ministry is organisation id 117**, with **351 datasets**.
- **4 of them are exam results by school, and they are kept up to date:**

| Exam | Dataset name on the portal | Dataset id | Years used | Schools per year | Scale |
|---|---|---|---|---|---|
| НВО 4th grade | Резултати по училища от националното външно оценяване за IV клас | `5613e75f-2b1b-4244-9f54-b27580a91dfb` | 2020/21 – 2025/26 | 1,738 – 1,768 | points, max 100 |
| НВО 7th grade | Резултати по училища от националното външно оценяване за VII клас | `b56288b6-25aa-4049-9aa6-de2cd4cdabf8` | 2018/19 – 2025/26 | 1,702 – 1,743 | points, max 100 |
| НВО 10th grade | Резултати по училища от националното външно оценяване за X клас | `2f801b2f-d4cb-4ddb-a23d-3e372339c80f` | 2020/21 – 2025/26 | 1,000 – 1,034 | points, max 100 |
| ДЗИ (матури) | Резултати от държавните зрелостни изпити по училища и по предмети | `066b4b04-d81d-444e-a61c-8ca0516079e4` | 2021/22 – 2025/26 | 951 – 976 | grade, 2 to 6 |

- **The ДЗИ dataset has 17 files** because each year has several sessions and exam types. Only the
  **compulsory exams of the May–June session** are used (one file per year).
- **Older datasets with similar names exist** (from 2018 and 2023). The script takes the most recently
  updated dataset with the exact name.

## The portal's API

All calls are `POST https://data.egov.bg/api/<method>` with a JSON body. No API key is needed to read.

| Method | Body | Returns |
|---|---|---|
| `getOrganisationDetails` | `{"org_uri": "<profile id>"}` | the organisation, with its numeric `id` |
| `listDatasets` | `{"criteria": {"org_ids": [117]}, "records_per_page": 100, "page_number": 1}` | datasets, 100 per page |
| `listResources` | `{"criteria": {"dataset_uri": "<dataset id>"}}` | the files in a dataset |
| `getResourceData` | `{"resource_uri": "<file id>"}` | the file's rows as lists of text |

Gotchas:
- **The portal answers HTTP 200 even on errors.** Check the `"success"` field.
- **`listDatasetResources` doesn't exist** (error "Непознат метод"), and `listResources` only works with
  `criteria`.
- **Keyword search (`criteria.keywords`) is unreliable.** "национално външно оценяване" returned
  air-quality bulletins. Listing the ministry's datasets and comparing names works better.
- **Listing the 351 datasets takes about 15 seconds.** Downloading one results file takes about 1 second.
  That's why the app keeps everything in a local database and calls the API only to fill or update
  it (see "The database" below).

## File layouts and quirks

**НВО files (9 columns):**
`Област, Община, Населено място, Училище, Код по НЕИСПУО, БЕЛ Явили се, БЕЛ Ср. успех в точки,
МАТ Явили се, МАТ Ср. успех в точки`

**ДЗИ files:** the same 5 school columns, then a pair of columns (`Бр.` = students, `Ср.усп.` = average
grade) for each subject. Bulgarian (`БЕЛ(ООП)`) comes first. Each student then takes one of the other
subjects, or the professional qualification exam (`ДИППК`), as their 2nd compulsory exam. The script
combines those into a single "2nd exam" average, weighted by the number of students.

**Caveat:** in 3–20 schools per year (out of about 970), more students took the 2nd exam than
Bulgarian. They are almost all vocational schools, where more students sat the professional
qualification exam (ДИППК) than Bulgarian that session. For those schools the "2nd exam" average
includes students who didn't sit Bulgarian. National totals are not affected (2025/2026: 49,027
students in Bulgarian, 48,159 in the 2nd exam).

Quirks the script handles:
- **The 7th grade 2022/2023 file has a title line** above the column names. The script starts at the
  row beginning with "Област".
- **In 7th grade 2018/2019 and 2019/2020, "Код" comes before "Училище".** The columns are found by name.
- **The 2020/2021 files write school codes with spaces** (`2 216 001`). Without removing the spaces,
  every school looked like two schools (4,252 instead of 2,379).
- **Some column names start with an invisible BOM character** (`﻿`), and older files use the label
  "Код по Админ". The codes are the same.
- **Older ДЗИ files use decimal commas** (`3,09`) and empty cells. Newer ones use `0` when nobody took
  an exam. Both are read as "no result".
- **Schools abroad are under the region "ЧУЖБИНА"**, spelled "В ЧУЖБИНА" in one file. The newest files
  list them under "СОФИЯ-ГРАД" instead (for example the school in БРАТИСЛАВА).
- **Town names vary too:** `ГР. СОФИЯ` instead of `ГР.СОФИЯ` in one year, Sofia districts instead of
  the city in a few files (`СОФИЯ 11 РН КРАСНА ПОЛЯНА`), and mixed case abroad (`Прага` and `ПРАГА`).
  The script makes them all the same.
- **School names vary between years.** Older files abbreviate them (`СМГ "П. Хилендарски"`,
  `ОУ "Хр. Ботев"`). 1,787 school codes have more than one spelling. **The school code is the reliable
  key**, not the name.
- **Skipped files with a different layout:** "Среден успех … по предмети в точки" (7th grade 2018,
  4th grade 2018 and 2019), ДЗИ before 2021/22, the ДЗИ August–September retake session, and ДЗИ elective exams
  ("по желание").

## Headline results, 2025/2026

Whole country. The averages are weighted by the number of students, calculated from the school
averages, so they may differ slightly from the ministry's official national figures.

| Exam | Schools | Bulgarian (БЕЛ) | Maths (НВО) / 2nd compulsory exam (ДЗИ) |
|---|---|---|---|
| НВО 4th grade | 1,738 | 76.39 points (53,522 students) | 62.71 points (53,245 students) |
| НВО 7th grade | 1,702 | 55.28 points (53,739 students) | 38.46 points (53,548 students) |
| НВО 10th grade | 1,034 | 45.49 points (55,062 students) | 30.34 points (53,233 students) |
| ДЗИ (матури) | 976 | 4.33 (49,034 students) | 4.77 (48,161 students) |

Top 3 schools by Bulgarian score:

| Exam | Bulgarian | Maths / 2nd exam | School |
|---|---|---|---|
| НВО 4th grade | 97.25 | 85.00 | Частно средно училище "Нов век", с. Кирилово |
| | 97.17 | 86.33 | Частно основно училище "Монтесори Варна – Веритас", Варна |
| | 96.64 | 93.19 | Частно основно училище "Света София", София |
| НВО 7th grade | 95.08 | 97.20 | Софийска математическа гимназия "Паисий Хилендарски", София |
| | 94.07 | 92.98 | Частно основно училище "Света София", София |
| | 93.22 | 95.30 | Математическа гимназия "Д-р Петър Берон", Варна |
| НВО 10th grade | 78.58 | 78.75 | Частно средно училище "Наука за деца", София |
| | 78.32 | 73.65 | 164. гимназия с преподаване на испански език "Мигел де Сервантес", София |
| | 77.39 | 43.05 | Национална гимназия за древни езици и култури "Константин Кирил Философ", София |
| ДЗИ (матури) | 5.78 | 5.89 | 91. Немска езикова гимназия "Професор Константин Гълъбов", София |
| | 5.75 | 5.78 | Софийска математическа гимназия "Паисий Хилендарски", София |
| | 5.72 | 5.16 | Национална гимназия за древни езици и култури "Константин Кирил Философ", София |

НВО 7th grade, national averages over time:

| School year | Bulgarian | Maths | Schools |
|---|---|---|---|
| 2018/2019 | 53.06 | 33.99 | 1,735 |
| 2019/2020 | 51.06 | 36.33 | 1,743 |
| 2020/2021 | 53.86 | 37.94 | 1,723 |
| 2021/2022 | 53.63 | 35.32 | 1,736 |
| 2022/2023 | 55.04 | 35.29 | 1,735 |
| 2023/2024 | 54.61 | 42.94 | 1,722 |
| 2024/2025 | 55.91 | 42.74 | 1,720 |
| 2025/2026 | 55.28 | 38.46 | 1,702 |

## The schools/ folder

- **One CSV file per school, 2,379 files**, named `<school name> - <town> (<school code>).csv`, for
  example `Софийска математическа гимназия Паисий Хилендарски - ГР.СОФИЯ (2216306).csv`.
  - **The name is the school's most recent name.** Quotes are removed because Windows doesn't allow
    them in file names.
  - **The code keeps the names unique**: many towns have an "Основно училище "Христо Ботев"".
- **Each file has one row per exam and year.** Columns: `Exam, School year, BEL students, BEL average,
  2nd subject, 2nd subject students, 2nd subject average, Scale, School, Town, Municipality, Region,
  School code`.
  - "School" is the name as written that year.
  - "2nd subject" is `MAT` for НВО and `2nd compulsory exam` for ДЗИ.
- **[_all_schools.csv](schools/_all_schools.csv) is the index**: every school with its region, town,
  code, number of results, exams and file name. Use it to find a school's file.
- **The files are saved as UTF-8 with BOM**, so Excel shows the Cyrillic correctly when you double-click
  them.
- **Most schools appear in only some exams,** depending on their grades: 1,149 schools have only
  НВО 4th and 7th grade; 464 have all four exams; 444 have only НВО 10th grade and ДЗИ.
- **The files are a snapshot from 17 November 2026.** The copy that gets updated is the database,
  [school_results.db](school_results.db).

## The script: alex_school_results.py

1. **The app reads the local database,** [school_results.db](school_results.db): no internet needed.
   - **If the database is empty** (the very first start), it fills it from the government websites,
     once, in about a minute.
   - **The green "Check for new results" button** does the same at any time, but downloads only the
     files that are new or that the ministry has replaced.
2. **Filling the database:**
   - **BeautifulSoup reads mon.bg's open data page** and finds the ministry's profile link on
     data.egov.bg. If mon.bg can't be reached, the script uses the profile id found there on
     17 November 2026.
   - **`requests` calls the portal's API** to find the 4 datasets and their yearly files (about 15
     seconds), then downloads and cleans each file it needs (about 1 second each).
3. **Gradio (`gr.Blocks`) shows the page.**
   - **At the top:** how many results files the database has and when it was last checked, with the
     green **Check for new results** button.
   - **Inputs:** exam and school year, region, town (the list follows the region; type to
     search), a search box (school, town or municipality, in Cyrillic), and rank by Bulgarian or
     Maths/2nd exam.
   - **Schools tab:** a summary with weighted averages, and the ranked table. It updates as soon as
     you change the exam, region, town or ranking. For the search box, press Enter or click
     "Show results".
     - **When a town is chosen,** the summary compares it with its region and Bulgaria, and gives
       its rank among towns: for example, in НВО 7th grade 2025/2026, Варна is #2 of 66 towns in
       Bulgaria and #1 of 12 in its region.
   - **"Write AI overview" (second tab):** two tables calculated by the code, then a short text
     written by gemma4 through Ollama, streamed word by word. It takes 1 to 3 minutes on a CPU.
     - **The tables** are the top 5 towns and the top 5 schools for the chosen exam and region,
       ranked by the average of both subjects, with each one's distance from the area's average.
     - **Without AI** (Ollama not running, the model missing, or an error halfway), the program
       writes the overview itself from the same numbers, instantly, and says why.
   - **Minimum sizes,** so tiny villages and schools don't top the lists: 100 students per town
     nationally, 30 per town inside one region (with 100, most regions had only 1–2 ranked towns),
     and 10 per school.
   - **"Map and trends of the regions" (third tab):** three buttons switch between three views of the 28
     regions, always compared with the national average: the difference from it, the change since
     the previous year, and the trends over the years. See the section below.
   - **The buttons are light grey** (dark text on `#e9e9e7`, a contrast of 13.6:1), except the green
     **Check for new results**, which stands out.
   - **Speed:** reading one exam and year from the database takes about 20 milliseconds.
4. **Four languages.** Blue **EN BG RU RO** buttons next to the title switch the whole page.
   - **Addresses:** Bulgarian at the plain address (http://127.0.0.1:7860), and English, Russian
     and Romanian at `/en`, `/ru` and `/ro`. Gradio builds them as 4 "routes" of one app, so each
     language can be shared as a link.
   - **One table of texts:** [translations.py](translations.py) holds all 137 texts, each in the
     4 languages. The app checks at start that none is missing.
   - **The code never changes language:** the lists show translated labels but give the code the
     English values, like "NVO 7th grade - 2025/2026". So the calculations are the same in every
     language. Tested: all 25 files × 3 subjects × 3 views, the Schools tab and the overview, in
     all 4 languages, with no text left untranslated.
   - **Kept as they are:** school, town and region names (as the ministry writes them), and the
     decimal point (55.28) in every language. Whole numbers get a space between thousands outside
     English (53 739), because "53,739" reads as a decimal in Bulgarian, Russian and Romanian.
   - **The AI overview** is written in the page's language. It gets the facts in English, which it
     reads best, and the instruction "Write the whole answer in Bulgarian" (or another language).
   - **Texts that needed plural forms were reworded,** like "Schools: 1,738" instead of
     "1738 schools", because Bulgarian and Russian change the word with the number.

Run it with `uv run education_bulgaria/alex_school_results.py` in this project, or with
`python alex_school_results.py` from a downloaded copy (see [README.md](README.md)). Ollama is only
needed for the AI-written overview; without it, the program writes a plainer one.

### Lesson learned: let the code do the maths

In the first version, gemma4 calculated how far each town and school was above the average itself,
and about half of those figures were wrong. It wrote 13.04 instead of 14.04 for Sofia, and "60.04
points above" instead of 6.75 for Varna. Now the code calculates the difference ("Vs area average")
and the model only copies it: all 30 figures were correct across 3 test overviews.

The model is reliable at wording; the code has to provide every number.

## The database

**Why:** before, every start asked the portal for its list of files (about 15 seconds), and every exam
and year was downloaded again after each restart (about 1 second each). Without internet, or when the
portal was down, the app couldn't start.

**The file:** [school_results.db](school_results.db) is an **SQLite** database. SQLite is built into
Python, so there's nothing to install; the whole database is one file; and it can be queried with SQL.

| Table | One row per | Columns |
|---|---|---|
| `files` | results file, meaning one exam in one school year (25 rows) | `choice` (like "NVO 7th grade - 2025/2026"), `exam`, `school_year`, `kind` ("nvo" or "dzi"), `resource_id` (the file's id on data.egov.bg), `downloaded_at` |
| `results` | school in each file (35,292 rows) | `choice`, `region`, `municipality`, `town`, `school`, `school_code`, `bel_students`, `bel_average`, `second_students`, `second_average` |
| `checks` | check of the portal | `checked_at`, `new_files` (how many files were added or replaced) |

- **The results are stored already cleaned:** every quirk listed above is fixed while downloading, so
  reading needs no more work.
- **An index on `results(choice)`** makes reading one exam and year fast.

**Measured:**

| | Before: from the internet | Now: from the database |
|---|---|---|
| Starting the app | about 15 s, just to list the files | about 1 s |
| Opening an exam and year | about 1 s per file, after every restart | about 20 ms |
| Without internet, or with the portal down | doesn't start | works |
| Size | n/a | 8.1 MB |

**Updating, with the green "Check for new results" button:**
1. **The same steps as before:** mon.bg, then the portal, then the list of files (about 20 seconds).
2. **It compares that list with the `files` table.** A file is downloaded if its exam and year are
   missing, **or if its file id changed**, which means the ministry replaced it with a corrected
   version.
3. **Each file is saved in one transaction:** the old rows are deleted and the new rows and the
   `files` row are written together. An interrupted update never leaves half a file.
4. **Every check is logged in `checks`,** which gives the "last checked" date at the top of the page.

**Tested:**
- **The database built from all 25 files is identical to a fresh download** of each file: every
  school, number, empty cell and column type.
- **A second check finds nothing new** and downloads nothing.
- **A simulated new year and a simulated corrected file:** I removed one file and changed another
  file's id, and exactly those 2 files were downloaded, with no duplicate rows.
- **A start with the internet switched off (simulated)** works from the database. The green button
  then reports the connection error instead of crashing.
- **The green button clicked in the real page** (in a background browser) reports "No new results:
  the database is up to date" and updates the "last checked" time.

**Looking inside:** any SQLite tool can open the file, for example the free
[DB Browser for SQLite](https://sqlitebrowser.org). Or, with one line of Python from the project
folder:
```
uv run python -X utf8 -c "import sqlite3; db = sqlite3.connect('education_bulgaria/school_results.db'); print(db.execute('SELECT choice, COUNT(*) FROM results GROUP BY choice ORDER BY choice LIMIT 3').fetchall())"
```
It prints the first 3 exams and years with their number of schools, starting with
`('DZI (matura) - 2021/2022', 951)`.

## The map of the regions

### The borders

- **Source:** [Natural Earth](https://www.naturalearthdata.com) 1:10m "Admin 1 – States, Provinces",
  which is in the **public domain**, so it's free to republish in a public repository. (GADM, another
  common source, doesn't allow redistribution.)
- **The world file is 40 MB.** [bulgaria_regions.geojson](bulgaria_regions.geojson) keeps only
  Bulgaria, which makes it **66 KB**:
  - 28 regions with the official ISO codes BG-01 to BG-28, and about 3,400 border points in total;
  - coordinates rounded to 4 decimals (about 10 m);
  - each region labelled with its name **exactly as written in the ministry's data**
    (`СОФИЯ-ГРАД`, `ВЕЛИКО ТЪРНОВО`…), so the map and the data match directly.
- **Checked:**
  - every region in all 25 files has a border, and every border has data;
  - the borders run in the direction the map library expects (otherwise it colours the whole world
    instead of the region);
  - Sofia city and Sofia region fit together like puzzle pieces, with no overlap.

### The colours

Dark red → red → orange → **yellow** (the national average) → light green. The scale is centred on
the average, so it shows the *difference* from the national average, and the colours mean the same
thing for points (НВО) and grades (ДЗИ).

The colours were measured, not picked by eye, using colour-blindness simulation (Machado 2009 model;
ΔE is the visible colour difference, and 8 or more is "easy to tell apart"):

| Scale | "Below average" vs "above average" for colour-blind readers | Darker = worse, even in black and white |
|---|---|---|
| Textbook diverging: dark red → pale → dark green | **ΔE 0.8, unreadable**: both ends look olive | No: both ends are dark |
| **Chosen: lighter as results get better** | **ΔE 13.3** (deuteranopia), 17.2 (protanopia) | **Yes** |

The weak point of the chosen scale: "a bit above average" and "far above average" are close
(ΔE 6.8). That's why every value is also shown as an **exact signed number** on the bar chart and in
the hover pop-ups.

### What the map shows (latest year, both subjects)

| Exam | Regions above the national average | Best region | Worst region | Gap between regions | Cities (ГР.) vs villages (С.) |
|---|---|---|---|---|---|
| НВО 4th grade | 8 of 28 | СОФИЯ-ГРАД (+8.90) | СЛИВЕН (−14.11) | 23.01 points | 72.27 vs 54.82: **17.45 points** |
| НВО 7th grade | 4 of 28 | СОФИЯ-ГРАД (+13.34) | СЛИВЕН (−13.45) | 26.79 points | 49.68 vs 30.95: **18.73 points** |
| НВО 10th grade | 6 of 28 | СОФИЯ-ГРАД (+8.21) | РАЗГРАД (−8.47) | 16.69 points | 38.20 vs 30.87: 7.33 points |
| ДЗИ (matura) | 7 of 28 | СОФИЯ-ГРАД (+0.26) | РАЗГРАД (−0.38) | 0.64 of a grade | 4.57 vs 3.97: 0.60 of a grade |

- **Why so few regions are above average:** the national average is weighted by students, and Sofia
  city has a large share of them, with the best results. So most regions sit below the national
  average.
- **Schools abroad are left out of the map**, because they have no region. Some files list them under
  ЧУЖБИНА, others under СОФИЯ-ГРАД (the school in БРАТИСЛАВА, for example); the map keeps only towns
  starting with "ГР." or "С.".
- **Under the map, a note explains** that the colours show differences in results, not the quality of
  the schools: results also depend on family income, town or village, and which students sit the
  exam.

### Comparing years: change and trends

**Why every view compares with the national average:** each year's test is different. The 7th grade
national average went from 43.53 points (2018/19) up to 49.33 (2024/25) and down to 46.87 (2025/26).
That mostly shows how hard each test was, not schools getting better or worse. So the app subtracts
each year's national average from each region's average, and compares those distances between years.

**The three views of the map tab:**
- **Difference from Bulgaria:** the map and bar chart described above.
- **Change since the previous year:** the same map and bar chart, coloured by how much each region's
  distance from the national average changed since the year before. The first year of each exam has
  no previous year, so the page says so instead.
- **Trends over the years:** a grid with one row per region and one column per year, each cell
  showing that region's distance from the national average, and a line chart of the gap between the
  best and the worst region. The summary also gives that gap compared with how spread out the
  schools' results were (see "Measuring the gap fairly" below).

**Change since the previous year (latest year, both subjects):**

| Exam | Improved most | Fell behind most | Typical movement |
|---|---|---|---|
| НВО 4th grade | ВРАЦА +2.85, КЮСТЕНДИЛ +2.76 | ЯМБОЛ −2.29, ВЕЛИКО ТЪРНОВО −2.24 | 0.71 points |
| НВО 7th grade | ДОБРИЧ +2.14, ПЕРНИК +1.76 | ЯМБОЛ −4.99, ПЛЕВЕН −2.04 | 0.98 points |
| НВО 10th grade | ЯМБОЛ +2.58, КЪРДЖАЛИ +2.08 | ШУМЕН −2.61, СЛИВЕН −2.34 | 0.85 points |
| ДЗИ (matura) | КЪРДЖАЛИ +0.15, ЛОВЕЧ +0.09 | ГАБРОВО −0.15, ВИДИН −0.11 | 0.03 of a grade |

- **"Typical movement"** is the median of how far the 28 regions moved: half moved less, half moved
  more. Most regions move less than a point a year, so a change of that size is often just noise.
- **One year is not a trend:** ЯМБОЛ fell behind most in the 7th grade (−4.99) but improved most in
  the 10th grade (+2.58).

**Trends over the years (both subjects):**

| Exam | Years | Gap between the best and worst region | Gap ÷ spread of the schools' results | Caught up most since the first year | Fell behind most since the first year |
|---|---|---|---|---|---|
| НВО 4th grade | 2020/21 – 2025/26 | 22.01 → 23.01 points | 1.32 → 1.41: drifted apart | ЛОВЕЧ +3.36 | РАЗГРАД −7.28 |
| НВО 7th grade | 2018/19 – 2025/26 | 20.58 → **26.79** points | 1.37 → **1.53**: drifted apart | СОФИЯ-ГРАД +2.30 | КЪРДЖАЛИ −6.55 |
| НВО 10th grade | 2020/21 – 2025/26 | 15.62 → 16.69 points | 1.28 → 1.21: came closer | ПЕРНИК +2.08 | СМОЛЯН −4.50 |
| ДЗИ (matura) | 2021/22 – 2025/26 | 0.74 → 0.64 of a grade | 1.02 → 0.87: came closer | КЪРДЖАЛИ +0.31 | ПАЗАРДЖИК −0.17 |

**Measuring the gap fairly.** Comparing with the national average cancels out how *easy* each test
was, but not how much it *spread the students apart*. A test that spreads students further apart
widens the gap between regions too, even if nothing really changed. So the app also divides the gap
by the **spread of the schools' results** that year (their standard deviation: roughly, how far a
typical school is from the average). The summary shows both numbers, and the line chart's pop-ups
show the second one.

7th grade, both subjects, year by year:

| | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|---|---|---|---|---|---|---|---|---|
| Gap between regions (points) | 20.58 | 21.95 | 23.55 | 24.65 | 23.78 | 23.79 | 25.56 | 26.79 |
| Spread of the schools' results (points) | 15.01 | 15.58 | 16.15 | 16.04 | 15.56 | 15.95 | 16.76 | 17.55 |
| Gap ÷ spread | 1.37 | 1.41 | 1.46 | 1.54 | 1.53 | 1.49 | 1.53 | 1.53 |

- **In the 7th grade the regions did drift apart, but less than the points suggest:** +30% in points,
  +12% compared with the spread. And it all happened by 2021/22. Since then, the growth in points
  comes from tests that spread students further apart, not from the regions. The two regions that
  pulled ahead most, СОФИЯ-ГРАД and ВАРНА, were already above the national average.
- **The 10th grade shows why this matters:** its gap grew by 1.07 points, but compared with the
  spread, the regions came a little closer.
- **In every exam, 20 of the 28 regions were below the national average in every year.**
- **The matura's gap shrank on both measures,** mostly because КЪРДЖАЛИ caught up.
- **"Caught up" and "fell behind" compare only the first and the last year,** so one unusual year at
  either end can change them. A typical region moves about 1 point a year, so changes of 2 to 3
  points over 6 years are borderline. The app's summary says so too.
- **The gap uses only the best and the worst region** (usually СОФИЯ-ГРАД against СЛИВЕН or
  РАЗГРАД). The grid shows what happens to the 26 regions in between.

### How the map and its views were tested

- **All 25 files × 3 subjects × 3 views (225 drawings)** work. The first year of each exam shows its
  message instead of a map.
- **The same 28 regions appear in every year of every exam,** so no region gets lost to a spelling
  difference between years.
- **The numbers were checked against a separate calculation.** The only difference was in the check
  itself: the 7th grade's typical movement is 0.98, not 1.04. The median of 28 numbers is the average
  of the 14th and the 15th (0.91 and 1.04), and the check had taken only the 15th.
- **The real app was photographed in a background browser,** with the map tab clicked. That's how
  three layout problems were found and fixed: a region name hidden behind the chart's label, numbers
  touching the region names, and a colour key without signs.
- **The three views were clicked through in the real page,** also with another exam chosen. That
  found 4 more layout problems, now fixed: an axis title cut off, slanted years hidden behind the
  chart's label, "-0.0" written in the grid, and the line chart's last number cut off at the top.
- **Lesson learned about browsers:** at first, the test browser reopened old tabs of the app from
  earlier tests. Every open tab of the app keeps connections to it, and a browser allows only 6
  connections to one server, so the new page's clicks waited forever. A fresh browser profile for
  every test fixed it. The same can happen with many tabs of the app open: close the extra tabs.

## Not covered, and ideas

- **Not covered:** ДЗИ elective exams, the August–September retake session, files before 2018/19, and
  the personal results on infopriem.mon.bg (deliberately).
- **Ideas:**
  - a chart of one school's results over the years;
  - comparing two schools side by side;
  - adding the regional and national average to each school's row;
  - an AI summary of one school's results over the years (with the code calculating the trends).
