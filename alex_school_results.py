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

The "Map of the regions" tab colours Bulgaria's 28 regions by how far their results are
from the national average, from dark red (far below) to light green (far above).

Before running:
- bulgaria_regions.geojson (the region borders for the map) must be next to this script.
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

ALL_REGIONS = "All regions"
ALL_TOWNS = "All towns"
# Bulgarian schools in other countries are listed under this "region"
ABROAD = "ЧУЖБИНА"
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

# What the map can be coloured by
MAP_SUBJECTS = ["Both subjects", "Bulgarian (BEL)", "Maths / 2nd exam"]

# The map's colours, from far below the national average to far above it:
# dark red -> red -> yellow (about average) -> light green.
# They also get steadily lighter, so darker always means lower results, even in black and
# white or for colour-blind readers (checked with simulated colour blindness)
MAP_COLOURS = [[0.0, "#7a1416"], [0.25, "#c8432c"], [0.5, "#f0b84a"], [0.75, "#d8e88c"], [1.0, "#c4f1bd"]]

# Shown under the map, so the colours aren't read as a verdict on the schools
MAP_NOTE = (
    "Colours show differences in exam results, not the quality of the schools: results also "
    "depend on family income, town or village, and which students sit the exam."
)

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

Format your answer in markdown:
## Top towns
One sentence introducing the list, then a numbered list with one short line per town:
its name, its "Both subjects" score, and its "Vs area average" text exactly as given.
## Top schools
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


def database_status():
    """
    A one-line description of the database, for the top of the page
    """
    database = open_database()
    try:
        files = database.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        last_check = database.execute("SELECT MAX(checked_at) FROM checks").fetchone()[0]
    finally:
        database.close()
    return (f"**Data:** {files} results files in the local database ({DATABASE_FILE.name}) · "
            f"last checked on data.egov.bg: {last_check or 'never'}")


def load_choice(exam_files, choice):
    """
    Return the kind of exam ("nvo" or "dzi") and the results table for a dropdown choice,
    from the database, with a message on the page if it can't be read
    """
    if choice not in exam_files:
        raise gr.Error("Please choose an exam and a school year.")
    kind, _ = exam_files[choice]
    try:
        return kind, read_results(choice, kind)
    except (sqlite3.Error, pd.errors.DatabaseError) as error:
        raise gr.Error(f"Couldn't read the results from the database: {error}")


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


def town_choices(exam_files, choice, region):
    """
    The towns for the dropdown: those with schools in the chosen exam and region.
    Cities ("ГР.") come before villages ("С.") because of the alphabetical order
    """
    _, table = load_choice(exam_files, choice)
    # An empty region box means the same as "All regions"
    if region and region != ALL_REGIONS:
        table = table[table["Region"] == region]
    towns = table[["Town", "Region"]].drop_duplicates()
    return [ALL_TOWNS] + sorted(town_label(row.Town, row.Region) for row in towns.itertuples())


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


def show_results(exam_files, choice, region, town, search, rank_by):
    """
    Filter and rank the schools, and write a summary above the table.
    When a town is chosen, the summary compares it with its region and the country
    """
    kind, everything = load_choice(exam_files, choice)
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]

    # Pick the schools to show, and the wider areas to compare them with
    table = everything
    compare_with = []
    if town and town != ALL_TOWNS:
        town_name, town_region = split_town_label(town)
        region_table = everything[everything["Region"] == town_region]
        table = region_table[region_table["Town"] == town_name]
        compare_with = [(f"{town_region} region", region_table), ("Bulgaria", everything)]
        area = town
    elif region and region != ALL_REGIONS:
        table = everything[everything["Region"] == region]
        compare_with = [("Bulgaria", everything)]
        area = region
    else:
        area = ALL_REGIONS

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

    scale = "points (maximum 100)" if kind == "nvo" else "grade (2 to 6)"
    schools = "school" if len(table) == 1 else "schools"
    summary = [f"**{choice}** · {area} · **{len(table)} {schools}**"]
    for count_column, average_column in [(bel_students, bel_average), (second_students, second_average)]:
        average, students = weighted_average(table, count_column, average_column)
        if average is None:
            continue
        # "BEL points" -> "BEL", "2nd exam grade" -> "2nd exam"
        subject = average_column.rsplit(" ", 1)[0]
        line = f"- {subject}: average **{average:.2f}** {scale}, {students:,} students"
        for name, other in compare_with:
            other_average, _ = weighted_average(other, count_column, average_column)
            if other_average is not None:
                line += f" · {name}: {other_average:.2f}"
        summary.append(line)

    if town and town != ALL_TOWNS:
        ranks = []
        for ranked, where, minimum in [
            (rank_towns(everything, kind, MIN_TOWN_STUDENTS), "towns in Bulgaria", MIN_TOWN_STUDENTS),
            (rank_towns(region_table, kind, MIN_TOWN_STUDENTS_IN_REGION), f"in {town_region} region", MIN_TOWN_STUDENTS_IN_REGION)
        ]:
            here = ranked[(ranked["Town"] == town_name) & (ranked["Region"] == town_region)]
            if not here.empty:
                ranks.append(f"**#{here['#'].iloc[0]} of {len(ranked)}** {where} (towns with {minimum}+ students)")
        if ranks:
            summary.append("- Town rank (average of both subjects): " + " · ".join(ranks))
        else:
            summary.append(f"- Town rank: not ranked, fewer than {MIN_TOWN_STUDENTS_IN_REGION} students took each exam")
    if table.empty:
        summary.append("\nNo schools match your search.")
    return "\n".join(summary), table


def ollama_problem():
    """
    Return None if Ollama is running and the model is downloaded,
    otherwise a message that says what's wrong
    """
    try:
        models = requests.get("http://localhost:11434/api/tags", timeout=5).json()["models"]
    except requests.exceptions.RequestException:
        return "Ollama isn't running: start the Ollama app to get the AI overview."
    # Ollama treats a model name without a tag as ":latest"
    wanted = MODEL if ":" in MODEL else MODEL + ":latest"
    if wanted not in [model["name"] for model in models]:
        return f"{MODEL} isn't downloaded: run `ollama pull {MODEL}` in a terminal."
    return None


def overview_messages(choice, kind, area, area_averages, towns, schools, min_town_students):
    """
    Build the list of messages for the model: our instructions, then the facts in JSON
    """
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
        {"role": "system", "content": overview_system_prompt},
        {"role": "user", "content": request}
    ]


def template_overview(area, towns, schools):
    """
    The overview written by the program itself, from the same numbers the AI gets.
    Used when the AI isn't available: plainer than the AI's text, but instant and always exact
    """
    lines = ["## Top towns"]
    if towns.empty:
        lines.append(f"No town in {area} has enough students to be ranked.")
    else:
        lines.append(f"The best towns in {area}, ranked by the average of both subjects:")
        for town in towns.to_dict(orient="records"):
            lines.append(f"{town['#']}. **{town['Town']}**: {town['Both subjects']:.2f}, "
                         f"{town['Vs area average']} the area's average")

    lines += ["", "## Top schools"]
    if schools.empty:
        lines.append(f"No school in {area} has enough students to be ranked.")
    else:
        lines.append(f"The best schools in {area}, ranked by the average of both subjects:")
        for school in schools.to_dict(orient="records"):
            lines.append(f"{school['#']}. **{school['School']}** ({school['Town']}): {school['Both subjects']:.2f}, "
                         f"{school['Vs area average']} the area's average")
        # What the list has in common: the town where most of the top schools are
        towns_count = schools["Town"].value_counts()
        if towns_count.iloc[0] == len(schools) and len(schools) > 1:
            lines.append(f"\nAll of the top schools are in {towns_count.index[0]}.")
        elif towns_count.iloc[0] > len(schools) / 2:
            lines.append(f"\nMost of the top schools are in {towns_count.index[0]}.")
    return "\n".join(lines)


def write_overview(exam_files, choice, region):
    """
    Rank the top towns and schools for the chosen exam and region and show them
    straight away, then stream the model's overview of them as it is written.
    Each step yields the two tables and the text so far
    """
    # An empty region box means the same as "All regions", as on the Schools tab
    region = region or ALL_REGIONS
    kind, table = load_choice(exam_files, choice)
    bel_students, bel_average, second_students, second_average = RESULT_COLUMNS[kind]
    if region != ALL_REGIONS:
        table = table[table["Region"] == region]
    area = "Bulgaria (all regions)" if region == ALL_REGIONS else f"{region} region"
    min_town_students = MIN_TOWN_STUDENTS if region == ALL_REGIONS else MIN_TOWN_STUDENTS_IN_REGION

    towns = rank_towns(table, kind, min_town_students).head(TOP).copy()
    schools = rank_schools(table, kind).head(TOP).copy()
    if towns.empty and schools.empty:
        yield towns, schools, f"Not enough data to rank: no town or school in {area} is big enough."
        return

    # How far each town and school is from the area's average. The code calculates this,
    # because language models often get subtractions wrong (we saw gemma4 write 13.04 for 14.04)
    bel, _ = weighted_average(table, bel_students, bel_average)
    second, _ = weighted_average(table, second_students, second_average)
    area_both = (bel + second) / 2
    area_averages = f"{bel_average} {bel:.2f}, {second_average} {second:.2f}, both subjects {area_both:.2f}"
    for ranked in (towns, schools):
        ranked["Vs area average"] = [
            f"{abs(score - area_both):.2f} {'above' if score >= area_both else 'below'}"
            for score in ranked["Both subjects"]
        ]

    problem = ollama_problem()
    if problem:
        # No AI: the program writes the overview itself, from the same numbers
        yield towns, schools, f"{template_overview(area, towns, schools)}\n\n*Written by the program, without AI. {problem}*"
        return
    yield towns, schools, f"*{MODEL} is writing the overview - this takes 1 to 3 minutes on this computer...*"

    text = ""
    try:
        stream = ollama.chat(
            model = MODEL,
            messages = overview_messages(choice, kind, area, area_averages, towns, schools, min_town_students),
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
            yield towns, schools, text
    except Exception as error:
        # Any failure (Ollama closed, a timeout...): the program writes the overview instead,
        # and says why, rather than leaving half a text or Gradio's generic "Error"
        yield towns, schools, (f"{template_overview(area, towns, schools)}\n\n*Written by the program, because the AI "
                               f"stopped with an error: {type(error).__name__}: {error}*")


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


# @cache: the map file is read once, the first time the map is shown
@cache
def load_region_map():
    """
    Read the borders of Bulgaria's 28 regions from the map file next to this script
    """
    with open(REGION_MAP_FILE, encoding="utf-8") as file:
        return json.load(file)


def region_map(regions, borders, unit, limit):
    """
    The map: each region coloured by how far its average is from the national average
    """
    english = {feature["properties"]["region"]: feature["properties"]["name_en"] for feature in borders["features"]}
    # The colour key's labels, like "-13", "-7", "0 = average", "+7", "+13"
    ticks = [-limit, -limit / 2, 0, limit / 2, limit]
    decimals = 0 if unit == "points" else 1
    tick_labels = [f"{tick:+.{decimals}f}" if tick else "0 = average" for tick in ticks]
    figure = go.Figure(go.Choropleth(
        geojson = borders,
        # Match the map's regions to the data by their Bulgarian names, like "СОФИЯ-ГРАД"
        featureidkey = "properties.region",
        locations = regions["Region"],
        z = regions["Vs Bulgaria"],
        # The same distance both ways, so the national average is always the middle colour (yellow)
        zmin = -limit,
        zmax = limit,
        colorscale = MAP_COLOURS,
        marker_line_color = "#6b6b6b",
        marker_line_width = 0.6,
        colorbar = dict(title=f"vs Bulgaria<br>({unit})", tickvals=ticks, ticktext=tick_labels, len=0.8, thickness=14),
        customdata = list(zip([english.get(region, "") for region in regions["Region"]], regions["Score"], regions["Schools"])),
        hovertemplate = ("<b>%{location}</b> (%{customdata[0]})<br>Average: %{customdata[1]:.2f}"
                         "<br>vs Bulgaria: %{z:+.2f}<br>Schools: %{customdata[2]}<extra></extra>")
    ))
    # Show only Bulgaria's regions, without the world map around them
    figure.update_geos(fitbounds="locations", visible=False, bgcolor="#fcfcfb")
    figure.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#fcfcfb")
    return figure


def region_bars(regions, unit, limit):
    """
    The same regions as a bar chart: best at the top, worst at the bottom, with each
    region's exact difference written next to its bar, so it can be read without colours
    """
    figure = go.Figure(go.Bar(
        x = regions["Vs Bulgaria"],
        y = regions["Region"],
        orientation = "h",
        marker = dict(color=regions["Vs Bulgaria"], colorscale=MAP_COLOURS, cmin=-limit, cmax=limit,
                      line=dict(color="#6b6b6b", width=0.6)),
        text = [f"{difference:+.2f}" for difference in regions["Vs Bulgaria"]],
        textposition = "outside",
        cliponaxis = False,
        customdata = regions["Score"],
        hovertemplate = "<b>%{y}</b><br>Average: %{customdata:.2f}<br>vs Bulgaria: %{x:+.2f}<extra></extra>"
    ))
    figure.update_layout(
        height = 660,
        # Room at the top, so the chart's label doesn't cover the first region's name
        margin = dict(l=10, r=10, t=40, b=40),
        paper_bgcolor = "#fcfcfb",
        plot_bgcolor = "#fcfcfb",
        # Zero (the national average) in the middle, with room for the numbers on both sides
        xaxis = dict(title=f"Difference from the Bulgarian average ({unit})", range=[-limit * 1.6, limit * 1.6],
                     zeroline=True, zerolinecolor="#444444", gridcolor="#e6e6e3"),
        yaxis = dict(automargin=True),
        bargap = 0.25,
        barcornerradius = 4
    )
    return figure


def show_map(exam_files, choice, subject):
    """
    The map tab: a summary of the biggest gaps, then the map and the bar chart of the
    28 regions, coloured by how far each region is from the national average
    """
    kind, table = load_choice(exam_files, choice)
    table = schools_in_bulgaria(table)
    subject = subject or MAP_SUBJECTS[0]
    unit = "points" if kind == "nvo" else "grade"
    try:
        borders = load_region_map()
    except OSError:
        return f"The map file {REGION_MAP_FILE.name} is missing: it must be next to this script.", None, None

    national = subject_score(table, kind, subject)
    regions = pd.DataFrame(
        [{"Region": region, "Schools": len(schools), "Score": subject_score(schools, kind, subject)}
         for region, schools in table.groupby("Region")],
        columns = ["Region", "Schools", "Score"]
    ).dropna(subset=["Score"])
    if national is None or regions.empty:
        return f"No results for {subject} in {choice}.", None, None
    regions["Vs Bulgaria"] = regions["Score"] - national
    regions = regions.sort_values("Vs Bulgaria")
    # The biggest distance from the average, in either direction, sets the ends of the colour scale
    limit = max(regions["Vs Bulgaria"].abs().max(), 0.01)

    worst, best = regions.iloc[0], regions.iloc[-1]
    cities = subject_score(table[table["Town"].str.startswith("ГР.")], kind, subject)
    villages = subject_score(table[table["Town"].str.startswith("С.")], kind, subject)
    summary = [
        f"**{choice}** · {subject} · Bulgaria: average **{national:.2f}** {unit}",
        f"- Best region: **{best['Region']}** {best['Score']:.2f} ({best['Vs Bulgaria']:+.2f}) · "
        f"worst region: **{worst['Region']}** {worst['Score']:.2f} ({worst['Vs Bulgaria']:+.2f}) · "
        f"gap: **{best['Score'] - worst['Score']:.2f}** {unit}"
    ]
    if cities is not None and villages is not None:
        summary.append(f"- Cities (ГР.): {cities:.2f} · villages (С.): {villages:.2f} · gap: **{cities - villages:.2f}** {unit}")
    return "\n".join(summary), region_map(regions, borders, unit, limit), region_bars(regions, unit, limit)


def build_page(exam_files, regions):
    """
    Build the Gradio web page. gr.Blocks (instead of gr.Interface) lets the town list
    change when you pick a region, and gives the AI overview its own button
    """
    choices = list(exam_files)
    # Start with the newest 7th grade results: the ones parents look at the most
    default = next((choice for choice in choices if choice.startswith("NVO 7th grade")), choices[0])

    def show(choice, region, town, search, rank_by):
        return show_results(exam_files, choice, region, town, search, rank_by)

    # Gradio streams the overview only when it gets a generator function
    def overview(choice, region):
        yield from write_overview(exam_files, choice, region)

    def refresh_towns(choice, region, current_town):
        towns = town_choices(exam_files, choice, region)
        # Keep the chosen town if it's still in the list
        return gr.Dropdown(choices=towns, value=current_town if current_town in towns else ALL_TOWNS)

    def map_view(choice, subject):
        return show_map(exam_files, choice, subject)

    # The green button: check the portal for new files, then refresh the "Exam and school year" list.
    # It's a generator, so the page can say "Checking..." while it works
    def check_for_new_results(current_choice):
        yield "*Checking data.egov.bg for new results files: this takes about 20 seconds...*", gr.update()
        try:
            new_files = update_database()
        except Exception as error:
            yield f"Couldn't check for new results: {type(error).__name__}: {error}  \n{database_status()}", gr.update()
            return
        # Refill the shared dictionary of files, so every part of the page sees the new ones
        files = stored_files()
        exam_files.clear()
        exam_files.update(files)
        if new_files:
            found = f"Added {len(new_files)} new results files: {', '.join(new_files)}."
        else:
            found = "No new results: the database is up to date."
        yield f"{found}  \n{database_status()}", gr.Dropdown(choices=list(exam_files), value=current_choice)

    # Colour the "Check for new results" button green. White text on #1a7f37 has a contrast
    # of 5.1:1, so it's easy to read; the darker #116329 shows when the mouse is over it
    green_button = (
        "#check-button { background: #1a7f37 !important; color: #ffffff !important; border-color: #1a7f37 !important; }"
        "#check-button:hover { background: #116329 !important; border-color: #116329 !important; }"
    )

    with gr.Blocks(title="Bulgarian school exam results", css=green_button) as page:
        gr.Markdown(
            "# Bulgarian school exam results\n"
            "Official results by school from the Ministry of Education and Science (МОН), "
            "published on the national open data portal data.egov.bg. "
            "**NVO** (НВО) = national external assessment, average score in points (maximum 100). "
            "**DZI** (ДЗИ) = state matriculation exams (матури), May-June session, average grade from 2 to 6. "
            "**BEL** = Bulgarian language and literature, **MAT** = Maths."
        )
        with gr.Row(equal_height=True):
            database_info = gr.Markdown(database_status())
            check_button = gr.Button("Check for new results", elem_id="check-button", scale=0, min_width=220)
        with gr.Row():
            exam = gr.Dropdown(choices, label="Exam and school year", value=default)
            region = gr.Dropdown([ALL_REGIONS] + regions, label="Region (област)", value=ALL_REGIONS)
            town = gr.Dropdown(town_choices(exam_files, default, ALL_REGIONS), label="Town (град / село) - type to search", value=ALL_TOWNS)
        with gr.Row():
            search = gr.Textbox(label="School, town or municipality contains", placeholder="for example: Математическа")
            rank_by = gr.Radio(RANK_BY, label="Rank schools by", value=RANK_BY[0])
        with gr.Row():
            show_button = gr.Button("Show results", variant="primary")
            overview_button = gr.Button(f"Write AI overview of the top {TOP} ({MODEL})")

        with gr.Tabs() as tabs:
            with gr.Tab("Schools", id="schools"):
                summary = gr.Markdown()
                results = gr.Dataframe(label="Schools")
            with gr.Tab(f"Top {TOP} towns and schools + AI overview", id="top"):
                gr.Markdown(
                    f"For the chosen exam and region, ranked by the **average of both subjects**. "
                    f"Towns need at least {MIN_TOWN_STUDENTS} students in each exam ({MIN_TOWN_STUDENTS_IN_REGION} "
                    f"inside one region), and schools at least {MIN_SCHOOL_STUDENTS}. The tables come from the data; "
                    f"the text below them is written by {MODEL} on this computer, or by the program itself "
                    f"when the AI isn't available."
                )
                top_towns = gr.Dataframe(label=f"Top {TOP} towns")
                top_schools = gr.Dataframe(label=f"Top {TOP} schools")
                overview_text = gr.Markdown()
            with gr.Tab("Map of the regions", id="map") as map_tab:
                gr.Markdown(
                    "The 28 regions for the chosen exam and year, coloured by how far each one is from the "
                    "Bulgarian average: **dark red** = far below, **yellow** = about average, **light green** = "
                    "far above. Darker always means lower. The map always shows the whole country."
                )
                map_subject = gr.Radio(MAP_SUBJECTS, label="Colour by", value=MAP_SUBJECTS[0])
                map_summary = gr.Markdown()
                with gr.Row():
                    map_plot = gr.Plot(label="Map", scale=3)
                    bars_plot = gr.Plot(label="All regions, best at the top", scale=2)
                gr.Markdown(f"*{MAP_NOTE}*  \nRegion borders: Natural Earth (public domain).")

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
            show, filters, shown, api_name="show")
        search.submit(show_schools_tab, None, tabs, api_name=False).then(
            show, filters, shown, api_name=False)
        overview_button.click(lambda: gr.Tabs(selected="top"), None, tabs, api_name=False).then(
            overview, [exam, region], [top_towns, top_schools, overview_text], api_name="overview")
        # Show the default results as soon as the page opens
        page.load(show, filters, shown, api_name=False)
        # The map is drawn when you open its tab (a chart drawn in a hidden tab can get the
        # wrong size), and again when you change the exam or what it's coloured by
        map_shown = [map_summary, map_plot, bars_plot]
        map_tab.select(map_view, [exam, map_subject], map_shown, api_name=False)
        exam.change(map_view, [exam, map_subject], map_shown, api_name=False)
        map_subject.input(map_view, [exam, map_subject], map_shown, api_name="map")
        # The green button updates the database line and the list of exams and years
        check_button.click(check_for_new_results, [exam], [database_info, exam], api_name="check")
    return page


def main():
    # Lets the Windows terminal print Cyrillic, like "Министерство"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
        page = build_page(exam_files, regions)
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
    # The AI overview needs Ollama, but the rest of the page doesn't: just warn
    problem = ollama_problem()
    if problem:
        print(f"Note: {problem}")
    page.launch(inbrowser=True)


if __name__ == "__main__":
    main()
