# School Exam Results in Bulgaria: Project Overview

This document describes the architecture, data and features of the project. The project is built in [alex_school_results.py](../alex_school_results.py), with the local database [school_results.db](../school_results.db) and the per-school archive in the [schools/](../schools/) folder.

---

## 1. Short summary

* **Official data source:** The Ministry of Education and Science (`mon.bg`) does not publish results for individual schools as tables on its web pages. It publishes them as open datasets on the **Open Data Portal of the Republic of Bulgaria** ([data.egov.bg](https://data.egov.bg)).
* **Scope:** The project covers **4 main datasets** (NVO (НВО) for 4th, 7th and 10th grade, and DZI (ДЗИ) for 12th grade). They have **25 yearly files** with data for **2,379 schools**, from the 2018/2019 to the 2025/2026 school year.
* **Application:** [alex_school_results.py](../alex_school_results.py) gives an interactive web dashboard (built with Gradio). It lets you filter, compare, rank, see a map of the inequality between the regions and how it changes over the years, and get an AI analysis of the results.
* **Local database:** The results are stored in the SQLite database [school_results.db](../school_results.db) (8.1 MB). The application starts in seconds and works without internet. It connects to the government sites only when you click the green **"Check for new results"** button.
* **School archive:** The [schools/](../schools/) folder holds a separate CSV file for each school, with the history of all its results (a snapshot as of 17 November 2026).

---

## 2. Data sources and API integration

> The government sites are used only to fill and update the local database: on the first start (if the database is empty) and when you click the green **"Check for new results"** button.

### Ministry of Education and Science (MON, МОН)
1. The script reads the official page [mon.bg → Open data](https://www.mon.bg/mon/dostap-do-informatsiya/otvoreni-danni/) with `BeautifulSoup`.
2. It extracts the link to the ministry's profile on the national open data portal (`organisation id 117`).
3. The public MON pages contain sample exam papers and grading scales. The individual results of students are on `infopriem.mon.bg`. They need an entry number and a code, so they are not public and are not processed.

### Open Data Portal (data.egov.bg)
All requests are HTTP `POST` requests to the API address `https://data.egov.bg/api/<method>` with a JSON body:
* `getOrganisationDetails`: Gets the internal numeric ID of MON.
* `listDatasets`: Lists the ministry's datasets (100 records per page).
* `listResources`: Returns the list of files (resources) for a given dataset.
* `getResourceData`: Downloads the contents of the selected file as table rows.

#### Main datasets:
| Exam | Dataset name on the portal | Years covered | Grading scale |
|---|---|---|---|
| **NVO (НВО), 4th grade** | Резултати по училища от националното външно оценяване за IV клас | 2020/21 – 2025/26 | Points (max. 100) |
| **NVO (НВО), 7th grade** | Резултати по училища от националното външно оценяване за VII клас | 2018/19 – 2025/26 | Points (max. 100) |
| **NVO (НВО), 10th grade** | Резултати по училища от националното външно оценяване за X клас | 2020/21 – 2025/26 | Points (max. 100) |
| **DZI (ДЗИ, matriculation exams)** | Резултати от държавните зрелостни изпити по училища и по предмети | 2021/22 – 2025/26 | Grade (from 2.00 to 6.00) |

> **Note on DZI:** For each year, only the regular session (May–June) with the compulsory exams is selected (Bulgarian language and literature (БЕЛ) and the second compulsory DZI / DIPPK (ДИППК)).

---

## 3. Data processing and normalisation

The incoming files from the government portal have a number of formatting differences. The script normalises them automatically:
* **Unique school key:** School names change and get shortened over the years. The project uses the **NEISPUO code (НЕИСПУО, Admin code)** as the only reliable unique identifier.
* **Code formatting:** Spaces are removed (e.g. `2 216 001` becomes `2216001`). This avoids artificial duplicate schools.
* **Normalising place names:** Spellings like `ГР. СОФИЯ` and `ГР.СОФИЯ` are made the same. The districts of Sofia are merged into `ГР.СОФИЯ`. Schools abroad are labelled consistently.
* **Grades and numbers:** Decimal commas (`3,09` → `3.09`), empty cells and zeros when no students sat the exam are handled.
* **Second compulsory DZI exam:** Graduates take different subjects for their second exam. So the script calculates one average grade for the second DZI, weighted by the number of students who sat each subject.
* **Weighted averages:** The overall averages for towns, regions and the whole country are always weighted by the number of students. They are not a simple average of the school averages.

---

## 4. Local database (`school_results.db`)

* **Format:** SQLite — built into Python (no extra installs). The whole database is one file, and you can query it with SQL.
* **Tables:**
  * `files` — one row for each results file, i.e. one exam in one school year (25 rows): exam, school year, type (`nvo` or `dzi`), the file's ID on data.egov.bg and the download date.
  * `results` — one row for each school in each file (35,292 rows), already cleaned and normalised.
  * `checks` — one row for each check for new results.
* **Speed:** Startup takes about 1 second instead of about 15. Loading one exam and year takes about 20 milliseconds instead of about 1 second.
* **Updating:** The green **"Check for new results"** button checks the portal (about 20 seconds). It downloads only the files that are missing from the database or that the ministry has replaced with a corrected version. Each file is saved in one transaction, so an interrupted update never leaves half a file.
* **First start:** If the database is missing or empty, the application fills it automatically (about a minute).
* **Verification:** The database built from all 25 files is identical to a fresh download of every file — every school, number, empty cell and column type.

---

## 5. Web application features (alex_school_results.py)

The user interface is built with **Gradio** (`gr.Blocks`) and has three tabs. Above them is a row with the database status (number of files and the date of the last check) and the green **"Check for new results"** button. All other buttons are light grey, so the green button stands out.

### The "Schools" tab
* **Filtering:** Choose the exam and school year, the region and the town or village (the list of towns and villages is filtered dynamically by the selected region).
* **Search:** Free-text search for a school, town or municipality (in Cyrillic).
* **Sorting:** Rank by Bulgarian language and literature (БЕЛ) or by mathematics / the second exam.
* **Summary statistics:**
  * Average result and number of students who sat the exam for the selected filter.
  * Direct comparison of the average result with the average for the region and for the country.
  * Rank of the selected town among all towns and villages in Bulgaria and in the region (a minimum number of students applies: at least 100 students at national level and at least 30 students within a region).

### The "Top 5 towns and schools + AI overview" tab
* **Ranking of the top 5 towns and schools:** Based on the overall average result of the two subjects.
* **Generating a structured text analysis:** With a local language model in **Ollama** (`gemma4`).
* **Architecture principle:** *All calculations are done by the program code, not by the language model.* The code calculates the differences from the average ("Vs area average") and passes the ready numbers to the model. This prevents maths errors and hallucinations.
* **Fallback without AI:** If Ollama is not running, the model is not downloaded, or an error happens while writing, the program writes the overview itself from the same numbers — instantly, with a note explaining why.

### The "Map and trends of the regions" tab
* **Always compared with the national average:** This removes the difference in test difficulty from year to year, so the years can be compared fairly.
* **Three views, switched with three light grey buttons:**
  * **"Difference from Bulgaria":** A map of the 28 regions, coloured by their difference from the national average: from dark red (far below average), through yellow (around average), to light green (far above average). Next to it is a bar chart with the exact difference for each region, and a summary of the differences: best versus weakest region, and towns versus villages.
  * **"Change since the previous year":** The same map and chart, coloured by how much each region's difference from the national average has changed since the previous year. The summary names the regions that improved the most and those that fell back the most, plus the typical change (the median), because small changes are often random fluctuations.
  * **"Trends over the years":** A table with coloured cells (one row for each region and one column for each year) showing the region's difference from the national average, and a line chart of the gap between the best and the weakest region. For example, for 7th grade this gap grows from 20.58 points (2018/19) to 26.79 points (2025/26).
    * In some years the test spreads students out more, and that alone makes the gap bigger. So the summary also compares the gap with the spread of school results in the same year (the standard deviation). By this measure, the 7th-grade gap grows by 12%, not by 30%, and only until 2021/22. For 10th grade, the regions even move slightly closer together.
* **The colours get lighter** as results improve, so all three views can be read by people with colour blindness and in black and white.
* **Note under the map:** the colours show differences in results, not the quality of the schools.
* **Region borders:** Natural Earth (public domain), in the file [bulgaria_regions.geojson](../bulgaria_regions.geojson).

---

## 6. Structure of the `schools/` folder

* **2,379 individual CSV files:** The file name format is `<school name> - <town> (<code>).csv`.
* **Index file:** `_all_schools.csv` lists all schools with their codes, regions, towns and the number of results available over the years.
* **Encoding:** The files are saved in `UTF-8 with BOM`, so the Cyrillic text opens without problems in Microsoft Excel.
* **Snapshot:** The files show the data as of 17 November 2026. The up-to-date copy, which gets updated, is the `school_results.db` database.

---

## 7. Running the project

### Requirements:
1. The Python package manager `uv` installed (or the libraries from [requirements.txt](../requirements.txt): `gradio`, `pandas`, `plotly`, `requests`, `beautifulsoup4`, `ollama`).
2. (Optional, for the AI analysis) **Ollama** running with a downloaded model. Without it, the program writes a simpler overview itself.
   ```bash
   ollama pull gemma4
   ```

### Command to run:
From the project's root folder:
```bash
uv run education_bulgaria/alex_school_results.py
```
From a downloaded copy of the GitHub repository:
```bash
python alex_school_results.py
```
The application starts in a few seconds from the database and opens automatically in the browser (usually at `http://127.0.0.1:7860`). You do not need internet to use it — it is needed only for the **"Check for new results"** button.
