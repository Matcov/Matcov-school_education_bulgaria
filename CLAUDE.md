# CLAUDE.md

A Gradio app that shows the official exam results of every Bulgarian school (НВО 4th, 7th, 10th
grade and ДЗИ), compares towns and regions, and maps the inequality between regions over the
years. A learning project: the owner is a Python beginner, so the code and docs are written to be
read by beginners.

## Running and testing

- Run from the course root `c:\projects\llm_engineering`: `uv run education_bulgaria/alex_school_results.py`.
  It opens http://127.0.0.1:7860 (Bulgarian). It needs `translations.py` and
  `bulgaria_regions.geojson` next to it.
- Python is the course's `.venv` (Python 3.12, managed by uv). The system Python has none of the
  libraries; in VS Code the interpreter must be `.venv\Scripts\python.exe`.
- The app reads only `school_results.db` (SQLite, 25 files, 35,292 rows). The government sites
  (mon.bg, data.egov.bg) are called only when the database is empty or on "Check for new results".
- Ollama with `gemma4` writes the AI overview; without it the program writes the overview itself.
- Test code changes by calling the app's own functions for every file in `stored_files()`, all three
  `MAP_SUBJECTS` and every view (`show_map`, `show_change`, `show_trends`). For layout changes, start
  the app on another port (7864) with `page.launch(server_port=..., prevent_thread_lock=True)` and
  screenshot it in a headless Edge through the DevTools protocol. Check a narrow window too.

## Rules of the project

- **The code calculates every number; the AI only words it.** gemma4 got subtractions wrong, so
  differences like "Vs area average" are computed and passed in.
- **Years are never compared on raw averages.** Regions are compared with that year's national
  average, and trends also divide the gap between regions by the spread of the schools' results
  (`school_spread()`), because some tests spread students further apart.
- **Averages are weighted by students** (`weighted_average()`), never averages of school averages.
- **The school code is the key,** not the name: names change between years.
- Colours: the map scale gets lighter as results get better, so it reads for colour-blind readers.
  Button colours have their contrast checked (white on green 5.1:1, dark on grey 13.6:1).
- Comments and docstrings: plain English, short sentences, explain *why*. Every function has a
  docstring.

## Four languages

- The page exists in Bulgarian (at `/`, the first language), English (`/en`), Russian (`/ru`) and
  Romanian (`/ro`): `build_app()` makes one Gradio app with `app.route()` per extra language, and
  `build_language_page()` builds each one. The blue EN BG RU RO buttons are plain links.
- **Every text the page shows comes from `translations.py`** through `translate(key, language, ...)`,
  never from a string in the main script. A new or changed text needs all 4 languages; `main()`
  refuses to start if one is missing. Terminal messages stay in English.
- **The code works only with English values.** Dropdowns and radios use (label, value) pairs, and
  `shown_table()` translates column names only for display. Never compare a translated string.
- Never translate data (school, town, region names). Decimals keep the dot in every language;
  `whole_number()` puts a space between thousands outside English.
- Avoid texts that need plural forms ("Schools: 1702", not "1702 schools").
- Test a change in all 4 languages: call the view functions with each language, check that no
  `{placeholder}` is left unfilled, and screenshot the longer languages (Bulgarian, Russian), which
  can overflow buttons, tabs and chart axes.

## Docs that must follow every code change

- `README.md` (GitHub front page), `info.md` (research notes and findings, with numbers).
- `Overviews/overview_{english,bulgarian,russian,romanian}.md`: the same overview in 4 languages.
- `Explanations/explanation_{english,bulgarian,russian,romanian}.md`: every function explained for
  beginners, with a mermaid diagram of the calls. English is the source; the others are translations
  with the same function headings, the same diagram arrows and the same structure.
- The explanations' function headings link to line numbers (also for `translations.py`):
  ``#### `name(args)`: [line N](../alex_school_results.py#LN)`` (`ред`, `строка`, `linia` in the
  other languages). After any code change, update every N from the `def` lines with a small script,
  and check that no function is undocumented.
- Numbers in prose: English uses dots; Bulgarian, Russian and Romanian use decimal commas. Text the
  app shows on screen keeps the dot in every language.

## Git and GitHub

- Work happens on branch `alex/education-bulgaria` of the course repo. Commit only when asked.
- `.png` files are ignored by the course's `.gitignore`: add screenshots with `git add -f`.
- Don't commit `school_results.db` when its only change is a new row in the `checks` log.
- The folder is published to the owner's public repo `Matcov/Matcov-school_education_bulgaria`
  (remote `mygithub`, branch `main`), with the folder's contents at the top. Push only when asked.
  `git subtree split` is far too slow on the course history. Instead, replay each new commit with
  `git commit-tree <commit>:education_bulgaria -p <previous>`, keeping its message, author and
  dates, on top of `mygithub/main`. First check that `mygithub/main^{tree}` equals the folder tree of
  the last published commit. Then push `education-bulgaria-only:main`, a normal fast-forward.
- Commits use the owner's GitHub noreply email; never put their work email in anything published.
