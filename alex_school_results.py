"""
Bulgarian school exam results: a web page that shows the official exam results of every
school in Bulgaria, published by the Ministry of Education and Science (МОН, mon.bg).

How it gets the data:
1. It reads mon.bg's open data page with BeautifulSoup and follows the ministry's link to
   the national open data portal (data.egov.bg). The results by school are published
   there as data files, not as pages on mon.bg.
2. It asks the portal's API for the ministry's exam result files: one file per school year.
3. When you pick an exam and a year, it downloads that file and shows it as a table.

The exams:
- NVO (НВО, national external assessment) in 4th, 7th and 10th grade:
  average score in points (maximum 100) in Bulgarian (BEL) and Maths (MAT)
- DZI (ДЗИ, state matriculation exams, "матури") in 12th grade, May-June session:
  average grade from 2 to 6 in Bulgarian (BEL) and in the second compulsory exam

On the page you can also pick a town, to see how it compares with its region and the
country, and ask a local Ollama model (gemma4) for an overview of the top 5 towns and
top 5 schools. The rankings are calculated by the code; the model only writes about them.

Before running:
- For the AI overview only: the Ollama app must be running, with the model downloaded:
  ollama pull gemma4. The rest of the page works without it.

Run it from the project folder with:
    uv run education_bulgaria/alex_school_results.py
The page opens in your browser (usually at http://127.0.0.1:7860). Press Ctrl+C to stop.
"""

import json
import re
import sys
from functools import cache

import gradio as gr
import ollama
import pandas as pd
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


# @cache remembers each file once it's downloaded, so going back to it is instant
@cache
def load_results(kind, resource_id):
    """
    Download one results file and return it as a table: one row per school
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


def load_choice(exam_files, choice):
    """
    Return the kind of exam ("nvo" or "dzi") and the results table for a dropdown choice,
    with a message on the page if it can't be loaded
    """
    if choice not in exam_files:
        raise gr.Error("Please choose an exam and a school year.")
    kind, resource_id = exam_files[choice]
    try:
        return kind, load_results(kind, resource_id)
    except (requests.exceptions.RequestException, RuntimeError, StopIteration) as error:
        raise gr.Error(f"Couldn't load the results from data.egov.bg: {error}")


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
        yield towns, schools, problem
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
        # Any failure (Ollama closed, a timeout...): say so on the page, below what was
        # written so far, instead of Gradio's generic "Error"
        yield towns, schools, f"{text}\n\n*The model stopped with an error: {type(error).__name__}: {error}*"


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

    with gr.Blocks(title="Bulgarian school exam results") as page:
        gr.Markdown(
            "# Bulgarian school exam results\n"
            "Official results by school from the Ministry of Education and Science (МОН), "
            "published on the national open data portal data.egov.bg. "
            "**NVO** (НВО) = national external assessment, average score in points (maximum 100). "
            "**DZI** (ДЗИ) = state matriculation exams (матури), May-June session, average grade from 2 to 6. "
            "**BEL** = Bulgarian language and literature, **MAT** = Maths."
        )
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
                    f"the text below them is written by {MODEL} on this computer."
                )
                top_towns = gr.Dataframe(label=f"Top {TOP} towns")
                top_schools = gr.Dataframe(label=f"Top {TOP} schools")
                overview_text = gr.Markdown()

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
    return page


def main():
    # Lets the Windows terminal print Cyrillic, like "Министерство"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"Reading {MON_OPEN_DATA_PAGE} ...")
    try:
        ministry_id = find_ministry_on_portal()
    except (requests.exceptions.RequestException, RuntimeError) as error:
        # mon.bg only tells us where the data is: if it's down, use the id we found there before
        print(f"Couldn't read mon.bg ({error}) - using the ministry's id found on 17 November 2026")
        ministry_id = KNOWN_MINISTRY_ID

    try:
        print("Asking data.egov.bg for the ministry's exam results...")
        exam_files = list_exam_files(find_exam_datasets(ministry_id))
        if not exam_files:
            print("The open data portal has no exam result files that this script recognises")
            sys.exit(1)
        # The 28 regions are the same in every file: take them from the first one.
        # Schools abroad are missing from some years, so make sure they're in the list
        first_kind, first_file = next(iter(exam_files.values()))
        regions = sorted(set(load_results(first_kind, first_file)["Region"]) | {ABROAD})
        page = build_page(exam_files, regions)
    except Exception as error:
        # Anything else, like the portal changing the layout of its data:
        # a clear message instead of a long Python error
        print(f"Couldn't get the data from data.egov.bg: {type(error).__name__}: {error}")
        sys.exit(1)

    print(f"Found {len(exam_files)} results files, for example: {', '.join(list(exam_files)[:3])}")
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
