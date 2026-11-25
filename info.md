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
- **A map of the 28 regions shows strong inequality:** in the latest year, only 4 to 8 regions are
  above the national average, depending on the exam, and in the 4th and 7th grade villages score
  17–19 points below cities.

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
- **The files are a snapshot from 17 November 2026.** The web page always downloads fresh data.

## The script: alex_school_results.py

1. **BeautifulSoup reads mon.bg's open data page** and finds the ministry's profile link on data.egov.bg.
   If mon.bg can't be reached, the script uses the profile id found there on 17 November 2026, so it
   still starts.
2. **`requests` calls the portal's API** to find the 4 datasets and their yearly files (about 17
   seconds at startup).
3. **Gradio (`gr.Blocks`) shows the page.**
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
   - **Minimum sizes,** so tiny villages and schools don't top the lists: 100 students per town
     nationally, 30 per town inside one region (with 100, most regions had only 1–2 ranked towns),
     and 10 per school.
   - **"Map of the regions" (third tab):** the 28 regions coloured by their distance from the national
     average, a bar chart with every region's exact number, and the biggest gaps. See the section
     below.
   - **Speed:** each file is downloaded once and remembered, so opening it again is instant.

Run it with `uv run education_bulgaria/alex_school_results.py` in this project, or with
`python alex_school_results.py` from a downloaded copy (see [README.md](README.md)). Ollama is only
needed for the AI overview; the rest of the page works without it.

### Lesson learned: let the code do the maths

In the first version, gemma4 calculated how far each town and school was above the average itself,
and about half of those figures were wrong. It wrote 13.04 instead of 14.04 for Sofia, and "60.04
points above" instead of 6.75 for Varna. Now the code calculates the difference ("Vs area average")
and the model only copies it: all 30 figures were correct across 3 test overviews.

The model is reliable at wording; the code has to provide every number.

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

### How the map was tested

- **All 25 files × 3 subjects (75 maps):** the data matches the borders and the colour range is
  centred on the average.
- **The real app was photographed in a background browser,** with the map tab clicked. That's how
  three layout problems were found and fixed: a region name hidden behind the chart's label, numbers
  touching the region names, and a colour key without signs.

## Not covered, and ideas

- **Not covered:** ДЗИ elective exams, the August–September retake session, files before 2018/19, and
  the personal results on infopriem.mon.bg (deliberately).
- **Ideas:**
  - a chart of one school's results over the years;
  - comparing two schools side by side;
  - adding the regional and national average to each school's row;
  - an AI summary of one school's results over the years (with the code calculating the trends).
