"""
Bulgarian school exam results: a web page that shows the official exam results of every
school in Bulgaria, published by the Ministry of Education and Science (МОН, mon.bg).

How it gets the data:
1. The results are stored in a local SQLite database, school_results.db, next to this script.
   The app reads only this file, so it starts in a second and works without internet.
2. The database is filled from the government's websites only when it's empty, or when you
   click the green "Check for new results" button:
   - it reads mon.bg's open data page with BeautifulSoup and follows the ministry's link to
     the national open data portal (data.egov.bg), where the results by school are
     published as data files, not as pages on mon.bg;
   - it asks the portal's API for the ministry's exam result files (one per school year)
     and downloads only the ones the database doesn't have yet.

The exams:
- NVO (НВО, national external assessment) in 4th, 7th and 10th grade:
  average score in points (maximum 100) in Bulgarian (BEL) and Maths (MAT)
- DZI (ДЗИ, state matriculation exams, "матури") in 12th grade, May-June session:
  average grade from 2 to 6 in Bulgarian (BEL) and in the second compulsory exam

On the page you can also pick a town, to see how it compares with its region and the
country, and ask a local Ollama model (gemma4) for an overview of the top 5 towns and
top 5 schools. The rankings are calculated by the code; the model only writes about them.
When the AI isn't available, the program writes the overview itself, from the same numbers.

The "Map and trends of the regions" tab colours Bulgaria's 28 regions by how far their results
are from the national average, from dark red (far below) to light green (far above).

The page comes in 4 languages, with a button for each at the top: Bulgarian at the plain address,
and English, Russian and Romanian at /en, /ru and /ro. All its texts are in translations.py.

Before running:
- bulgaria_regions.geojson (the region borders for the map) and translations.py (the texts)
  must be next to this script.
  school_results.db is created and filled automatically the first time, if it's missing.
- For the AI overview: the Ollama app must be running, with the model downloaded:
  ollama pull gemma4. Without it, the program writes a plainer overview itself.

Run it from the project folder with:
    uv run education_bulgaria/alex_school_results.py
The page opens in your browser (usually at http://127.0.0.1:7860). Press Ctrl+C to stop.
"""

import json
import re
import sqlite3
import sys
from datetime import datetime
from functools import cache
from pathlib import Path

import gradio as gr
import ollama
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

# The page's texts in 4 languages, from translations.py next to this script. Python must look
# for it in this script's folder, also when the script is used from another folder
sys.path.insert(0, str(Path(__file__).parent))
from translations import FIRST_LANGUAGE, LANGUAGE_NAMES, LANGUAGES, missing_translations, translate, whole_number


# mon.bg's page that links to the ministry's data on the national open data portal
MON_OPEN_DATA_PAGE = "https://www.mon.bg/mon/dostap-do-informatsiya/otvoreni-danni/"

# The national open data portal's API: we send it a method name and get JSON back
PORTAL_API = "https://data.egov.bg/api/"

# The ministry's profile id on the portal, as found on mon.bg on 17 November 2026.
# Used only when mon.bg can't be reached, so the app still starts
KNOWN_MINISTRY_ID = "a57a2273-6b21-4a7a-99ee-05ec4f67ebe4"

# Both are public government websites, so we can say honestly who we are
headers = {"User-Agent": "alex-school-results (learning project)"}

# The local Ollama model that writes the AI overview
MODEL = "gemma4"
# gemma4 "thinks" (writes hidden reasoning) before it answers, unless told not to.
# On a CPU that makes the overview much slower, and this task doesn't need it.
THINK = False

# The exams we show, and the name of each one's dataset on the portal (in lower case).
# "nvo" files have scores in points, "dzi" files have grades from 2 to 6.
EXAMS = {
    "NVO 4th grade": ("nvo", "резултати по училища от националното външно оценяване за iv клас"),
    "NVO 7th grade": ("nvo", "резултати по училища от националното външно оценяване за vii клас"),
    "NVO 10th grade": ("nvo", "резултати по училища от националното външно оценяване за x клас"),
    "DZI (matura)": ("dzi", "резултати от държавните зрелостни изпити по училища и по предмети")
}

# The column names we show for each kind of exam
RESULT_COLUMNS = {
    "nvo": ["BEL students", "BEL points", "MAT students", "MAT points"],
    "dzi": ["BEL students", "BEL grade", "2nd exam students", "2nd exam grade"]
}

# The values the code uses for "all regions" and "all towns" in the lists. The page shows them
# translated; these stay the same in every language
ALL_REGIONS = "All regions"
ALL_TOWNS = "All towns"
# Bulgarian schools in other countries are listed under this "region"
ABROAD = "ЧУЖБИНА"
# The values of "Rank schools by" (the page shows them translated, from "subject: ..." in translations.py)
RANK_BY = ["Bulgarian (BEL)", "Maths / 2nd exam"]

# How many towns and schools the overview shows
TOP = 5
# Towns and schools are ranked only when at least this many students took both exams.
# Otherwise a village with one school of 6 strong students would come top.
MIN_TOWN_STUDENTS = 100
# Inside one region most towns are small: with 100, a region would have only 1 or 2 ranked towns
MIN_TOWN_STUDENTS_IN_REGION = 30
MIN_SCHOOL_STUDENTS = 10

# Some files start with an invisible "byte order mark" character
BOM = chr(0xFEFF)

# The local database with every results file already downloaded, next to this script.
# The app reads only this file; the government websites are contacted only when it's empty,
# or when you click "Check for new results"
DATABASE_FILE = Path(__file__).parent / "school_results.db"

# The database's tables, in SQL. They're created the first time the file is opened:
# - files: one row per results file (one exam in one school year), and when it was downloaded
# - results: one row per school in each file
# - checks: one row each time the portal was checked for new files
DATABASE_TABLES = """
CREATE TABLE IF NOT EXISTS files (
    choice        TEXT PRIMARY KEY,  -- like "NVO 7th grade - 2025/2026"
    exam          TEXT NOT NULL,     -- like "NVO 7th grade"
    school_year   TEXT NOT NULL,     -- like "2025/2026"
    kind          TEXT NOT NULL,     -- "nvo" (points) or "dzi" (grades)
    resource_id   TEXT NOT NULL,     -- the file's id on data.egov.bg
    downloaded_at TEXT NOT NULL      -- like "2026-11-25 14:05"
);
CREATE TABLE IF NOT EXISTS results (
    choice          TEXT NOT NULL REFERENCES files(choice),
    region          TEXT,
    municipality    TEXT,
    town            TEXT,
    school          TEXT,
    school_code     TEXT,
    bel_students    INTEGER,
    bel_average     REAL,
    second_students INTEGER,         -- Maths (НВО) or the 2nd compulsory exam (ДЗИ)
    second_average  REAL
);
CREATE INDEX IF NOT EXISTS results_by_file ON results(choice);
CREATE TABLE IF NOT EXISTS checks (
    checked_at TEXT NOT NULL,        -- like "2026-11-25 14:05"
    new_files  INTEGER NOT NULL      -- how many files were added or replaced
);
"""

# The results columns' names in the database (the page shows the names in RESULT_COLUMNS)
DATABASE_COLUMNS = ["region", "municipality", "town", "school", "school_code",
                    "bel_students", "bel_average", "second_students", "second_average"]

# The borders of Bulgaria's 28 regions, for the map: a small file next to this script,
# made from Natural Earth's public domain map data (naturalearthdata.com)
REGION_MAP_FILE = Path(__file__).parent / "bulgaria_regions.geojson"

# What the map can be coloured by (the page shows them translated, like RANK_BY)
MAP_SUBJECTS = ["Both subjects", "Bulgarian (BEL)", "Maths / 2nd exam"]

# The map tab's three views. Each one's button label is "view_<name>" in translations.py
MAP_VIEWS = ["difference", "change", "trends"]

# The map's colours, from far below the national average to far above it:
# dark red -> red -> yellow (about average) -> light green.
# They also get steadily lighter, so darker always means lower results, even in black and
# white or for colour-blind readers (checked with simulated colour blindness)
MAP_COLOURS = [[0.0, "#7a1416"], [0.25, "#c8432c"], [0.5, "#f0b84a"], [0.75, "#d8e88c"], [1.0, "#c4f1bd"]]

# The instructions for the AI model. The words in {curly brackets} are filled in for the page's
# language: the model writes in that language, with the headings translated
overview_system_prompt = """
You are an education data analyst. You write short, clear overviews of Bulgarian school
exam results for parents.
You get the exam, the area, the area's average scores, and two ranked lists in JSON:
the top towns and the top schools. The rankings are already done: keep their order.

Rules:
- Use only the numbers in the message. Do not invent scores, reasons, reputations or
  any other facts about a town or school.
- Do not calculate anything yourself. Every number you need is already in the JSON,
  including how far each town and school is from the area's average ("Vs area average").
- Keep town and school names exactly as written, in Cyrillic.
- "Both subjects" is the average of the two subjects.
- Do not ask questions. Do not write code. Do not wrap the answer in a code block.
- Write the whole answer in {language}.

Format your answer in markdown:
## {towns_heading}
One sentence introducing the list, then a numbered list with one short line per town:
its name, its "Both subjects" score, and its "Vs area average" text exactly as given.
## {schools_heading}
The same for the schools, with each school's town after its name.
End with one sentence about what the two lists have in common, only if the data shows
it (for example: most of the top schools are in the same town).
"""


def tidy(text):
    """
    Make names easy to compare: single spaces, lower case, no full stop at the end
    """
    return " ".join(text.split()).lower().rstrip(".")


def tidy_town(town):
    """
    Make town names the same in every file
    """
    # "Прага" and "ПРАГА" -> "ПРАГА"; double spaces -> single spaces
    town = " ".join(town.split()).upper()
    # One year writes "ГР. СОФИЯ" instead of "ГР.СОФИЯ"
    town = re.sub(r"^(ГР|С)\.\s+", r"\1.", town)
    # A few files give a Sofia district instead of the city, like "СОФИЯ 11 РН КРАСНА ПОЛЯНА"
    if re.match(r"^СОФИЯ \d+ РН", town):
        town = "ГР.СОФИЯ"
    return town


def call_portal(method, payload):
    """
    Call one method of the open data portal's API and return its answer
    """
    response = requests.post(PORTAL_API + method, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    answer = response.json()
    # The portal answers 200 even when something is wrong, and says so in "success"
    if not answer.get("success"):
        raise RuntimeError(f"The open data portal couldn't do '{method}': {answer.get('error')}")
    return answer


def find_ministry_on_portal():
    """
    Read mon.bg's open data page and find its link to the ministry's profile on the portal.
    Return the profile's id, which is part of the link
    """
    response = requests.get(MON_OPEN_DATA_PAGE, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        # The link looks like https://data.egov.bg/organisation/profile/a57a2273-...?q=...
        if "data.egov.bg/organisation/profile/" in href:
            return href.split("/profile/")[1].split("?")[0]
    raise RuntimeError(f"Couldn't find the link to the open data portal on {MON_OPEN_DATA_PAGE}")


def find_exam_datasets(ministry_id):
    """
    Return a dictionary of exam name -> id of its dataset on the portal
    """
    ministry = call_portal("getOrganisationDetails", {"org_uri": ministry_id})["data"]

    # The ministry has a few hundred datasets; the portal sends them 100 at a time
    datasets = []
    page = 1
    while True:
        answer = call_portal("listDatasets", {
            "criteria": {"org_ids": [ministry["id"]]},
            "records_per_page": 100,
            "page_number": page
        })
        datasets += answer["datasets"]
        if len(answer["datasets"]) < 100:
            break
        page += 1

    found = {}
    for exam, (_, dataset_name) in EXAMS.items():
        matches = [dataset for dataset in datasets if tidy(dataset["name"]) == dataset_name]
        if matches:
            # Some old datasets have the same name: take the one updated most recently
            newest = max(matches, key=lambda dataset: dataset["updated_at"])
            found[exam] = newest["uri"]
    return found


def list_exam_files(exam_datasets):
    """
    Return a dictionary of "exam - school year" -> where to download that file,
    newest year first for each exam
    """
    files = {}
    for exam, dataset_id in exam_datasets.items():
        kind = EXAMS[exam][0]
        resources = call_portal("listResources", {"criteria": {"dataset_uri": dataset_id}})["resources"]
        found = []
        for resource in resources:
            name = resource["name"]
            year = re.search(r"учебна (\d{4}/\d{4})", name)
            if year is None:
                continue    # older files in a different layout, without "учебна 2025/2026"
            # For the matura, keep the main session's compulsory exams (May-June)
            if kind == "dzi" and not ("задължителни" in name and "май-юни" in name):
                continue
            found.append((year.group(1), resource["uri"]))
        for year, resource_id in sorted(found, reverse=True):
            files[f"{exam} - {year}"] = (kind, resource_id)
    return files


def to_number(text):
    """
    Turn "52.4" or "3,09" into a number. Empty cells and zeros mean nobody took
    that exam, so they become None
    """
    try:
        value = float(str(text).strip().replace(",", "."))
    except ValueError:
        return None
    return value or None


def download_results(kind, resource_id):
    """
    Download one results file from the open data portal and return it as a clean table:
    one row per school. Used only to fill the database
    """
    rows = call_portal("getResourceData", {"resource_uri": resource_id})["data"]

    # Some files have a title line above the column names: start at the row beginning with "Област"
    start = next(i for i, row in enumerate(rows) if row and row[0].replace(BOM, "").strip() == "Област")
    header = rows[start]
    # In a few years "Код" (school code) comes before "Училище" (school), so find them by name
    school_column = next(i for i, name in enumerate(header) if "Училище" in name)
    code_column = next(i for i, name in enumerate(header) if "Код" in name)

    schools = []
    for row in rows[start + 1:]:
        if not row[school_column].strip():
            continue
        numbers = [to_number(cell) for cell in row]
        if kind == "nvo":
            # The last 4 columns: BEL students, BEL points, MAT students, MAT points
            results = numbers[-4:]
        else:
            # Columns 5 and 6 are Bulgarian; after that, a (students, grade) pair per subject.
            # Each student takes one of those subjects as the 2nd compulsory exam,
            # so we combine them into one average, weighted by the number of students
            pairs = [(count, grade) for count, grade in zip(numbers[7::2], numbers[8::2]) if count and grade]
            second_count = sum(count for count, _ in pairs)
            second_grade = sum(count * grade for count, grade in pairs) / second_count if second_count else None
            results = [numbers[5], numbers[6], second_count or None, second_grade]
        # One year spells the schools abroad "В ЧУЖБИНА" instead of "ЧУЖБИНА"
        region = ABROAD if row[0].strip() == "В " + ABROAD else row[0].strip()
        # The 2020/2021 files write codes with spaces, like "2 216 001": remove them
        code = re.sub(r"\s", "", row[code_column])
        school = " ".join(row[school_column].split())
        schools.append([region, row[1].strip(), tidy_town(row[2]), school, code] + results)

    table = pd.DataFrame(schools, columns=["Region", "Municipality", "Town", "School", "School code"] + RESULT_COLUMNS[kind])
    students = RESULT_COLUMNS[kind][0::2]
    averages = RESULT_COLUMNS[kind][1::2]
    # Int64 shows whole numbers without ".0" and allows empty cells
    table[students] = table[students].astype("Int64")
    table[averages] = table[averages].round(2)
    return table


def open_database():
    """
    Open the database file (SQLite creates it the first time) and make sure its tables exist.
    Whoever opens it must close it again with .close()
    """
    database = sqlite3.connect(DATABASE_FILE)
    database.executescript(DATABASE_TABLES)
    return database


def save_results(choice, kind, resource_id, table):
    """
    Store one downloaded results file in the database, replacing an older copy of it
    """
    rows = table.set_axis(DATABASE_COLUMNS, axis=1).assign(choice=choice)
    exam, school_year = choice.rsplit(" - ", 1)
    database = open_database()
    try:
        # "with database" makes all of this one transaction: either everything is saved, or nothing
        with database:
            database.execute("DELETE FROM results WHERE choice = ?", (choice,))
            rows.to_sql("results", database, if_exists="append", index=False)
            database.execute("INSERT OR REPLACE INTO files VALUES (?, ?, ?, ?, ?, ?)",
                             (choice, exam, school_year, kind, resource_id, datetime.now().strftime("%Y-%m-%d %H:%M")))
    finally:
        database.close()


def stored_files():
    """
    Return a dictionary of "exam - school year" -> (kind, file id) for every file in the
    database, in the same order as the portal list: exam by exam, newest year first
    """
    database = open_database()
    try:
        files = database.execute("SELECT choice, exam, school_year, kind, resource_id FROM files").fetchall()
    finally:
        database.close()
    exam_order = list(EXAMS)
    # First newest year first, then exam by exam: Python's sort keeps the year order inside each exam
    files.sort(key=lambda file: file[2], reverse=True)
    files.sort(key=lambda file: exam_order.index(file[1]) if file[1] in exam_order else len(exam_order))
    return {choice: (kind, resource_id) for choice, _, _, kind, resource_id in files}


def read_results(choice, kind):
    """
    Read one exam and year from the database, as a table with the page's column names
    """
    database = open_database()
    try:
        table = pd.read_sql("SELECT " + ", ".join(DATABASE_COLUMNS) + " FROM results WHERE choice = ? ORDER BY rowid",
                            database, params=(choice,))
    finally:
        database.close()
    table.columns = ["Region", "Municipality", "Town", "School", "School code"] + RESULT_COLUMNS[kind]
    # Int64 shows whole numbers without ".0" and allows empty cells
    students = RESULT_COLUMNS[kind][0::2]
    table[students] = table[students].astype("Int64")
    return table


def update_database():
    """
    Ask the open data portal for its list of results files, and download the ones the
    database doesn't have yet, or that the ministry has replaced with a new version.
    Return the list of files that were added or replaced
    """
    try:
        ministry_id = find_ministry_on_portal()
    except (requests.exceptions.RequestException, RuntimeError):
        # mon.bg only tells us where the data is: if it's down, use the id we found there before
        ministry_id = KNOWN_MINISTRY_ID
    print("Asking data.egov.bg for the list of results files...", flush=True)
    portal_files = list_exam_files(find_exam_datasets(ministry_id))
    stored = stored_files()
    new_files = [choice for choice, file in portal_files.items() if stored.get(choice) != file]
    for choice in new_files:
        kind, resource_id = portal_files[choice]
        print(f"Downloading {choice} ...", flush=True)
        save_results(choice, kind, resource_id, download_results(kind, resource_id))

    database = open_database()
    try:
        with database:
            database.execute("INSERT INTO checks VALUES (?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M"), len(new_files)))
    finally:
        database.close()
    return new_files


def database_status(language):
    """
    A one-line description of the database, for the top of the page
    """
    database = open_database()
    try:
        files = database.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        last_check = database.execute("SELECT MAX(checked_at) FROM checks").fetchone()[0]
    finally:
        database.close()
    return translate("data_status", language, files=files, database=DATABASE_FILE.name,
                     last_check=last_check or translate("never", language))


def exam_name(exam, language):
    """
    An exam's name in the page's language: "NVO 7th grade" -> "НВО 7. клас" in Bulgarian
    """
    return translate(f"exam: {exam}", language)


def choice_label(choice, language):
    """
    How an exam and year appears in the list, in the page's language:
    "NVO 7th grade - 2025/2026" -> "НВО 7. клас - 2025/2026" in Bulgarian.
    The code keeps using the English choice; only the label is translated
    """
    exam, year = choice.rsplit(" - ", 1)
    return f"{exam_name(exam, language)} - {year}"


def choice_list(exam_files, language):
    """
    The "Exam and school year" list: (label, value) pairs. Gradio shows the label and gives
    the code the value, so the code always gets the English choice
    """
    return [(choice_label(choice, language), choice) for choice in exam_files]


def subject_name(subject, language):
    """
    "Both subjects", "Bulgarian (BEL)" or "Maths / 2nd exam" in the page's language
    """
    return translate(f"subject: {subject}", language)


def shown_table(table, language):
    """
    A copy of a table with its column names in the page's language, ready to show.
    The code works with the English names; only what you see is translated
    """
    return table.rename(columns=lambda column: column if column == "#" else translate(f"column: {column}", language))


def load_choice(exam_files, choice, language):
    """
    Return the kind of exam ("nvo" or "dzi") and the results table for a dropdown choice,
    from the database, with a message on the page if it can't be read
    """
    if choice not in exam_files:
        raise gr.Error(translate("choose_exam", language))
    kind, _ = exam_files[choice]
    try:
        return kind, read_results(choice, kind)
    except (sqlite3.Error, pd.errors.DatabaseError) as error:
        raise gr.Error(translate("database_error", language, error=error))


def weighted_average(table, count_column, average_column):
    """
    The average over all students, not over schools: a school with 100 students
    counts more than one with 5
    """
    taken = table.dropna(subset=[count_column, average_column])
    students = taken[count_column].sum()
    if students == 0:
        return None, 0
    return (taken[count_column] * taken[average_column]).sum() / students, students


def town_label(town, region):
    """
    How a town appears in the dropdown. The region is included because many village
    names exist in several regions
    """
    return f"{town} ({region})"


def split_town_label(label):
    """
    "ГР.ВАРНА (ВАРНА)" -> ("ГР.ВАРНА", "ВАРНА")
    """
    town, region = label.rsplit(" (", 1)
    return town, region.rstrip(")")


def town_choices(exam_files, choice, region, language):
    """
    The towns for the dropdown: those with schools in the chosen exam and region.
    Cities ("ГР.") come before villages ("С.") because of the alphabetical order.
    The first one, "All towns", is a (label, value) pair: translated label, English value
    """
    _, table = load_choice(exam_files, choice, language)
    # An empty region box means the same as "All regions"
    if region and region != ALL_REGIONS:
        table = table[table["Region"] == region]
    towns = table[["Town", "Region"]].drop_duplicates()
    return [(translate("all_towns", language), ALL_TOWNS)] + sorted(town_label(row.Town, row.Region) for row in towns.itertuples())


def rank_towns(table, kind, min_students):
    """
    One row per town, with its averages weighted by students, best first.
    Ranked by the average of both subjects; only towns where at least
    min_students students took each exam are included
    """
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]
    towns = []
    for (region, town), schools in table.groupby(["Region", "Town"]):
        bel, bel_count = weighted_average(schools, bel_students, bel_average)
        second, second_count = weighted_average(schools, second_students, second_average)
        if bel is None or second is None or min(bel_count, second_count) < min_students:
            continue
        towns.append({
            "Town": town, "Region": region, "Schools": len(schools), "Students": int(bel_count),
            bel_average: round(bel, 2), second_average: round(second, 2),
            "Both subjects": round((bel + second) / 2, 2)
        })
    ranked = pd.DataFrame(towns, columns=["Town", "Region", "Schools", "Students", bel_average, second_average, "Both subjects"])
    ranked = ranked.sort_values("Both subjects", ascending=False)
    ranked.insert(0, "#", range(1, len(ranked) + 1))
    return ranked


def rank_schools(table, kind):
    """
    The schools, best first by the average of both subjects; only schools where at least
    MIN_SCHOOL_STUDENTS students took each exam are included
    """
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]
    # fillna(0): a missing number of students counts as "too few"
    big_enough = (table[bel_students].fillna(0) >= MIN_SCHOOL_STUDENTS) & (table[second_students].fillna(0) >= MIN_SCHOOL_STUDENTS)
    schools = table[big_enough].dropna(subset=[bel_average, second_average])
    schools = schools[["School", "Town", "Region", bel_students, bel_average, second_average]].copy()
    schools["Both subjects"] = ((schools[bel_average] + schools[second_average]) / 2).round(2)
    schools = schools.rename(columns={bel_students: "Students"})
    schools = schools.sort_values("Both subjects", ascending=False)
    schools.insert(0, "#", range(1, len(schools) + 1))
    return schools


def show_results(exam_files, choice, region, town, search, rank_by, language):
    """
    Filter and rank the schools, and write a summary above the table.
    When a town is chosen, the summary compares it with its region and the country
    """
    kind, everything = load_choice(exam_files, choice, language)
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]

    # Pick the schools to show, and the wider areas to compare them with
    table = everything
    compare_with = []
    if town and town != ALL_TOWNS:
        town_name, town_region = split_town_label(town)
        region_table = everything[everything["Region"] == town_region]
        table = region_table[region_table["Town"] == town_name]
        compare_with = [(translate("region_name", language, region=town_region), region_table),
                        (translate("bulgaria", language), everything)]
        area = town
    elif region and region != ALL_REGIONS:
        table = everything[everything["Region"] == region]
        compare_with = [(translate("bulgaria", language), everything)]
        area = region
    else:
        area = translate("all_regions", language)

    if search and search.strip():
        text = search.strip()
        matches = (
            table["School"].str.contains(text, case=False, regex=False)
            | table["Town"].str.contains(text, case=False, regex=False)
            | table["Municipality"].str.contains(text, case=False, regex=False)
        )
        table = table[matches]

    sort_column = bel_average if rank_by == RANK_BY[0] else second_average
    # Best first; schools without a result for that exam go to the end
    table = table.sort_values(sort_column, ascending=False, na_position="last")
    table.insert(0, "#", range(1, len(table) + 1))

    scale = translate("scale_nvo" if kind == "nvo" else "scale_dzi", language)
    summary = [translate("summary_head", language, choice=choice_label(choice, language), area=area,
                         count=whole_number(len(table), language))]
    for count_column, average_column in [(bel_students, bel_average), (second_students, second_average)]:
        average, students = weighted_average(table, count_column, average_column)
        if average is None:
            continue
        # "BEL points" -> "BEL", "2nd exam grade" -> "2nd exam", then translated
        subject = translate("short: " + average_column.rsplit(" ", 1)[0], language)
        line = translate("subject_line", language, subject=subject, average=f"{average:.2f}", scale=scale,
                         students=whole_number(students, language))
        for name, other in compare_with:
            other_average, _ = weighted_average(other, count_column, average_column)
            if other_average is not None:
                line += f" · {name}: {other_average:.2f}"
        summary.append(line)

    if town and town != ALL_TOWNS:
        ranks = []
        for ranked, where, minimum in [
            (rank_towns(everything, kind, MIN_TOWN_STUDENTS), translate("rank_in_bulgaria", language), MIN_TOWN_STUDENTS),
            (rank_towns(region_table, kind, MIN_TOWN_STUDENTS_IN_REGION),
             translate("rank_in_region", language, region=town_region), MIN_TOWN_STUDENTS_IN_REGION)
        ]:
            here = ranked[(ranked["Town"] == town_name) & (ranked["Region"] == town_region)]
            if not here.empty:
                ranks.append(translate("rank_item", language, rank=here["#"].iloc[0], total=len(ranked), where=where, minimum=minimum))
        if ranks:
            summary.append(translate("town_rank", language, ranks=" · ".join(ranks)))
        else:
            summary.append(translate("not_ranked", language, minimum=MIN_TOWN_STUDENTS_IN_REGION))
    if table.empty:
        summary.append("\n" + translate("no_match", language))
    return "\n".join(summary), shown_table(table, language)


def ollama_problem(language):
    """
    Return None if Ollama is running and the model is downloaded,
    otherwise a message that says what's wrong
    """
    try:
        models = requests.get("http://localhost:11434/api/tags", timeout=5).json()["models"]
    except requests.exceptions.RequestException:
        return translate("ollama_not_running", language)
    # Ollama treats a model name without a tag as ":latest"
    wanted = MODEL if ":" in MODEL else MODEL + ":latest"
    if wanted not in [model["name"] for model in models]:
        return translate("model_missing", language, model=MODEL)
    return None


def overview_messages(choice, kind, area, area_averages, towns, schools, min_town_students, language):
    """
    Build the list of messages for the model: our instructions, then the facts in JSON.
    The facts are in English, which the model reads best; it writes its answer in the page's language
    """
    system_prompt = overview_system_prompt.format(
        language=LANGUAGE_NAMES[language],
        towns_heading=translate("heading_towns", language),
        schools_heading=translate("heading_schools", language)
    )
    scale = "average points out of 100" if kind == "nvo" else "average grade from 2 (lowest) to 6 (highest)"
    subjects = "Bulgarian (BEL) and Maths (MAT)" if kind == "nvo" else "Bulgarian (BEL) and the 2nd compulsory matura exam"
    # ensure_ascii=False keeps the Cyrillic names readable instead of turning them into codes
    towns_json = json.dumps(towns.to_dict(orient="records"), indent=2, ensure_ascii=False)
    schools_json = json.dumps(schools.to_dict(orient="records"), indent=2, ensure_ascii=False)
    request = (
        f"Exam: {choice}\n"
        f"Scores: {scale}\n"
        f"Subjects: {subjects}\n"
        f"Area: {area}\n"
        f"Area averages: {area_averages}\n\n"
        f"Top towns (only towns where at least {min_town_students} students took each exam):\n{towns_json}\n\n"
        f"Top schools (only schools where at least {MIN_SCHOOL_STUDENTS} students took each exam):\n{schools_json}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request}
    ]


def template_overview(area, towns, schools, language):
    """
    The overview written by the program itself, from the same numbers the AI gets.
    Used when the AI isn't available: plainer than the AI's text, but instant and always exact
    """
    lines = ["## " + translate("heading_towns", language)]
    if towns.empty:
        lines.append(translate("no_town_ranked", language, area=area))
    else:
        lines.append(translate("best_towns_intro", language, area=area))
        for town in towns.to_dict(orient="records"):
            lines.append(translate("town_item", language, rank=town["#"], town=town["Town"],
                                   score=f"{town['Both subjects']:.2f}", difference=town["Vs area average"]))

    lines += ["", "## " + translate("heading_schools", language)]
    if schools.empty:
        lines.append(translate("no_school_ranked", language, area=area))
    else:
        lines.append(translate("best_schools_intro", language, area=area))
        for school in schools.to_dict(orient="records"):
            lines.append(translate("school_item", language, rank=school["#"], school=school["School"], town=school["Town"],
                                   score=f"{school['Both subjects']:.2f}", difference=school["Vs area average"]))
        # What the list has in common: the town where most of the top schools are
        towns_count = schools["Town"].value_counts()
        if towns_count.iloc[0] == len(schools) and len(schools) > 1:
            lines.append("\n" + translate("all_top_in", language, town=towns_count.index[0]))
        elif towns_count.iloc[0] > len(schools) / 2:
            lines.append("\n" + translate("most_top_in", language, town=towns_count.index[0]))
    return "\n".join(lines)


def write_overview(exam_files, choice, region, language):
    """
    Rank the top towns and schools for the chosen exam and region and show them
    straight away, then stream the model's overview of them as it is written.
    Each step yields the two tables (with their column names translated) and the text so far
    """
    # An empty region box means the same as "All regions", as on the Schools tab
    region = region or ALL_REGIONS
    kind, table = load_choice(exam_files, choice, language)
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]
    if region != ALL_REGIONS:
        table = table[table["Region"] == region]
    area = translate("area_all", language) if region == ALL_REGIONS else translate("region_name", language, region=region)
    min_town_students = MIN_TOWN_STUDENTS if region == ALL_REGIONS else MIN_TOWN_STUDENTS_IN_REGION

    towns = rank_towns(table, kind, min_town_students).head(TOP).copy()
    schools = rank_schools(table, kind).head(TOP).copy()
    if towns.empty and schools.empty:
        yield shown_table(towns, language), shown_table(schools, language), translate("not_enough_data", language, area=area)
        return

    # How far each town and school is from the area's average. The code calculates this,
    # because language models often get subtractions wrong (we saw gemma4 write 13.04 for 14.04)
    bel, _ = weighted_average(table, bel_students, bel_average)
    second, _ = weighted_average(table, second_students, second_average)
    area_both = (bel + second) / 2
    area_averages = f"{bel_average} {bel:.2f}, {second_average} {second:.2f}, both subjects {area_both:.2f}"
    for ranked in (towns, schools):
        ranked["Vs area average"] = [
            translate("amount_above" if score >= area_both else "amount_below", language, amount=f"{abs(score - area_both):.2f}")
            for score in ranked["Both subjects"]
        ]
    towns_shown, schools_shown = shown_table(towns, language), shown_table(schools, language)

    problem = ollama_problem(language)
    if problem:
        # No AI: the program writes the overview itself, from the same numbers
        yield towns_shown, schools_shown, (template_overview(area, towns, schools, language) + "\n\n"
                                           + translate("written_without_ai", language, problem=problem))
        return
    yield towns_shown, schools_shown, translate("ai_writing", language, model=MODEL)

    text = ""
    try:
        stream = ollama.chat(
            model = MODEL,
            messages = overview_messages(choice, kind, area, area_averages, towns, schools, min_town_students, language),
            stream = True,
            think = THINK,
            options = {
                # A low temperature makes the model stick closer to the facts it was given
                "temperature": 0.3,
                # Safety net against a runaway answer: two lists of 5 never need more than this
                "num_predict": 900
            }
        )
        for chunk in stream:
            text += chunk.message.content
            yield towns_shown, schools_shown, text
    except Exception as error:
        # Any failure (Ollama closed, a timeout...): the program writes the overview instead,
        # and says why, rather than leaving half a text or Gradio's generic "Error"
        yield towns_shown, schools_shown, (template_overview(area, towns, schools, language) + "\n\n"
                                           + translate("ai_failed", language, error=f"{type(error).__name__}: {error}"))


def schools_in_bulgaria(table):
    """
    Leave out the schools abroad. In Bulgaria every town starts with "ГР." (city) or "С." (village);
    some files list the schools abroad under ЧУЖБИНА, others under a Bulgarian region
    """
    in_bulgaria = table["Town"].str.startswith(("ГР.", "С.")) & (table["Region"] != ABROAD)
    return table[in_bulgaria]


def subject_score(schools, kind, subject):
    """
    The average of a group of schools in the chosen subject, weighted by students.
    "Both subjects" is the average of the two. None if there are no results
    """
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]
    bel, _ = weighted_average(schools, bel_students, bel_average)
    second, _ = weighted_average(schools, second_students, second_average)
    if subject == MAP_SUBJECTS[1]:
        return bel
    if subject == MAP_SUBJECTS[2]:
        return second
    if bel is None or second is None:
        return None
    return (bel + second) / 2


def school_spread(schools, kind, subject):
    """
    How spread out the schools' results are: the standard deviation of their scores in the
    chosen subject. Some years' tests spread students further apart than others, which also
    widens the gap between regions, so the trends compare that gap with this spread
    """
    bel_average, second_average = RESULT_COLUMNS[kind][1], RESULT_COLUMNS[kind][3]
    if subject == MAP_SUBJECTS[1]:
        scores = schools[bel_average]
    elif subject == MAP_SUBJECTS[2]:
        scores = schools[second_average]
    else:
        scores = (schools[bel_average] + schools[second_average]) / 2
    return scores.std()


# @cache: the map file is read once, the first time the map is shown
@cache
def load_region_map():
    """
    Read the borders of Bulgaria's 28 regions from the map file next to this script
    """
    with open(REGION_MAP_FILE, encoding="utf-8") as file:
        return json.load(file)


def colour_key(values, zero_label):
    """
    The colour scale for a set of numbers above and below 0: its two ends, and the labels
    of its key, like "-13", "-7", "0 = average", "+7", "+13". The ends are the same distance
    from 0 both ways, so 0 is always the middle colour (yellow)
    """
    limit = values.abs().max()
    if pd.isna(limit) or limit < 0.01:
        limit = 0.01
    # Fewer decimals for big numbers (points), more for small ones (grades and their changes)
    decimals = 0 if limit >= 5 else 1 if limit >= 0.5 else 2
    ticks = [-limit, -limit / 2, 0, limit / 2, limit]
    labels = [f"{tick:+.{decimals}f}" if tick else zero_label for tick in ticks]
    return limit, ticks, labels


def signed(value, decimals=2):
    """
    A number with its sign, like "+2.14" or "-4.99", for the numbers written on the charts.
    A number that rounds to zero is written without a sign: "0.00", not "-0.00"
    """
    text = f"{value:+.{decimals}f}"
    return text[1:] if float(text) == 0 else text


def year_labels(years):
    """
    School years written on two lines, like "2018/" above "2019", so they fit under
    narrow columns without being slanted
    """
    return [year.replace("/", "/<br>") for year in years]


def region_map(regions, borders, column, key_title, zero_label):
    """
    The map: each region coloured by the numbers in one column of `regions`, like its
    distance from the national average, or how much that distance changed since last year.
    `regions` also has a "Hover" column: the text shown when the mouse is over a region
    """
    limit, ticks, tick_labels = colour_key(regions[column], zero_label)
    figure = go.Figure(go.Choropleth(
        geojson = borders,
        # Match the map's regions to the data by their Bulgarian names, like "СОФИЯ-ГРАД"
        featureidkey = "properties.region",
        locations = regions["Region"],
        z = regions[column],
        zmin = -limit,
        zmax = limit,
        colorscale = MAP_COLOURS,
        marker_line_color = "#6b6b6b",
        marker_line_width = 0.6,
        colorbar = dict(title=key_title, tickvals=ticks, ticktext=tick_labels, len=0.8, thickness=14),
        customdata = regions["Hover"],
        hovertemplate = "%{customdata}<extra></extra>"
    ))
    # Show only Bulgaria's regions, without the world map around them
    figure.update_geos(fitbounds="locations", visible=False, bgcolor="#fcfcfb")
    figure.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#fcfcfb")
    return figure


def region_bars(regions, column, axis_title):
    """
    The same regions as a bar chart: highest at the top, lowest at the bottom, with each
    region's exact number written next to its bar, so it can be read without colours.
    `regions` must already be sorted by `column`, lowest first
    """
    limit, _, _ = colour_key(regions[column], "")
    figure = go.Figure(go.Bar(
        x = regions[column],
        y = regions["Region"],
        orientation = "h",
        marker = dict(color=regions[column], colorscale=MAP_COLOURS, cmin=-limit, cmax=limit,
                      line=dict(color="#6b6b6b", width=0.6)),
        text = [signed(value) for value in regions[column]],
        textposition = "outside",
        cliponaxis = False,
        customdata = regions["Hover"],
        hovertemplate = "%{customdata}<extra></extra>"
    ))
    figure.update_layout(
        height = 660,
        # Room at the top, so the chart's label doesn't cover the first region's name
        margin = dict(l=10, r=10, t=40, b=40),
        paper_bgcolor = "#fcfcfb",
        plot_bgcolor = "#fcfcfb",
        # Zero in the middle, with room for the numbers on both sides
        xaxis = dict(title=axis_title, range=[-limit * 1.6, limit * 1.6],
                     zeroline=True, zerolinecolor="#444444", gridcolor="#e6e6e3"),
        yaxis = dict(automargin=True),
        bargap = 0.25,
        barcornerradius = 4
    )
    return figure


def unit_word(kind, language):
    """
    The unit of an exam's scores in the page's language: "points" for НВО, "grade" for ДЗИ
    """
    return translate("unit_points" if kind == "nvo" else "unit_grade", language)


def show_map(exam_files, choice, subject, language):
    """
    The map tab: a summary of the biggest gaps, then the map and the bar chart of the
    28 regions, coloured by how far each region is from the national average
    """
    kind, table = load_choice(exam_files, choice, language)
    table = schools_in_bulgaria(table)
    subject = subject or MAP_SUBJECTS[0]
    unit = unit_word(kind, language)
    try:
        borders = load_region_map()
    except OSError:
        return translate("map_missing", language, file=REGION_MAP_FILE.name), None, None

    national = subject_score(table, kind, subject)
    regions = pd.DataFrame(
        [{"Region": region, "Schools": len(schools), "Score": subject_score(schools, kind, subject)}
         for region, schools in table.groupby("Region")],
        columns = ["Region", "Schools", "Score"]
    ).dropna(subset=["Score"])
    if national is None or regions.empty:
        return translate("no_results_subject", language, subject=subject_name(subject, language),
                         choice=choice_label(choice, language)), None, None
    regions["Vs Bulgaria"] = regions["Score"] - national
    regions = regions.sort_values("Vs Bulgaria")
    # The text shown when the mouse is over a region or its bar. The region names are in Bulgarian;
    # the pages in Latin letters (English, Romanian) also give the English name, like "ВАРНА (Varna)"
    english = {feature["properties"]["region"]: feature["properties"]["name_en"] for feature in borders["features"]}
    regions["Hover"] = [
        f"<b>{region}</b>{' (' + english.get(region, '') + ')' if language in ('en', 'ro') else ''}"
        f"<br>{translate('hover_average', language)}: {score:.2f}"
        f"<br>{translate('hover_vs_bulgaria', language)}: {difference:+.2f}"
        f"<br>{translate('hover_schools', language)}: {schools}"
        for region, score, difference, schools in zip(regions["Region"], regions["Score"], regions["Vs Bulgaria"], regions["Schools"])
    ]

    worst, best = regions.iloc[0], regions.iloc[-1]
    cities = subject_score(table[table["Town"].str.startswith("ГР.")], kind, subject)
    villages = subject_score(table[table["Town"].str.startswith("С.")], kind, subject)
    summary = [
        translate("map_head", language, choice=choice_label(choice, language), subject=subject_name(subject, language),
                  national=f"{national:.2f}", unit=unit),
        translate("best_worst", language, best=best["Region"], best_score=f"{best['Score']:.2f}",
                  best_difference=f"{best['Vs Bulgaria']:+.2f}", worst=worst["Region"], worst_score=f"{worst['Score']:.2f}",
                  worst_difference=f"{worst['Vs Bulgaria']:+.2f}", gap=f"{best['Score'] - worst['Score']:.2f}", unit=unit)
    ]
    if cities is not None and villages is not None:
        summary.append(translate("cities_villages", language, cities=f"{cities:.2f}", villages=f"{villages:.2f}",
                                 gap=f"{cities - villages:.2f}", unit=unit))
    return (
        "\n".join(summary),
        region_map(regions, borders, "Vs Bulgaria", translate("key_vs_bulgaria", language, unit=unit),
                   translate("zero_average", language)),
        region_bars(regions, "Vs Bulgaria", translate("bars_axis", language, unit=unit))
    )


def exam_years(exam_files, choice):
    """
    All the files of the same exam as `choice`, oldest year first,
    like "NVO 7th grade - 2018/2019" ... "NVO 7th grade - 2025/2026"
    """
    exam = choice.rsplit(" - ", 1)[0]
    return sorted(other for other in exam_files if other.rsplit(" - ", 1)[0] == exam)


def region_gaps(exam_files, choices, subject, language):
    """
    Each region's distance from the national average, for each of the given exams and years:
    a table with one row per region and one column per school year. Also returns the national
    averages and how spread out the schools' results were, year by year. Comparing with each
    year's own national average cancels out how easy or hard that year's test was
    """
    scores, national, spread = {}, {}, {}
    for choice in choices:
        kind, table = load_choice(exam_files, choice, language)
        table = schools_in_bulgaria(table)
        year = choice.rsplit(" - ", 1)[1]
        national[year] = subject_score(table, kind, subject)
        spread[year] = school_spread(table, kind, subject)
        scores[year] = {region: subject_score(schools, kind, subject) for region, schools in table.groupby("Region")}
    national = pd.Series(national, dtype=float)
    # Rows: regions, columns: years. Subtract each year's national average from its column
    gaps = pd.DataFrame(scores, dtype=float).sub(national, axis=1)
    return gaps, national, pd.Series(spread, dtype=float)


def region_list(regions_and_changes, language):
    """
    A few regions with their changes for a summary line, like "**ДОБРИЧ** +2.14, **ПЕРНИК** +1.76",
    or "none" in the page's language
    """
    return ", ".join(f"**{region}** {change:+.2f}" for region, change in regions_and_changes) or translate("none", language)


def show_change(exam_files, choice, subject, language):
    """
    The "Change since the previous year" view: how far each region moved compared with the
    national average, between the previous year and the chosen one
    """
    kind, _ = load_choice(exam_files, choice, language)
    subject = subject or MAP_SUBJECTS[0]
    unit = unit_word(kind, language)
    years = exam_years(exam_files, choice)
    position = years.index(choice)
    if position == 0:
        return translate("first_year", language, choice=choice_label(choice, language)), None, None
    try:
        borders = load_region_map()
    except OSError:
        return translate("map_missing", language, file=REGION_MAP_FILE.name), None, None

    gaps, national, _ = region_gaps(exam_files, [years[position - 1], choice], subject, language)
    before, now = gaps.columns
    regions = gaps.rename(columns={before: "Before", now: "Now"}).dropna().rename_axis("Region").reset_index()
    regions["Change"] = regions["Now"] - regions["Before"]
    regions = regions.sort_values("Change")
    regions["Hover"] = [
        f"<b>{region}</b><br>{translate('hover_change', language)}: {change:+.2f}"
        f"<br>{translate('hover_vs_bulgaria_in', language, year=now)}: {after:+.2f}"
        f"<br>{translate('hover_vs_bulgaria_in', language, year=before)}: {earlier:+.2f}"
        for region, change, after, earlier in zip(regions["Region"], regions["Change"], regions["Now"], regions["Before"])
    ]

    improved = regions[regions["Change"] > 0].iloc[::-1].head(3)
    fell_behind = regions[regions["Change"] < 0].head(3)
    summary = [
        translate("change_head", language, exam=exam_name(choice.rsplit(" - ", 1)[0], language), before=before, now=now,
                  subject=subject_name(subject, language)),
        translate("improved_most", language, regions=region_list(zip(improved["Region"], improved["Change"]), language)),
        translate("fell_behind_most", language, regions=region_list(zip(fell_behind["Region"], fell_behind["Change"]), language)),
        translate("typical_movement", language, amount=f"{regions['Change'].abs().median():.2f}", unit=unit),
        translate("national_moved", language, before=f"{national[before]:.2f}", now=f"{national[now]:.2f}",
                  change=f"{national[now] - national[before]:+.2f}")
    ]
    return (
        "\n".join(summary),
        region_map(regions, borders, "Change", translate("key_change", language, unit=unit), translate("zero_no_change", language)),
        region_bars(regions, "Change", translate("change_axis", language, unit=unit))
    )


def show_trends(exam_files, choice, subject, language):
    """
    The "Trends over the years" view: every region's distance from the national average in
    every year of the chosen exam, and how the gap between the best and worst region changed
    """
    kind, _ = load_choice(exam_files, choice, language)
    subject = subject or MAP_SUBJECTS[0]
    unit = unit_word(kind, language)
    years = exam_years(exam_files, choice)
    exam = exam_name(choice.rsplit(" - ", 1)[0], language)
    if len(years) < 2:
        return translate("one_year_only", language, exam=exam), None, None

    gaps, _, school_spreads = region_gaps(exam_files, years, subject, language)
    gaps = gaps.dropna(how="all")
    first, last = gaps.columns[0], gaps.columns[-1]
    # Best region at the top of the grid: Plotly draws the first row at the bottom
    gaps = gaps.sort_values(last)
    # The gap between the best and the worst region, year by year
    spread = gaps.max() - gaps.min()
    # The same gap divided by how spread out the schools' results were that year. A test that
    # spreads students further apart widens the gap in points even if nothing really changed,
    # so this is the fairer way to see whether the regions are drifting apart
    relative = spread / school_spreads
    # How much each region moved compared with the national average, from the first year to the last
    moved = (gaps[last] - gaps[first]).dropna().sort_values()
    caught_up = moved[moved > 0].iloc[::-1].head(3)
    fell_behind = moved[moved < 0].head(3)
    summary = [
        translate("trends_head", language, exam=exam, first=first, last=last, subject=subject_name(subject, language)),
        translate("gap_line", language, first_gap=f"{spread[first]:.2f}", first=first, last_gap=f"{spread[last]:.2f}",
                  last=last, change=f"{spread[last] - spread[first]:+.2f}", unit=unit),
        translate("relative_line", language, first_relative=f"{relative[first]:.2f}", last_relative=f"{relative[last]:.2f}",
                  drift=drift_words(relative[last] - relative[first], language)),
        translate("caught_up_since", language, first=first, regions=region_list(caught_up.items(), language)),
        translate("fell_behind_since", language, first=first, regions=region_list(fell_behind.items(), language)),
        translate("every_year", language, below=int((gaps < 0).all(axis=1).sum()), above=int((gaps > 0).all(axis=1).sum())),
        translate("endpoints_note", language)
    ]
    return "\n".join(summary), trend_heatmap(gaps, kind, language), gap_trend_chart(spread, relative, kind, language)


def drift_words(change, language):
    """
    Put a change in the gap compared with the spread into words. Changes smaller than 0.05
    of the spread are too small to mean anything
    """
    if change >= 0.05:
        return translate("drift_apart", language)
    if change <= -0.05:
        return translate("drift_closer", language)
    return translate("drift_same", language)


def trend_heatmap(gaps, kind, language):
    """
    A grid with one row per region and one column per school year: each cell is coloured by
    the region's distance from that year's national average, with the number written in it
    """
    limit, ticks, tick_labels = colour_key(pd.Series(gaps.values.ravel()), translate("zero_average", language))
    unit = unit_word(kind, language)
    # Points are big numbers, so one decimal is enough; grades need two
    decimals = 1 if kind == "nvo" else 2
    figure = go.Figure(go.Heatmap(
        z = gaps.values,
        x = list(gaps.columns),
        y = list(gaps.index),
        zmin = -limit,
        zmax = limit,
        colorscale = MAP_COLOURS,
        text = [[signed(value, decimals) if pd.notna(value) else "" for value in row] for row in gaps.values],
        texttemplate = "%{text}",
        textfont = dict(size=10),
        # A thin gap between the cells, so each one is easy to tell apart
        xgap = 2,
        ygap = 2,
        colorbar = dict(title=translate("key_vs_bulgaria", language, unit=unit), tickvals=ticks, ticktext=tick_labels,
                        len=0.6, thickness=14),
        # %{y}, %{x} and %{z} are Plotly's codes for the cell's region, year and number
        hovertemplate = "<b>%{y}</b>, %{x}<br>" + translate("hover_vs_bulgaria", language) + ": %{z:+.2f}<extra></extra>"
    ))
    figure.update_layout(
        height = 760,
        # Room at the top for the years, below the chart's label
        margin = dict(l=10, r=10, t=75, b=10),
        paper_bgcolor = "#fcfcfb",
        plot_bgcolor = "#fcfcfb",
        xaxis = dict(side="top", tickvals=list(gaps.columns), ticktext=year_labels(gaps.columns), tickangle=0),
        yaxis = dict(automargin=True)
    )
    return figure


def gap_trend_chart(spread, relative, kind, language):
    """
    A line chart of the gap between the best and the worst region, year by year:
    a rising line means the regions are drifting apart. The pop-up of each point also
    gives the gap compared with how spread out the schools' results were that year
    """
    unit = unit_word(kind, language)
    figure = go.Figure(go.Scatter(
        x = list(spread.index),
        y = spread.values,
        mode = "lines+markers+text",
        # The numbers only on the first and last year, so the line stays easy to read
        text = [f"{value:.2f}" if position in (0, len(spread) - 1) else "" for position, value in enumerate(spread.values)],
        textposition = "top center",
        # The numbers may stand above the top of the chart without being cut off
        cliponaxis = False,
        line = dict(color="#2a78d6", width=2),
        marker = dict(size=8, color="#2a78d6"),
        customdata = relative.values,
        # %{x}, %{y} and %{customdata} are Plotly's codes for the point's year, gap and gap ÷ spread
        hovertemplate = (f"%{{x}}<br>{translate('hover_gap', language)}: %{{y:.2f}} {unit}<br>"
                         f"= %{{customdata:.2f}} {translate('hover_times_spread', language)}<extra></extra>")
    ))
    figure.update_layout(
        height = 340,
        margin = dict(l=10, r=20, t=50, b=40),
        paper_bgcolor = "#fcfcfb",
        plot_bgcolor = "#fcfcfb",
        # From 0, with room above the highest point for its number
        yaxis = dict(title=translate("gap_axis", language, unit=unit), range=[0, spread.max() * 1.2], gridcolor="#e6e6e3"),
        xaxis = dict(tickvals=list(spread.index), ticktext=year_labels(spread.index), tickangle=0, gridcolor="#e6e6e3"),
        showlegend = False
    )
    return figure


def language_buttons(language):
    """
    The 4 blue language buttons next to the title: links to the 4 versions of the page.
    The page's own language is darker and marked as the current one
    """
    links = []
    for code, label in LANGUAGES.items():
        address = "/" if code == FIRST_LANGUAGE else f"/{code}"
        current = ' class="current" aria-current="page"' if code == language else ""
        links.append(f'<a href="{address}" hreflang="{code}"{current}>{label}</a>')
    return '<nav class="language-buttons" aria-label="Language">' + "".join(links) + "</nav>"


def build_language_page(page, exam_files, regions, language):
    """
    Build one language's version of the web page, inside `page`, the app that holds all 4.
    gr.Blocks (instead of gr.Interface) lets the town list change when you pick a region,
    and gives the AI overview its own button
    """
    choices = list(exam_files)
    # Start with the newest 7th grade results: the ones parents look at the most
    default = next((choice for choice in choices if choice.startswith("NVO 7th grade")), choices[0])

    def api(name):
        """
        Each event's name for Gradio's API must be different in each language: "show", "show_en"...
        """
        return name if language == FIRST_LANGUAGE else f"{name}_{language}"

    def show(choice, region, town, search, rank_by):
        return show_results(exam_files, choice, region, town, search, rank_by, language)

    # Gradio streams the overview only when it gets a generator function
    def overview(choice, region):
        yield from write_overview(exam_files, choice, region, language)

    def refresh_towns(choice, region, current_town):
        towns = town_choices(exam_files, choice, region, language)
        # Keep the chosen town if it's still in the list. The list's first item is a (label, value) pair
        values = [town[1] if isinstance(town, tuple) else town for town in towns]
        return gr.Dropdown(choices=towns, value=current_town if current_town in values else ALL_TOWNS)

    # The map tab has three views. This draws the chosen one, names its two charts,
    # and puts a tick on the chosen view's button
    def map_view(choice, subject, view):
        if view == "change":
            text, first_chart, second_chart = show_change(exam_files, choice, subject, language)
            chart_names = ["chart_change_map", "chart_change_bars"]
        elif view == "trends":
            text, first_chart, second_chart = show_trends(exam_files, choice, subject, language)
            chart_names = ["chart_trend_grid", "chart_trend_gap"]
        else:
            text, first_chart, second_chart = show_map(exam_files, choice, subject, language)
            chart_names = ["chart_map", "chart_bars"]
        buttons = [gr.Button(value=("✓ " if key == view else "") + translate(f"view_{key}", language)) for key in MAP_VIEWS]
        return [view, text, gr.Plot(value=first_chart, label=translate(chart_names[0], language)),
                gr.Plot(value=second_chart, label=translate(chart_names[1], language))] + buttons

    # One small function per view button
    def difference_view(choice, subject):
        return map_view(choice, subject, "difference")

    def change_view(choice, subject):
        return map_view(choice, subject, "change")

    def trends_view(choice, subject):
        return map_view(choice, subject, "trends")

    # The green button: check the portal for new files, then refresh the "Exam and school year" list.
    # It's a generator, so the page can say "Checking..." while it works
    def check_for_new_results(current_choice):
        yield translate("checking", language), gr.update()
        try:
            new_files = update_database()
        except Exception as error:
            yield (translate("check_failed", language, error=f"{type(error).__name__}: {error}") + "  \n"
                   + database_status(language)), gr.update()
            return
        # Refill the shared dictionary of files, so every part of the page (in every language) sees the new ones
        files = stored_files()
        exam_files.clear()
        exam_files.update(files)
        if new_files:
            found = translate("files_added", language, count=len(new_files),
                              files=", ".join(choice_label(choice, language) for choice in new_files))
        else:
            found = translate("no_new_files", language)
        yield f"{found}  \n{database_status(language)}", gr.Dropdown(choices=choice_list(exam_files, language), value=current_choice)

    # The title, with the 4 language buttons to its right
    with gr.Row(equal_height=True):
        gr.Markdown("# " + translate("page_title", language))
        # A narrow column on the right, just wide enough for the 4 buttons
        with gr.Column(scale=0, min_width=260):
            gr.HTML(language_buttons(language))
    gr.Markdown(translate("intro", language))
    with gr.Row(equal_height=True):
        database_info = gr.Markdown(database_status(language))
        check_button = gr.Button(translate("check_button", language), elem_id="check-button", scale=0, min_width=270)
    with gr.Row():
        # The lists show translated labels, but give the code English values: (label, value) pairs
        exam = gr.Dropdown(choice_list(exam_files, language), label=translate("exam_label", language), value=default)
        region = gr.Dropdown([(translate("all_regions", language), ALL_REGIONS)] + regions,
                             label=translate("region_label", language), value=ALL_REGIONS)
        town = gr.Dropdown(town_choices(exam_files, default, ALL_REGIONS, language),
                           label=translate("town_label", language), value=ALL_TOWNS)
    with gr.Row():
        search = gr.Textbox(label=translate("search_label", language), placeholder=translate("search_placeholder", language))
        rank_by = gr.Radio([(subject_name(value, language), value) for value in RANK_BY],
                           label=translate("rank_label", language), value=RANK_BY[0])
    with gr.Row():
        show_button = gr.Button(translate("show_button", language), elem_classes="grey-button")
        overview_button = gr.Button(translate("overview_button", language, top=TOP, model=MODEL), elem_classes="grey-button")

    # Which view the map tab shows: "difference", "change" or "trends". It's not drawn on the page:
    # gr.State only remembers a value for each visitor
    map_view_state = gr.State("difference")
    with gr.Tabs(elem_id="main-tabs") as tabs:
        with gr.Tab(translate("tab_schools", language), id="schools"):
            summary = gr.Markdown()
            results = gr.Dataframe(label=translate("schools_table", language))
        with gr.Tab(translate("tab_top", language, top=TOP), id="top"):
            gr.Markdown(translate("top_intro", language, min_town=MIN_TOWN_STUDENTS, min_town_region=MIN_TOWN_STUDENTS_IN_REGION,
                                  min_school=MIN_SCHOOL_STUDENTS, model=MODEL))
            top_towns = gr.Dataframe(label=translate("top_towns_table", language, top=TOP))
            top_schools = gr.Dataframe(label=translate("top_schools_table", language, top=TOP))
            overview_text = gr.Markdown()
        with gr.Tab(translate("tab_map", language), id="map") as map_tab:
            gr.Markdown(translate("map_intro", language))
            with gr.Row():
                difference_button = gr.Button("✓ " + translate("view_difference", language), elem_classes="grey-button")
                change_button = gr.Button(translate("view_change", language), elem_classes="grey-button")
                trends_button = gr.Button(translate("view_trends", language), elem_classes="grey-button")
            map_subject = gr.Radio([(subject_name(value, language), value) for value in MAP_SUBJECTS],
                                   label=translate("colour_by", language), value=MAP_SUBJECTS[0])
            map_summary = gr.Markdown()
            with gr.Row():
                map_plot = gr.Plot(label=translate("chart_map", language), scale=3)
                bars_plot = gr.Plot(label=translate("chart_bars", language), scale=2)
            gr.Markdown(f"*{translate('map_note', language)}*  \n{translate('borders_credit', language)}")

    filters = [exam, region, town, search, rank_by]
    shown = [summary, results]

    def show_schools_tab():
        return gr.Tabs(selected="schools")

    # A new exam or region changes which towns are in the list, then shows the new results
    exam.change(refresh_towns, [exam, region, town], town, api_name=False).then(
        show, filters, shown, api_name=False)
    region.change(refresh_towns, [exam, region, town], town, api_name=False).then(
        show, filters, shown, api_name=False)
    # Picking a town or a ranking also shows the new results straight away.
    # .input (instead of .change) reacts only to you, not to refresh_towns resetting the town,
    # which would show the results twice
    town.input(show, filters, shown, api_name=False)
    rank_by.input(show, filters, shown, api_name=False)
    # The button and Enter in the search box first switch to the Schools tab, then show the results
    show_button.click(show_schools_tab, None, tabs, api_name=False).then(
        show, filters, shown, api_name=api("show"))
    search.submit(show_schools_tab, None, tabs, api_name=False).then(
        show, filters, shown, api_name=False)
    overview_button.click(lambda: gr.Tabs(selected="top"), None, tabs, api_name=False).then(
        overview, [exam, region], [top_towns, top_schools, overview_text], api_name=api("overview"))
    # Show the default results as soon as the page opens
    page.load(show, filters, shown, api_name=False)
    # The map is drawn when you open its tab (a chart drawn in a hidden tab can get the
    # wrong size), and again when you change the exam, what it's coloured by, or the view
    map_shown = [map_view_state, map_summary, map_plot, bars_plot, difference_button, change_button, trends_button]
    map_tab.select(map_view, [exam, map_subject, map_view_state], map_shown, api_name=False)
    exam.change(map_view, [exam, map_subject, map_view_state], map_shown, api_name=False)
    map_subject.input(map_view, [exam, map_subject, map_view_state], map_shown, api_name=api("map"))
    difference_button.click(difference_view, [exam, map_subject], map_shown, api_name=api("map_difference"))
    change_button.click(change_view, [exam, map_subject], map_shown, api_name=api("map_change"))
    trends_button.click(trends_view, [exam, map_subject], map_shown, api_name=api("map_trends"))
    # The green button updates the database line and the list of exams and years
    check_button.click(check_for_new_results, [exam], [database_info, exam], api_name=api("check"))


def build_app(exam_files, regions):
    """
    Build the whole app: the Bulgarian page at the plain address, and the English, Russian and
    Romanian pages at /en, /ru and /ro. Gradio calls each extra page a "route"
    """
    # The page's colours and sizes, in CSS:
    # - "Check for new results" is green: white text on #1a7f37 has a contrast of 5.1:1, so it's
    #   easy to read; the darker #116329 shows when the mouse is over it
    # - the other buttons are light grey: dark text on #e9e9e7 has a contrast of 13.6:1
    # - the language buttons are blue: white text on #0b5cad has a contrast of 6.7:1; the current
    #   language is darker (#073d73, 10.9:1) and underlined, so it doesn't rely on colour alone
    # The three tabs' names are centred, bold and two text sizes bigger than normal (--text-xl
    # instead of --text-md), so the tabs are easy to find. In a narrow window they wrap onto a
    # second line ("flex-wrap"), because centred tabs that don't fit would be cut off on both sides
    page_style = (
        "#check-button { background: #1a7f37 !important; color: #ffffff !important; border-color: #1a7f37 !important; }"
        "#check-button:hover { background: #116329 !important; border-color: #116329 !important; }"
        ".grey-button { background: #e9e9e7 !important; color: #1f1f1f !important; border: 1px solid #8f8f8b !important; }"
        ".grey-button:hover { background: #dcdcd9 !important; }"
        "#main-tabs .tab-wrapper, #main-tabs .tab-container { justify-content: center; height: auto; }"
        "#main-tabs .tab-container { flex-wrap: wrap; }"
        "#main-tabs .tab-container button[role='tab'] { font-size: var(--text-xl); font-weight: 700; }"
        ".language-buttons { display: flex; gap: 8px; justify-content: flex-end; align-items: center; height: 100%; }"
        ".language-buttons a { background: #0b5cad !important; color: #ffffff !important; text-decoration: none !important;"
        " font-weight: 700; padding: 6px 14px; border-radius: 6px; }"
        ".language-buttons a:hover { background: #094a8c !important; }"
        ".language-buttons a.current { background: #073d73 !important; text-decoration: underline !important;"
        " text-underline-offset: 4px; }"
        # Gradio adds its own menu of the pages at the very top; the language buttons do its job
        ".nav-holder { display: none !important; }"
    )

    with gr.Blocks(title=translate("page_title", FIRST_LANGUAGE), css=page_style) as app:
        build_language_page(app, exam_files, regions, FIRST_LANGUAGE)
    for language, label in LANGUAGES.items():
        if language == FIRST_LANGUAGE:
            continue
        with app.route(label, f"/{language}"):
            build_language_page(app, exam_files, regions, language)
    return app


def main():
    # Lets the Windows terminal print Cyrillic, like "Министерство"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Every text must exist in all 4 languages: stop with a clear message if one is missing
    missing = missing_translations()
    if missing:
        print(f"translations.py is missing these texts: {', '.join(missing)}")
        sys.exit(1)

    try:
        exam_files = stored_files()
        if not exam_files:
            # The first time, without a database: fill it from the government's websites, once
            print(f"{DATABASE_FILE.name} is empty: downloading every results file once (about a minute)...")
            update_database()
            exam_files = stored_files()
        if not exam_files:
            print("The open data portal has no exam result files that this script recognises")
            sys.exit(1)
        # The 28 regions are the same in every file: take them from the first one.
        # Schools abroad are missing from some years, so make sure they're in the list
        first_choice, (first_kind, _) = next(iter(exam_files.items()))
        regions = sorted(set(read_results(first_choice, first_kind)["Region"]) | {ABROAD})
        page = build_app(exam_files, regions)
    except Exception as error:
        # Anything else, like the portal changing the layout of its data:
        # a clear message instead of a long Python error
        print(f"Couldn't get the data: {type(error).__name__}: {error}")
        sys.exit(1)

    print(f"{len(exam_files)} results files in {DATABASE_FILE.name}, for example: {', '.join(list(exam_files)[:3])}")
    # If the ministry renames or moves a dataset, that exam disappears from the list: say so
    found_exams = {choice.rsplit(" - ", 1)[0] for choice in exam_files}
    missing = [exam for exam in EXAMS if exam not in found_exams]
    if missing:
        print(f"Note: no results found for {', '.join(missing)} - the ministry may have renamed or moved them")
    # The AI overview needs Ollama, but the rest of the page doesn't: just warn (in English, in the terminal)
    problem = ollama_problem("en")
    if problem:
        print(f"Note: {problem}")
    page.launch(inbrowser=True)


if __name__ == "__main__":
    main()
