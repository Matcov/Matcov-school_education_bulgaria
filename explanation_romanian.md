# Cum funcționează `alex_school_results.py`, explicat simplu

Acest ghid este pentru cei care sunt **la început cu Python**. Explică pe înțelesul tuturor fiecare
funcție (`def`) din [alex_school_results.py](alex_school_results.py) și apoi arată cum lucrează
toate împreună.

Cum să-l citești:
1. Citește **„Ce face programul”** și **„Cuvinte pe care le vei întâlni”**.
2. Uită-te la **diagrama** din secțiunea 4.
3. Citește funcțiile. Fiecare are un link către linia ei din cod (numerele liniilor sunt cele de la
   25 noiembrie 2026).

---

## 1. Ce face programul

1. **Păstrează** rezultatele oficiale la examene ale fiecărei școli din Bulgaria într-o **bază de date
   locală**, fișierul `school_results.db`. Ministerul Educației din Bulgaria (МОН) publică rezultatele
   pe internet; programul le descarcă doar prima dată sau atunci când apeși butonul verde
   **Check for new results** („Caută rezultate noi”).
2. **Curăță** datele în timp ce le descarcă, pentru că sunt dezordonate: nume scrise în moduri
   diferite, numere cu virgulă și așa mai departe.
3. **Afișează** rezultatele pe o pagină web în browserul tău, făcută cu biblioteca Gradio.
4. Pe pagină **alegi** un examen, un an școlar, o regiune și o localitate. Programul face
   **clasamentul** școlilor și al localităților pentru tine.
5. Dacă vrei, un **AI local** (modelul gemma4, care rulează în Ollama pe calculatorul tău) scrie o
   scurtă prezentare a primelor 5 localități și școli. Dacă AI-ul nu este disponibil, programul scrie
   singur o prezentare mai simplă.
6. O **hartă a celor 28 de regiuni** colorează fiecare regiune după cât de departe sunt rezultatele
   ei de media națională, de la roșu închis (mult sub medie) la verde deschis (mult peste medie),
   alături de un grafic cu bare care arată numerele exacte.
7. Trei butoane din fila hărții comută între trei **vederi**: acea diferență față de media
   națională, **schimbarea față de anul precedent** și **tendințele de-a lungul anilor**.

**Examenele:**
- **НВО** (evaluarea națională externă) în clasele a 4-a, a 7-a și a 10-a: puncte de la 0 la 100 la
  limba bulgară (**BEL**) și la matematică (**MAT**).
- **ДЗИ** (bacalaureatul, „matura”) în clasa a 12-a: note de la 2 la 6 la limba bulgară și la un al
  doilea examen.

---

## 2. Cuvinte pe care le vei întâlni

| Cuvânt | Ce înseamnă |
|---|---|
| **funcție** (`def`) | O rețetă cu nume. Îi dai ingrediente (**parametri**), ea face niște pași și îți dă înapoi un rezultat (**`return`**). Exemplu: `def add(a, b): return a + b` → `add(2, 3)` dă `5`. |
| **a apela** o funcție | A o folosi: `tidy_town("ГР. СОФИЯ")`. „A apelează B” înseamnă că funcția A folosește funcția B. |
| **`None`** | Cuvântul din Python pentru „nimic, nicio valoare”. |
| **șir de caractere** (string) | Text, între ghilimele: `"Варна"`. |
| **listă** (list) `[ ]` | Mai multe valori, în ordine: `["Варна", "Бургас"]`. |
| **tuplu** (tuple) `( )` | Ca o listă, dar care nu se poate schimba: `("ГР.ВАРНА", "ВАРНА")`. O funcție poate întoarce două valori sub formă de tuplu. |
| **dicționar** (dictionary) `{ }` | Perechi *cheie → valoare*, ca o carte de telefon: `{"NVO 7th grade": "b56288b6-..."}`. |
| **tabel** (pandas `DataFrame`) | O foaie ca în Excel, dar în interiorul lui Python: rânduri și coloane. |
| **bază de date** (SQLite) | Un fișier care păstrează tabele și în care se poate căuta repede. SQLite este inclus în Python, iar toată baza de date este un singur fișier: aici, `school_results.db`. |
| **SQL** | Limbajul în care pui întrebări unei baze de date. `SELECT school FROM results WHERE town = 'ГР.ВАРНА'` înseamnă „dă-mi școlile din Varna”. |
| **tranzacție** | Mai multe modificări într-o bază de date care se fac **toate împreună sau deloc**. Dacă ceva eșuează la jumătate, nimic nu rămâne salvat pe jumătate. |
| **API** | Un site făcut pentru **programe**, nu pentru oameni: trimiți o întrebare și primești date înapoi. |
| **JSON** | Un format de text pentru date, care seamănă cu dicționarele și listele din Python. API-urile răspund în JSON. |
| **eroare** (excepție, exception) | Semnalul din Python că „ceva n-a mers bine”. `raise` trimite un astfel de semnal; `try:` … `except:` îl prinde, ca programul să poată reacționa. `finally:` se execută în orice caz, cu eroare sau fără. |
| **`_`** | Un nume pentru o valoare de care **nu avem nevoie**: `kind, table = …` față de `_, table = …`. |
| **decorator** (`@cache`) | O etichetă scrisă deasupra unei funcții, care îi dă o abilitate în plus. `@cache` îi dă memorie. |
| **generator** (`yield`) | O funcție care dă rezultatele **bucată cu bucată**, nu pe toate deodată cu `return`. Se folosește ca textul AI-ului să apară cuvânt cu cuvânt. |
| **funcție interioară** | O funcție scrisă în interiorul altei funcții. |
| **eveniment** (event) | Ceva ce se întâmplă pe pagina web (un clic, o alegere nouă). Atunci Gradio apelează o funcție. |
| **constantă** | O setare scrisă cu MAJUSCULE la începutul fișierului, de exemplu `TOP = 5`. Nu se schimbă cât timp rulează programul. |
| **stare** (`gr.State`) | O valoare pe care Gradio o **ține minte** pentru fiecare vizitator al paginii, fără s-o afișeze. Aici: care dintre cele trei vederi ale hărții ai ales. |
| **mediană** | Valoarea din mijloc: jumătate dintre numere sunt mai mici, jumătate sunt mai mari. Dacă numărul de valori este par, este media celor două din mijloc. Spre deosebire de media obișnuită, un singur număr extrem abia o mișcă. |

---

## 3. Setările de la începutul fișierului (liniile 57–199)

| Setare | Ce este |
|---|---|
| `MON_OPEN_DATA_PAGE` | Pagina web a ministerului care ne spune unde sunt datele |
| `PORTAL_API` | Adresa API-ului portalului național de date deschise (data.egov.bg) |
| `KNOWN_MINISTRY_ID` | ID-ul ministerului pe portal, folosit dacă mon.bg nu funcționează |
| `headers` | Le spune sincer site-urilor cine întreabă |
| `MODEL`, `THINK` | Modelul AI (`gemma4`) și „nu gândi cu voce tare”, ca să fie mai rapid |
| `EXAMS` | Cele 4 examene, cu tipul lor (`"nvo"` sau `"dzi"`) și numele setului lor de date pe portal |
| `RESULT_COLUMNS` | Numele celor 4 coloane cu rezultate pentru fiecare tip de examen |
| `ALL_REGIONS`, `ALL_TOWNS`, `ABROAD`, `RANK_BY` | Texte fixe folosite pe pagină |
| `TOP` | Câte localități și școli arată prezentarea AI (5) |
| `MIN_TOWN_STUDENTS`, `MIN_TOWN_STUDENTS_IN_REGION`, `MIN_SCHOOL_STUDENTS` | Numărul minim de elevi (100, 30, 10) pentru a intra în clasament, ca să nu câștige satele foarte mici |
| `BOM` | Un caracter invizibil cu care încep unele fișiere |
| `DATABASE_FILE` | Unde se află baza de date: fișierul `school_results.db` de lângă script |
| `DATABASE_TABLES` | Cele 3 tabele ale bazei de date, scrise în SQL: `files`, `results` și `checks`. Sunt create prima dată când se deschide fișierul |
| `DATABASE_COLUMNS` | Numele coloanelor cu rezultate din baza de date (`region`, `school`, `bel_average`…) |
| `REGION_MAP_FILE` | Unde sunt granițele regiunilor pentru hartă: fișierul `bulgaria_regions.geojson` de lângă script |
| `MAP_SUBJECTS` | După ce se poate colora harta: ambele materii, limba bulgară sau matematică / al 2-lea examen |
| `MAP_COLOURS` | Culorile hărții, de la roșu închis (mult sub medie) la verde deschis (mult peste medie). În plus, devin tot mai deschise, așa că mai închis înseamnă mereu mai slab |
| `MAP_VIEWS` | Cele trei vederi ale filei hărții și textul de pe butonul fiecăreia: `"difference"` → „Difference from Bulgaria” (diferența față de Bulgaria), `"change"` → „Change since the previous year” (schimbarea față de anul precedent), `"trends"` → „Trends over the years” (tendințele de-a lungul anilor) |
| `MAP_NOTE` | Rândul de sub hartă: culorile arată diferențe între rezultate, nu calitatea școlilor |
| `overview_system_prompt` | Regulile pe care AI-ul trebuie să le respecte când scrie prezentarea |

---

## 4. Imaginea de ansamblu: cum sunt legate funcțiile

Cum citești diagrama:
- O **săgeată** `A → B` înseamnă „A **apelează** B”.
- O **săgeată punctată** înseamnă „creează” sau „apoi Gradio rulează”.
- Un **cilindru** este ceva din afara codului: un site, un fișier sau AI-ul de pe calculatorul tău.

> Diagrama apare ca imagine **pe GitHub**. În VS Code, instalează extensia
> *„Markdown Preview Mermaid Support”* sau citește varianta text de sub diagramă.

```mermaid
flowchart TD
    START(["Pornești scriptul"]) --> n_main["main()"]

    subgraph g_helpers ["1 - Mici ajutoare"]
        n_tidy["tidy()"]
        n_tidy_town["tidy_town()"]
        n_to_number["to_number()"]
        n_weighted["weighted_average()"]
        n_town_label["town_label()"]
        n_split_label["split_town_label()"]
    end

    subgraph g_internet ["2 - Luarea datelor de pe internet"]
        n_find_ministry["find_ministry_on_portal()"]
        n_find_datasets["find_exam_datasets()"]
        n_list_files["list_exam_files()"]
        n_download["download_results()"]
        n_call_portal["call_portal()"]
    end

    subgraph g_db ["3 - Baza de date"]
        n_update["update_database()"]
        n_save["save_results()"]
        n_stored["stored_files()"]
        n_read["read_results()"]
        n_status["database_status()"]
        n_open["open_database()"]
        n_load_choice["load_choice()"]
    end

    subgraph g_rank ["4 - Alegere și clasament"]
        n_town_choices["town_choices()"]
        n_show_results["show_results()"]
        n_rank_towns["rank_towns()"]
        n_rank_schools["rank_schools()"]
    end

    subgraph g_ai ["5 - Prezentarea AI"]
        n_write_overview["write_overview()"]
        n_overview_messages["overview_messages()"]
        n_template["template_overview()"]
        n_ollama_problem["ollama_problem()"]
    end

    subgraph g_map ["6 - Harta și cele trei vederi ale ei"]
        n_show_map["show_map()"]
        n_show_change["show_change()"]
        n_show_trends["show_trends()"]
        n_exam_years["exam_years()"]
        n_region_gaps["region_gaps()"]
        n_schools_in_bulgaria["schools_in_bulgaria()"]
        n_subject_score["subject_score()"]
        n_school_spread["school_spread()"]
        n_drift_words["drift_words()"]
        n_load_region_map["load_region_map()<br/>cu memorie: @cache"]
        n_region_map["region_map()"]
        n_region_bars["region_bars()"]
        n_trend_heatmap["trend_heatmap()"]
        n_gap_trend_chart["gap_trend_chart()"]
        n_colour_key["colour_key()"]
        n_signed["signed()"]
        n_year_labels["year_labels()"]
    end

    subgraph g_page ["7 - Pagina web, făcută de build_page()"]
        n_build_page["build_page()"]
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

    MON[("mon.bg")]
    PORTAL[("data.egov.bg")]
    DBFILE[("school_results.db")]
    OLLAMA[("Ollama cu gemma4")]
    MAPFILE[("bulgaria_regions.geojson")]
    YOU(["Tu, în browser"])

    %% Pornirea programului
    n_main --> n_stored
    n_main -->|doar dacă baza de date e goală| n_update
    n_main --> n_read
    n_main --> n_build_page
    n_main --> n_ollama_problem

    %% Baza de date
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

    %% Luarea datelor de pe internet
    n_find_ministry --> MON
    n_find_datasets --> n_call_portal
    n_find_datasets --> n_tidy
    n_list_files --> n_call_portal
    n_download --> n_call_portal
    n_download --> n_to_number
    n_download --> n_tidy_town
    n_call_portal --> PORTAL

    %% Pagina web
    n_build_page --> n_town_choices
    n_build_page --> n_status
    n_build_page -.->|creează| n_show
    n_build_page -.->|creează| n_refresh
    n_build_page -.->|creează| n_tab
    n_build_page -.->|creează| n_overview
    n_build_page -.->|creează| n_map_view
    n_build_page -.->|creează| n_difference_view
    n_build_page -.->|creează| n_change_view
    n_build_page -.->|creează| n_trends_view
    n_build_page -.->|creează| n_check
    YOU -->|pagina se deschide, localitate nouă sau alt clasament| n_show
    YOU -->|examen sau regiune nouă| n_refresh
    YOU -->|Show results sau Enter| n_tab
    YOU -->|Write AI overview| n_overview
    YOU -->|fila Map, examen nou sau Colour by| n_map_view
    YOU -->|Difference from Bulgaria| n_difference_view
    YOU -->|Change since the previous year| n_change_view
    YOU -->|Trends over the years| n_trends_view
    YOU -->|Check for new results| n_check
    n_refresh -.->|apoi| n_show
    n_tab -.->|apoi| n_show
    n_check --> n_update
    n_check --> n_stored
    n_check --> n_status

    %% Alegere și clasament
    n_show --> n_show_results
    n_refresh --> n_town_choices
    n_town_choices --> n_load_choice
    n_town_choices --> n_town_label
    n_show_results --> n_load_choice
    n_show_results --> n_split_label
    n_show_results --> n_weighted
    n_show_results --> n_rank_towns
    n_rank_towns --> n_weighted

    %% Prezentarea AI
    n_overview --> n_write_overview
    n_write_overview --> n_load_choice
    n_write_overview --> n_rank_towns
    n_write_overview --> n_rank_schools
    n_write_overview --> n_weighted
    n_write_overview --> n_ollama_problem
    n_write_overview --> n_overview_messages
    n_write_overview -->|fără AI| n_template
    n_write_overview --> OLLAMA
    n_ollama_problem --> OLLAMA

    %% Harta și cele trei vederi ale ei
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
    n_show_change --> n_load_choice
    n_show_change --> n_exam_years
    n_show_change --> n_load_region_map
    n_show_change --> n_region_gaps
    n_show_change --> n_region_map
    n_show_change --> n_region_bars
    n_show_trends --> n_load_choice
    n_show_trends --> n_exam_years
    n_show_trends --> n_region_gaps
    n_show_trends --> n_trend_heatmap
    n_show_trends --> n_gap_trend_chart
    n_show_trends --> n_drift_words
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
    n_gap_trend_chart --> n_year_labels
    n_subject_score --> n_weighted
    n_load_region_map --> MAPFILE
```

### Același lucru ca text: cinci parcursuri

**Parcursul A: pornești programul** (`uv run education_bulgaria/alex_school_results.py`)

```text
main()
 ├─ stored_files() → open_database()          lista fișierelor din school_results.db
 ├─ update_database()                         DOAR dacă baza de date e goală: vezi Parcursul E
 ├─ read_results() → open_database()          primul fișier, doar ca să ia lista regiunilor
 ├─ build_page()                              construiește pagina web
 │    ├─ database_status() → open_database()  rândul „Data: 25 results files...”
 │    └─ town_choices()                       umple lista de localități (Town)
 │         ├─ load_choice() → read_results()
 │         └─ town_label()
 ├─ ollama_problem()                          e gata AI-ul? (doar un avertisment)
 └─ page.launch()                             deschide browserul
```

Aici nu e nevoie de internet: totul vine din baza de date.

**Parcursul B: fila „Schools”** (pagina se deschide, schimbi ceva sau apeși „Show results”)

```text
show_schools_tab()                 doar pentru „Show results” și Enter: mergi la fila Schools
refresh_towns()                    doar când se schimbă examenul sau regiunea: o listă nouă de localități
 └─ town_choices() → load_choice() → read_results(), town_label()
show()
 └─ show_results()                 rezumatul + tabelul
      ├─ load_choice() → read_results()     (cam 20 de milisecunde, din baza de date)
      ├─ split_town_label()                 (dacă e aleasă o localitate)
      ├─ weighted_average()                 (mediile din rezumat)
      └─ rank_towns() → weighted_average()  (locul localității în clasament, dacă e aleasă una)
```

**Parcursul C: apeși „Write AI overview”**

```text
(pagina trece la a doua filă)
overview()
 └─ write_overview()
      ├─ load_choice() → read_results()
      ├─ rank_towns() → weighted_average()   primele 5 localități
      ├─ rank_schools()                      primele 5 școli
      ├─ weighted_average()                  media zonei și „Vs area average”
      ├─ ollama_problem()                    e gata Ollama?
      ├─ template_overview()                 dacă nu, sau dacă AI-ul eșuează: o scrie programul
      ├─ overview_messages()                 instrucțiunile + faptele în JSON
      └─ ollama.chat()                       gemma4 scrie, cuvânt cu cuvânt
```

**Parcursul D: deschizi fila „Map and trends of the regions”** (sau apeși unul dintre cele trei butoane ale ei,
schimbi examenul sau schimbi „Colour by”)

Cele trei butoane apelează `difference_view()`, `change_view()` sau `trends_view()`. Fiecare dintre
ele apelează `map_view()` cu vederea sa. Deschiderea filei, un examen nou sau „Colour by” apelează
`map_view()` direct, cu vederea pe care ai ales-o ultima (la început, „Difference from Bulgaria”).

```text
map_view()
 ├─ show_map()                     „Difference from Bulgaria”: rezumatul diferențelor + harta + barele
 │    ├─ load_choice() → read_results()
 │    ├─ schools_in_bulgaria()                  lasă deoparte școlile din străinătate
 │    ├─ load_region_map()                      citește bulgaria_regions.geojson (doar prima dată)
 │    ├─ subject_score() → weighted_average()   Bulgaria, fiecare regiune, orașe, sate
 │    ├─ region_map() → colour_key()            harta colorată
 │    └─ region_bars() → colour_key(), signed() graficul cu bare, cea mai bună sus
 ├─ show_change()                  „Change since the previous year”
 │    ├─ load_choice() → read_results()
 │    ├─ exam_years()                           anii acestui examen, ca să-l găsească pe cel precedent
 │    ├─ load_region_map()
 │    ├─ region_gaps()                          cât de departe e fiecare regiune de media națională
 │    │    ├─ load_choice() → read_results()    (pentru ambii ani)
 │    │    ├─ schools_in_bulgaria()
 │    │    ├─ subject_score() → weighted_average()
 │    │    └─ school_spread()                   cât de împrăștiate sunt rezultatele școlilor
 │    ├─ region_map() → colour_key()            harta schimbărilor
 │    └─ region_bars() → colour_key(), signed() graficul cu bare, cea mai îmbunătățită sus
 └─ show_trends()                  „Trends over the years”
      ├─ load_choice() → read_results()
      ├─ exam_years()                           toți anii acestui examen
      ├─ region_gaps()                          ca mai sus, pentru fiecare an
      ├─ drift_words()                          „drifted apart”, „came closer” sau „about the same”
      ├─ trend_heatmap() → colour_key(), signed(), year_labels()   grila regiunilor și anilor
      └─ gap_trend_chart() → year_labels()      linia decalajului dintre cea mai bună și cea mai slabă regiune
```

**Parcursul E: apeși butonul verde „Check for new results”**

```text
check_for_new_results()
 ├─ update_database()
 │    ├─ find_ministry_on_portal()           citește mon.bg (dacă nu merge: KNOWN_MINISTRY_ID)
 │    ├─ find_exam_datasets()                găsește cele 4 seturi de date ale examenelor
 │    │    ├─ call_portal()                  întreabă data.egov.bg
 │    │    └─ tidy()
 │    ├─ list_exam_files()                   lista de fișiere a portalului
 │    │    └─ call_portal()
 │    ├─ stored_files()                      lista din baza de date, pentru comparație
 │    ├─ download_results()                  doar pentru fiecare fișier nou sau înlocuit
 │    │    ├─ call_portal()
 │    │    ├─ to_number()
 │    │    └─ tidy_town()
 │    ├─ save_results() → open_database()    salvează fișierul, într-o singură tranzacție
 │    └─ open_database()                     notează verificarea în tabelul „checks”
 ├─ stored_files()                           reîmprospătează lista „Exam and school year”
 └─ database_status()                        noul rând „Data: ...”
```

### Ce funcții vorbesc cu lumea de afară

| Funcție | Vorbește cu |
|---|---|
| `find_ministry_on_portal()` | **mon.bg**, site-ul ministerului, doar când baza de date este umplută sau actualizată |
| `call_portal()` | **data.egov.bg**, portalul de date deschise, doar când baza de date este umplută sau actualizată. Orice întrebare către portal trece prin această singură funcție. |
| `open_database()` | Fișierul **school_results.db** de lângă script, pe calculatorul tău. Orice folosire a bazei de date trece prin această singură funcție. |
| `ollama_problem()` și `write_overview()` | **Ollama** pe calculatorul tău: AI-ul gemma4 |
| `load_region_map()` | Fișierul **bulgaria_regions.geojson** de lângă script, pe calculatorul tău |
| `main()`, prin `page.launch()` | **browserul tău** |

Toate celelalte funcții lucrează doar cu date care sunt deja în memorie.

---

## 5. Fiecare funcție, pe rând

### Grupa 1: Mici ajutoare

#### `tidy(text)`: [linia 202](alex_school_results.py#L202)
- **Într-o propoziție:** face un nume ușor de comparat cu alt nume.
- **Primește:** un text. **Dă înapoi:** același text cu litere mici, cu spații simple și fără punct
  la sfârșit.
- **Exemplu:** `"Резултати  от ДЗИ."` → `"резултати от дзи"`
- **De ce:** ministerul scrie uneori numele unui set de date cu un spațiu dublu sau cu un punct la
  sfârșit. După `tidy()`, „același nume, scris puțin diferit” contează ca fiind egal.
- **Cum:** `text.split()` taie textul în cuvinte și scoate toate spațiile; `" ".join(...)` lipește
  cuvintele la loc cu exact un spațiu; `.lower()` face literele mici; `.rstrip(".")` scoate punctul
  de la sfârșit.
- **Apelată de:** `find_exam_datasets()`.

#### `tidy_town(town)`: [linia 209](alex_school_results.py#L209)
- **Într-o propoziție:** face ca aceeași localitate să arate la fel în toate fișierele.
- **Exemple:** `"ГР. СОФИЯ"` → `"ГР.СОФИЯ"` · `"Прага"` → `"ПРАГА"` ·
  `"СОФИЯ 11 РН КРАСНА ПОЛЯНА"` (un cartier din Sofia) → `"ГР.СОФИЯ"`
- **Cum:**
  1. Spații simple și MAJUSCULE (`.upper()`).
  2. O **expresie regulată** (`re.sub`, un model de căutare pentru text) scoate spațiul de după
     „ГР.” sau „С.”.
  3. Dacă numele începe cu „СОФИЯ, un număr, РН”, este un cartier din Sofia, așa că devine
     „ГР.СОФИЯ”.
- **Apelată de:** `download_results()`, pentru fiecare școală.

#### `to_number(text)`: [linia 306](alex_school_results.py#L306)
- **Într-o propoziție:** transformă o celulă din fișier într-un număr sau în `None` când nu există
  rezultat.
- **Exemple:** `"52.4"` → `52.4` · `"3,09"` → `3.09` (virgulă zecimală) · `""` → `None` ·
  `"0"` → `None` (zero înseamnă că nimeni n-a dat acel examen) · `"Област"` → `None`
- **Cum:** înlocuiește virgula cu un punct și încearcă `float()`. Dacă Python nu poate face un număr,
  aruncă o eroare `ValueError`; partea `except` o prinde și întoarce `None`. Ultima linie,
  `return value or None`, transformă `0` în `None`.
- **Apelată de:** `download_results()`, pentru fiecare celulă.

#### `weighted_average(table, count_column, average_column)`: [linia 483](alex_school_results.py#L483)
- **Într-o propoziție:** media pe toți **elevii**, nu pe școli.
- **De ce:** o școală cu 100 de elevi trebuie să conteze mai mult decât o școală cu 5.
- **Exemplu:** școala A are 100 de elevi cu media 60; școala B are 5 elevi cu media 90.
  - Media celor două școli este (60 + 90) / 2 = **75**, ceea ce induce în eroare.
  - Media ponderată este (100 × 60 + 5 × 90) / 105 = **61,43**, ceea ce e corect.
- **Dă înapoi două valori:** media și numărul de elevi. Dacă nimeni n-a dat examenul: `(None, 0)`.
- **Cum:** scoate rândurile cu valori goale (`dropna`), înmulțește elevii × media pentru fiecare
  școală, adună totul și împarte la numărul total de elevi.
- **Apelată de:** `rank_towns()`, `show_results()`, `write_overview()`, `subject_score()`.

#### `town_label(town, region)`: [linia 495](alex_school_results.py#L495)
- **Într-o propoziție:** construiește textul afișat în lista de localități (Town).
- **Exemplu:** `town_label("ГР.ВАРНА", "ВАРНА")` → `"ГР.ВАРНА (ВАРНА)"`
- **De ce și regiunea:** multe sate au același nume în regiuni diferite.
- **Apelată de:** `town_choices()`.

#### `split_town_label(label)`: [linia 503](alex_school_results.py#L503)
- **Într-o propoziție:** opusul lui `town_label()`: desparte din nou localitatea și regiunea.
- **Exemplu:** `"ГР.ВАРНА (ВАРНА)"` → `("ГР.ВАРНА", "ВАРНА")`
- **Cum:** `rsplit(" (", 1)` taie textul o singură dată, la ultimul `" ("`; `rstrip(")")` scoate
  paranteza de închidere.
- **Apelată de:** `show_results()`.

---

### Grupa 2: Luarea datelor de pe internet

Aceste funcții sunt folosite **doar pentru a umple sau a actualiza baza de date**: prima dată și
atunci când apeși butonul verde **Check for new results**.

#### `call_portal(method, payload)`: [linia 223](alex_school_results.py#L223)
- **Într-o propoziție:** trimite o întrebare portalului de date deschise (data.egov.bg) și întoarce
  răspunsul lui.
- **Primește:** numele întrebării (`method`), de exemplu `"listResources"`, și detaliile ei
  (`payload`) sub formă de dicționar. **Dă înapoi:** răspunsul, ca dicționar.
- **Exemplu:** `call_portal("getOrganisationDetails", {"org_uri": "a57a2273-..."})` →
  `{"success": True, "data": {"id": 117, "name": "Министерство на образованието и науката", ...}}`
- **Cum:**
  1. `requests.post(...)` trimite întrebarea.
  2. `raise_for_status()` se oprește cu o eroare dacă site-ul răspunde cu un cod de eroare, cum ar
     fi 404 sau 500.
  3. `.json()` transformă textul JSON într-un dicționar Python.
  4. Portalul spune `"success": false` când ceva nu e în regulă. Atunci funcția aruncă propria ei
     eroare (`RuntimeError`) cu mesajul portalului.
- **Bine de știut:** aceasta este **singura ușă către portal**. Dacă portalul se schimbă vreodată,
  există un singur loc de reparat.
- **Apelată de:** `find_exam_datasets()`, `list_exam_files()`, `download_results()`.

#### `find_ministry_on_portal()`: [linia 236](alex_school_results.py#L236)
- **Într-o propoziție:** citește pagina „date deschise” a ministerului de pe mon.bg și găsește
  ID-ul ministerului pe portal.
- **Primește:** nimic. **Dă înapoi:** ID-ul, un text ca `"a57a2273-6b21-4a7a-99ee-05ec4f67ebe4"`.
- **Cum:** aceasta este partea de **web scraping** (extragerea datelor dintr-o pagină web), cu
  BeautifulSoup:
  1. `requests.get` descarcă pagina.
  2. `BeautifulSoup` citește codul ei HTML.
  3. O buclă trece prin fiecare link (`<a href="...">`).
  4. Când un link conține `data.egov.bg/organisation/profile/`, decupează ID-ul dintre
     `/profile/` și `?` și îl întoarce.
  5. Dacă nu găsește niciun link, aruncă o eroare.
- **Apelată de:** `update_database()`. Dacă mon.bg nu funcționează, `update_database()` folosește
  în schimb `KNOWN_MINISTRY_ID`.

#### `find_exam_datasets(ministry_id)`: [linia 252](alex_school_results.py#L252)
- **Într-o propoziție:** găsește cele 4 seturi de date ale ministerului despre examene (НВО clasele
  a 4-a, a 7-a și a 10-a, și ДЗИ) printre cele aproximativ 350 de seturi de date ale lui.
- **Dă înapoi:** un dicționar *examen → ID-ul setului de date*, de exemplu
  `{"NVO 7th grade": "b56288b6-...", ...}`
- **Cum:**
  1. Cere portalului numărul ministerului (117).
  2. Cere seturile de date ale ministerului **pagină cu pagină**, câte 100 odată. Bucla
     `while True:` se repetă până când o pagină are mai puțin de 100 (`break`).
  3. Pentru fiecare examen din `EXAMS`, păstrează seturile de date al căror nume trecut prin
     `tidy()` este egal cu numele așteptat.
  4. Dacă mai multe au acel nume, îl ia pe cel mai nou (`max` după `updated_at`).
- **Semnul `_`:** în `for exam, (_, dataset_name) in EXAMS.items():`, fiecare valoare din `EXAMS`
  este o pereche (tip, nume). Aici avem nevoie doar de nume, așa că tipul primește numele „nu-mi
  trebuie”, `_`.
- **Apelată de:** `update_database()`.

#### `list_exam_files(exam_datasets)`: [linia 282](alex_school_results.py#L282)
- **Într-o propoziție:** listează fișierele anuale ale fiecărui examen de pe portal și îi dă
  fiecăruia un nume ușor de citit, ca `"NVO 7th grade - 2025/2026"`.
- **Dă înapoi:** un dicționar *„examen - an” → (tip, ID-ul fișierului)*, de exemplu
  `{"NVO 7th grade - 2025/2026": ("nvo", "08157f0e-..."), ...}`.
- **Cum:**
  1. Cere portalului fișierele fiecărui set de date.
  2. O **expresie regulată** (`re.search`) găsește anul școlar în numele fișierului
     („учебна 2025/2026”). Fișierele fără el au un format vechi, așa că `continue` le sare.
  3. Pentru ДЗИ păstrează doar sesiunea principală (mai–iunie) a examenelor obligatorii.
  4. Sortează fișierele cu anul cel mai nou primul.
- **Apelată de:** `update_database()`, care compară această listă cu lista din baza de date.

#### `download_results(kind, resource_id)`: [linia 318](alex_school_results.py#L318)
- **Într-o propoziție:** descarcă un fișier cu rezultate de pe portal și îl transformă într-un tabel
  curat, cu un rând pentru fiecare școală.
- **Primește:** tipul (`"nvo"` sau `"dzi"`) și ID-ul fișierului. **Dă înapoi:** un tabel cu
  coloanele Region, Municipality, Town, School, School code (regiune, comună, localitate, școală,
  codul școlii) și 4 coloane cu rezultate.
- **Cea mai importantă funcție de curățare:** repară toate problemele din fișierele guvernului:
  - un rând de titlu deasupra numelor coloanelor;
  - coloane într-o altă ordine în unii ani;
  - coduri de școli scrise cu spații;
  - virgule zecimale;
  - „В ЧУЖБИНА” în loc de „ЧУЖБИНА” (în străinătate);
  - mai multe coloane de materii pentru al 2-lea examen de bacalaureat.
- **Cum:**
  1. Descarcă rândurile, adică liste de texte, prin `call_portal("getResourceData", ...)`.
  2. Găsește rândul de antet: rândul care începe cu „Област”.
  3. Găsește care coloane sunt „Училище” (școala) și „Код” (codul), după numele lor.
  4. Pentru fiecare școală: apelează `to_number()` pe fiecare celulă.
     - **НВО:** ia ultimele 4 numere.
     - **ДЗИ:** limba bulgară este în coloanele 5 și 6 (Python numără de la 0, deci acestea sunt a
       6-a și a 7-a coloană). Al 2-lea examen este media ponderată a tuturor celorlalte coloane de
       materii.
     - Pune în ordine regiunea, codul, numele și localitatea (`tidy_town()`).
  5. Construiește tabelul (`pd.DataFrame`). Numerele de elevi devin numere întregi (`Int64`), iar
     mediile sunt rotunjite la 2 zecimale.
- **Bine de știut:** tabelul curat merge direct în baza de date (`save_results()`), așa că
  curățarea se face **o singură dată pentru fiecare fișier**, nu de fiecare dată când te uiți la
  rezultate.
- **Apelată de:** `update_database()`.

---

### Grupa 3: Baza de date

#### `open_database()`: [linia 364](alex_school_results.py#L364)
- **Într-o propoziție:** deschide fișierul bazei de date `school_results.db` și îl creează, împreună
  cu tabelele lui, dacă nu există încă.
- **Dă înapoi:** o **conexiune** deschisă la baza de date: linia prin care Python vorbește cu ea.
- **Cum:**
  1. `sqlite3.connect(DATABASE_FILE)` deschide fișierul sau îl creează dacă lipsește.
  2. `executescript(DATABASE_TABLES)` rulează codul SQL din `DATABASE_TABLES`.
     `CREATE TABLE IF NOT EXISTS` creează fiecare tabel doar dacă nu există deja.
- **Bine de știut:** cine deschide baza de date trebuie s-o și închidă cu `.close()`. De aceea
  celelalte funcții folosesc `try:` … `finally: database.close()`: `finally` se execută chiar și
  când ceva eșuează între timp.
- **Apelată de:** `save_results()`, `stored_files()`, `read_results()`, `update_database()`,
  `database_status()`.

#### `save_results(choice, kind, resource_id, table)`: [linia 374](alex_school_results.py#L374)
- **Într-o propoziție:** salvează în baza de date un fișier cu rezultate descărcat, înlocuind o copie
  mai veche a lui.
- **Primește:** numele fișierului (`choice`, ca `"NVO 7th grade - 2025/2026"`), tipul lui, ID-ul lui
  pe portal și tabelul curat de la `download_results()`.
- **Cum:**
  1. Redenumește coloanele tabelului cu numele din baza de date (`DATABASE_COLUMNS`) și adaugă o
     coloană `choice`, ca fiecare rând să știe din ce fișier face parte.
  2. În interiorul lui `with database:`, care este o **tranzacție**:
     - șterge rândurile vechi ale fișierului (`DELETE FROM results WHERE choice = ?`);
     - adaugă rândurile noi (`to_sql`);
     - scrie rândul fișierului în tabelul `files`, cu data de azi (`INSERT OR REPLACE`).
  3. Datorită tranzacției, ori se salvează totul, ori nimic: o actualizare care eșuează la jumătate
     nu lasă niciodată o jumătate de fișier.
- **Semnul `?` din SQL:** un loc rezervat pe care sqlite3 îl completează cu valoarea, în siguranță.
  Nu lipi niciodată singur valori în textul SQL.
- **Apelată de:** `update_database()`.

#### `stored_files()`: [linia 392](alex_school_results.py#L392)
- **Într-o propoziție:** listează toate fișierele cu rezultate din baza de date.
- **Dă înapoi:** același fel de dicționar ca `list_exam_files()`: *„examen - an” → (tip, ID-ul
  fișierului)*. Acest dicționar umple lista „Exam and school year” (examen și an școlar) de pe
  pagină.
- **Cum:** `SELECT … FROM files` citește tabelul `files`. Apoi două sortări pun fișierele examen cu
  examen (în ordinea din `EXAMS`), cu anul cel mai nou primul. Sortarea din Python este **stabilă**:
  când sortează după examen, fișierele aceluiași examen își păstrează ordinea anilor din prima
  sortare.
- **Apelată de:** `main()`, `update_database()`, `check_for_new_results()`.

#### `read_results(choice, kind)`: [linia 409](alex_school_results.py#L409)
- **Într-o propoziție:** citește un examen și un an din baza de date, ca tabel cu numele de coloane
  de pe pagină.
- **Exemplu:** `read_results("NVO 7th grade - 2025/2026", "nvo")` dă cele 1.702 școli în cam 20 de
  milisecunde.
- **Cum:**
  1. `pd.read_sql("SELECT … FROM results WHERE choice = ? ORDER BY rowid", …)` întreabă baza de
     date. `ORDER BY rowid` păstrează ordinea în care au fost salvate rândurile.
  2. Redenumește coloanele cu numele de pe pagină (`RESULT_COLUMNS`) și transformă numerele de elevi
     în numere întregi (`Int64`).
- **Apelată de:** `load_choice()`, `main()`.

#### `update_database()`: [linia 426](alex_school_results.py#L426)
- **Într-o propoziție:** cere portalului lista lui de fișiere cu rezultate și le descarcă doar pe
  cele pe care baza de date nu le are încă sau pe care ministerul le-a înlocuit.
- **Dă înapoi:** lista fișierelor adăugate sau înlocuite. Este goală dacă nu era nimic nou.
- **Cum:**
  1. `find_ministry_on_portal()` (sau `KNOWN_MINISTRY_ID` dacă mon.bg nu merge), apoi
     `find_exam_datasets()` și `list_exam_files()`: lista portalului (cam 15–20 de secunde).
  2. O compară cu `stored_files()`. Un fișier contează ca nou dacă examenul și anul lui lipsesc sau
     dacă ID-ul fișierului este diferit, ceea ce înseamnă că ministerul l-a înlocuit cu o versiune
     corectată.
  3. Pentru fiecare fișier nou: `download_results()`, apoi `save_results()`.
  4. Notează verificarea în tabelul `checks`, cu data și numărul de fișiere noi.
- **Apelată de:** `main()` (doar când baza de date este goală) și `check_for_new_results()`
  (butonul verde).

#### `database_status()`: [linia 455](alex_school_results.py#L455)
- **Într-o propoziție:** scrie rândul din partea de sus a paginii, de exemplu *„Data: 25 results
  files in the local database (school_results.db) · last checked on data.egov.bg: 2026-11-25
  13:22”* (25 de fișiere cu rezultate în baza de date locală · ultima verificare pe data.egov.bg).
- **Cum:** pune bazei de date două întrebări în SQL: `SELECT COUNT(*) FROM files` (câte fișiere) și
  `SELECT MAX(checked_at) FROM checks` (ultima verificare). Dacă portalul n-a fost verificat
  niciodată, scrie „never” (niciodată).
- **Apelată de:** `build_page()` și `check_for_new_results()`.

#### `load_choice(exam_files, choice)`: [linia 469](alex_school_results.py#L469)
- **Într-o propoziție:** transformă ce ai ales în lista „Exam and school year” în tabelul cu
  rezultate, din baza de date, sau afișează un mesaj de eroare pe pagină.
- **Primește:** dicționarul de fișiere și alegerea ta, de exemplu `"DZI (matura) - 2025/2026"`.
  **Dă înapoi două valori:** tipul (`"dzi"`) și tabelul.
- **Cum:**
  1. Dacă alegerea ta nu este în dicționar, aruncă `gr.Error(...)`, pe care Gradio îl arată pe
     pagină ca o fereastră roșie.
  2. Caută tipul.
  3. Apelează `read_results()` în interiorul lui `try:`. Dacă baza de date nu poate fi citită,
     primești un `gr.Error` prietenos în loc ca programul să se blocheze.
- **Apelată de:** `town_choices()`, `show_results()`, `write_overview()`, `show_map()`.

---

### Grupa 4: Alegere și clasament

#### `town_choices(exam_files, choice, region)`: [linia 511](alex_school_results.py#L511)
- **Într-o propoziție:** face lista de localități pentru lista derulantă „Town”.
- **Dă înapoi:** o listă care începe cu `"All towns"` (toate localitățile), apoi localitățile în
  ordine alfabetică, de exemplu `"ГР.ВАРНА (ВАРНА)"`.
- **De ce orașele vin primele:** în alfabet Г vine înaintea lui С, așa că „ГР.” (orașele) vin
  înaintea lui „С.” (satele).
- **Cum:** încarcă tabelul (`load_choice()`), păstrează doar școlile din regiunea aleasă, scoate
  repetările (`drop_duplicates()`), face etichetele (`town_label()`) și le sortează.
- **Apelată de:** `build_page()` (prima listă) și `refresh_towns()` (când se schimbă examenul sau
  regiunea).

#### `rank_towns(table, kind, min_students)`: [linia 524](alex_school_results.py#L524)
- **Într-o propoziție:** face un clasament al localităților, cu cea mai bună prima.
- **Dă înapoi:** un tabel cu un rând pentru fiecare localitate: `#`, Town, Region, Schools, Students
  (localitate, regiune, școli, elevi), cele două medii și „Both subjects” (ambele materii).
- **Cum:**
  1. `groupby(["Region", "Town"])` adună laolaltă școlile din aceeași localitate.
  2. Pentru fiecare localitate, apelează `weighted_average()` pentru limba bulgară și pentru
     matematică (sau al 2-lea examen).
  3. Sare peste localitățile cu prea puțini elevi (mai puțin de `min_students`), ca un sat foarte
     mic să nu poată câștiga.
  4. „Both subjects” = (limba bulgară + matematică) / 2.
  5. Sortează după „Both subjects”, de la cel mai mare, și adaugă coloana cu locul, `#`: 1, 2, 3…
- **`min_students`:** 100 pentru toată Bulgaria, 30 în interiorul unei regiuni.
- **Apelată de:** `show_results()` (locul localității tale) și `write_overview()` (primele 5).

#### `rank_schools(table, kind)`: [linia 548](alex_school_results.py#L548)
- **Într-o propoziție:** la fel ca `rank_towns()`, dar pentru școli.
- **Cum:**
  1. Păstrează doar școlile cu cel puțin 10 elevi la fiecare examen (`MIN_SCHOOL_STUDENTS`).
     - `big_enough` este o listă de `True`/`False`, câte una pentru fiecare școală (o **mască**);
       `table[big_enough]` păstrează doar rândurile marcate cu `True`.
     - `fillna(0)` înseamnă că un număr de elevi gol contează ca 0, adică prea puțini.
  2. Calculează „Both subjects”, sortează școlile și le numerotează.
- **Apelată de:** `write_overview()`.

#### `show_results(exam_files, choice, region, town, search, rank_by)`: [linia 565](alex_school_results.py#L565)
- **Într-o propoziție:** face tot ce apare în fila „Schools”: textul rezumatului și tabelul.
- **Primește:** cele 5 alegeri ale tale de pe pagină: examenul, regiunea, localitatea, textul căutat
  și „rank by” (criteriul de clasament). **Dă înapoi două valori:** rezumatul (text Markdown) și
  tabelul.
- **Cum:**
  1. **Încărcare:** ia tabelul cu `load_choice()`.
  2. **Filtrare:** păstrează școlile din localitatea ta sau din regiunea ta.
     - Dacă ai ales o localitate, păstrează și regiunea ei și toată țara, pentru comparație.
     - Desparte eticheta localității cu `split_town_label()`.
  3. **Căutare:** păstrează rândurile în care școala, localitatea sau comuna conține textul tău.
     `case=False` înseamnă că nu contează dacă literele sunt mari sau mici.
  4. **Sortare:** după limba bulgară sau după matematică, cea mai bună prima, și adaugă coloana `#`.
  5. **Rezumat:** numărul de școli și mediile (`weighted_average()`), comparate cu regiunea și cu
     Bulgaria. Dacă ai ales o localitate, adaugă locul ei în Bulgaria și în regiunea ei
     (`rank_towns()`).
- **Apelată de:** `show()` de pe pagină.

---

### Grupa 5: Prezentarea AI

#### `ollama_problem()`: [linia 637](alex_school_results.py#L637)
- **Într-o propoziție:** verifică dacă AI-ul este gata: Ollama rulează și gemma4 este descărcat.
- **Dă înapoi:** `None` dacă totul e în regulă („nicio problemă”), altfel un mesaj care spune ce nu
  merge.
- **Cum:**
  1. Cere lui Ollama de pe calculatorul tău (`http://localhost:11434/api/tags`) lista lui de modele.
     - **Niciun răspuns:** „Ollama isn't running…” (Ollama nu rulează).
     - **gemma4 nu e în listă:** „gemma4 isn't downloaded…” (gemma4 nu e descărcat).
  2. Pentru Ollama, `gemma4` și `gemma4:latest` sunt același model, așa că programul adaugă
     `:latest` înainte de comparație.
- **De ce numele acesta:** funcția răspunde la întrebarea *„care e problema?”*, iar `None`
  înseamnă că nu există niciuna. De aceea codul se citește `if problem:`.
- **Apelată de:** `main()` (un avertisment la pornire) și `write_overview()` (înainte de a întreba
  AI-ul).

#### `overview_messages(choice, kind, area, area_averages, towns, schools, min_town_students)`: [linia 653](alex_school_results.py#L653)
- **Într-o propoziție:** scrie „scrisoarea” către AI: regulile noastre plus faptele.
- **Dă înapoi:** o listă cu două mesaje:
  - `{"role": "system", ...}`: regulile, din `overview_system_prompt` de la începutul fișierului.
  - `{"role": "user", ...}`: examenul, zona, mediile și primele 5 localități și școli, în JSON.
- **JSON:** `json.dumps(...)` transformă tabelele în text pe care AI-ul îl poate citi.
  `ensure_ascii=False` păstrează literele chirilice ușor de citit.
- **Apelată de:** `write_overview()`.

#### `template_overview(area, towns, schools)`: [linia 677](alex_school_results.py#L677)
- **Într-o propoziție:** scrie prezentarea **fără AI**, din aceleași numere pe care le primește
  AI-ul.
- **Când:** dacă Ollama nu rulează, dacă modelul nu e descărcat sau dacă AI-ul eșuează la jumătate.
- **Dă înapoi:** text Markdown cu aceeași așezare ca al AI-ului: „## Top towns” (primele
  localități), o listă numerotată, „## Top schools” (primele școli), o listă numerotată și un rând
  de încheiere dacă majoritatea primelor școli sunt în aceeași localitate.
- **Exemplu de rând:** `1. **ГР.ВАРНА**: 60.04, 6.75 above the area's average`
- **Cum:**
  1. `to_dict(orient="records")` transformă fiecare tabel într-o listă de dicționare, câte unul
     pentru fiecare rând, iar un f-string scrie câte un rând pentru fiecare.
  2. `value_counts()` numără localitățile primelor școli. Dacă o localitate le are pe toate sau mai
     mult de jumătate, rândul de încheiere spune asta.
- **Bine de știut:** este mai simplu decât textul AI-ului, dar **instant și mereu exact**.
- **Apelată de:** `write_overview()`.

#### `write_overview(exam_files, choice, region)`: [linia 708](alex_school_results.py#L708)
- **Într-o propoziție:** calculează primele 5 localități și școli, le afișează, apoi o lasă pe
  gemma4 să scrie prezentarea cuvânt cu cuvânt.
- **Ce are special:** este un **generator**. Folosește `yield` în loc de `return`, iar fiecare
  `yield` trimite paginii o actualizare: cele două tabele și textul scris până atunci. Așa apare
  textul cuvânt cu cuvânt.
- **Cum:**
  1. Încarcă tabelul și păstrează regiunea aleasă.
  2. Apelează `rank_towns()` și `rank_schools()` și le păstrează pe primele 5 (`head(TOP)`).
  3. Calculează media zonei și cât de departe de ea este fiecare localitate și școală
     („Vs area average”, față de media zonei).
     - **Codul calculează asta, nu AI-ul,** pentru că modelele AI nu se descurcă bine cu
       aritmetica. În testele noastre, gemma4 a scris 13,04 în loc de 14,04.
  4. Verifică Ollama (`ollama_problem()`). Dacă există o problemă, programul scrie singur
     prezentarea (`template_overview()`) și spune de ce.
  5. `ollama.chat(..., stream=True)` o întreabă pe gemma4. Pentru fiecare bucățică de text (un
     **chunk**), adaugă bucata și trimite cu `yield` textul mai lung.
  6. Dacă ceva eșuează în timp ce AI-ul scrie, `try`/`except` înlocuiește textul cu prezentarea
     programului și spune ce n-a mers.
- **Setările din apel:**
  - `temperature 0.3`: să se țină de fapte.
  - `num_predict 900`: o lungime maximă.
  - `think=False`: fără „gândire” ascunsă, ceea ce e mai rapid.
- **Apelată de:** `overview()` de pe pagină.

---

### Grupa 6: Harta și cele trei vederi ale ei

#### `schools_in_bulgaria(table)`: [linia 772](alex_school_results.py#L772)
- **Într-o propoziție:** lasă deoparte școlile din străinătate, care nu au o regiune pe hartă.
- **Cum:** în Bulgaria fiecare localitate începe cu „ГР.” (oraș) sau „С.” (sat).
  `str.startswith(("ГР.", "С."))` dă `True` pentru acestea, iar regiunea nu trebuie să fie
  „ЧУЖБИНА”. Tabelul păstrează doar acele rânduri.
- **De ce:** unele fișiere trec școlile din străinătate la ЧУЖБИНА, altele la o regiune din
  Bulgaria. Școala din БРАТИСЛАВА, de exemplu, este trecută la СОФИЯ-ГРАД, ceea ce ar amesteca-o în
  media Sofiei.
- **Apelată de:** `show_map()` și `region_gaps()`.

#### `subject_score(schools, kind, subject)`: [linia 781](alex_school_results.py#L781)
- **Într-o propoziție:** media unui grup de școli la materia aleasă, ponderată cu numărul de elevi.
- **Primește:** un grup de școli (o regiune, toate orașele, toate satele sau toată țara), tipul de
  examen și materia: „Both subjects”, „Bulgarian (BEL)” sau „Maths / 2nd exam”. **Dă înapoi:** un
  singur număr sau `None` dacă nu există rezultate.
- **Cum:** apelează `weighted_average()` pentru limba bulgară și pentru matematică (sau al 2-lea
  examen), apoi o întoarce pe cea pe care ai cerut-o. „Both subjects” este media celor două.
- **Exemplu:** НВО clasa a 7-a 2025/2026, ambele materii: toată țara dă 46,87, СОФИЯ-ГРАД dă 60,22.
- **Apelată de:** `show_map()` și `region_gaps()`.

#### `school_spread(schools, kind, subject)`: [linia 798](alex_school_results.py#L798)
- **Într-o propoziție:** cât de împrăștiate sunt rezultatele școlilor la materia aleasă.
- **Dă înapoi:** un singur număr, **abaterea standard**: în linii mari, cât de departe de medie este
  o școală obișnuită. Un număr mic înseamnă că majoritatea școlilor au cam aceleași rezultate; unul
  mare înseamnă că sunt departe unele de altele.
- **Cum:** alege coloana materiei alese (pentru „Both subjects”, media celor două coloane, școală cu
  școală), iar `.std()` din pandas face restul.
- **De ce:** comparația cu media națională anulează cât de *ușor* a fost un test, dar nu și cât de
  mult *îi împrăștie pe elevi*. Un test care îi împrăștie mai mult pe elevi mărește și decalajul
  dintre regiuni, chiar dacă de fapt nu s-a schimbat nimic. Împărțirea decalajului la acest număr
  scoate acest efect.
- **Exemplu:** НВО clasa a 7-a, ambele materii: 15,01 puncte în 2018/2019, 17,55 în 2025/2026.
- **Apelată de:** `region_gaps()`.

#### `load_region_map()`: [linia 816](alex_school_results.py#L816)
- **Într-o propoziție:** citește granițele celor 28 de regiuni din fișierul
  `bulgaria_regions.geojson`.
- **Dă înapoi:** conținutul fișierului, ca dicționar. Pentru fiecare regiune are numele așa cum e
  scris în date (de exemplu „ВАРНА”), codul (BG-03), numele în engleză și granița, ca listă de
  puncte.
- **`@cache`:** citește fișierul o singură dată, prima dată când se afișează harta, și îl ține minte.
- **Fișierul:** făcut din harta lumii de la Natural Earth, care este în domeniul public, păstrând
  doar Bulgaria (66 KB).
- **Apelată de:** `show_map()` și `show_change()`.

#### `colour_key(values, zero_label)`: [linia 824](alex_school_results.py#L824)
- **Într-o propoziție:** stabilește scara de culori pentru un set de numere peste și sub 0: cele
  două capete ale ei și etichetele legendei.
- **Primește:** numerele (o coloană de tabel) și textul pentru mijlocul legendei, ca
  „0 = average” (0 = media) sau „0 = no change” (0 = nicio schimbare). **Dă înapoi trei valori:**
  `limit`, cea mai mare distanță față de 0; cele 5 poziții ale etichetelor legendei; și etichetele
  însele.
- **Cum:**
  1. `values.abs().max()` este cel mai mare număr, fără a ține cont de semn. Scara merge de la
     `-limit` la `+limit`, aceeași distanță în ambele direcții, așa că 0 este mereu culoarea din
     mijloc, galbenul.
  2. Dacă nu există numere sau toate sunt 0, folosește o limită foarte mică (0,01), ca graficul să
     funcționeze totuși.
  3. Mai puține zecimale pentru numerele mari: „+13” pentru puncte, „+0.41” pentru note.
- **Exemplu:** pentru diferențele de la clasa a 7-a (−13,45 … +13,34) dă etichetele „−13”, „−7”,
  „0 = average”, „+7”, „+13”.
- **Apelată de:** `region_map()`, `region_bars()` și `trend_heatmap()`.

#### `signed(value, decimals=2)`: [linia 840](alex_school_results.py#L840)
- **Într-o propoziție:** scrie un număr cu semnul lui, ca „+2.14” sau „−4.99”, pentru numerele
  afișate pe grafice.
- **`decimals=2`:** un parametru cu **valoare implicită**. Dacă nu-l dai, este 2.
- **Cum:** `f"{value:+.2f}"` scrie numărul cu semn și 2 zecimale. Un număr care se rotunjește la
  zero ar ieși „-0.00”, așa că pentru acestea scoate semnul: `text[1:]` este textul fără primul
  caracter.
- **Exemplu:** `signed(2.141)` dă „+2.14”, `signed(-0.004)` dă „0.00”, iar `signed(-0.04, 1)` dă
  „0.0”.
- **Apelată de:** `region_bars()` și `trend_heatmap()`.

#### `year_labels(years)`: [linia 849](alex_school_results.py#L849)
- **Într-o propoziție:** scrie anii școlari pe două rânduri, ca „2018/” deasupra lui „2019”, ca să
  încapă sub coloanele înguste ale graficelor de tendințe fără să fie scriși înclinat.
- **Cum:** `year.replace("/", "/<br>")`. În etichetele din Plotly, `<br>` înseamnă „rând nou”.
- **Apelată de:** `trend_heatmap()` și `gap_trend_chart()`.

#### `region_map(regions, borders, column, key_title, zero_label)`: [linia 857](alex_school_results.py#L857)
- **Într-o propoziție:** desenează harta, cu fiecare regiune colorată după numerele dintr-o coloană a
  tabelului: diferența ei față de media națională sau cât s-a schimbat acea diferență.
- **Primește:** tabelul regiunilor, granițele, coloana după care colorează (`"Vs Bulgaria"` sau
  `"Change"`), titlul legendei de culori și textul pentru mijlocul ei („0 = average” sau
  „0 = no change”). Tabelul are și o coloană `"Hover"`: textul afișat când mouse-ul este deasupra
  unei regiuni. **Dă înapoi:** o figură Plotly, pe care Gradio o afișează pe pagină.
- **Cum:**
  1. `colour_key()` dă cele două capete ale scării și etichetele legendei.
  2. `go.Choropleth(...)` este harta Plotly cu „zone colorate”. `featureidkey="properties.region"`
     îi spune să potrivească fiecare graniță cu datele după numele bulgăresc al regiunii.
  3. `zmin=-limit, zmax=limit`: culorile merg la aceeași distanță în ambele direcții, așa că 0 este
     mereu culoarea din mijloc, galbenul.
  4. `fitbounds="locations", visible=False` face zoom pe Bulgaria și ascunde restul lumii.
- **De ce o singură funcție pentru două hărți:** vederile „Difference” și „Change” desenează același
  fel de hartă dintr-o coloană diferită, așa că folosesc împreună această funcție în loc să aibă
  două copii ale ei.
- **Apelată de:** `show_map()` și `show_change()`.

#### `region_bars(regions, column, axis_title)`: [linia 885](alex_school_results.py#L885)
- **Într-o propoziție:** aceleași 28 de regiuni ca grafic cu bare, cea mai mare sus, cu numărul
  exact al fiecărei regiuni scris lângă bara ei.
- **De ce:** o hartă e bună pentru *unde*, iar barele sunt mai bune pentru *cât*. Numerele scrise
  (ca `+13.34` sau `−13.45`, făcute de `signed()`) te lasă să citești graficul și fără culori.
- **Cum:**
  1. `go.Bar(..., orientation="h")` face bare orizontale, cu aceleași `MAP_COLOURS` și aceeași scară
     (`colour_key()`) ca harta.
  2. Axa merge la aceeași distanță în ambele direcții, cu 0 la mijloc. Este de 1,6 ori mai lungă
     decât cel mai mare număr, ca numerele să încapă lângă bare.
  3. Tabelul trebuie să fie deja sortat, cu cel mai mic primul, pentru că Plotly desenează primul
     rând jos.
- **Apelată de:** `show_map()` și `show_change()`.

#### `show_map(exam_files, choice, subject)`: [linia 920](alex_school_results.py#L920)
- **Într-o propoziție:** face tot ce apare în fila „Map and trends of the regions”: rezumatul diferențelor,
  harta și graficul cu bare.
- **Primește:** examenul și anul alese și materia din „Colour by” (colorează după). **Dă înapoi
  trei valori:** textul rezumatului, harta și graficul cu bare.
- **Cum:**
  1. Încarcă tabelul (`load_choice()`) și lasă deoparte școlile din străinătate
     (`schools_in_bulgaria()`).
  2. Citește granițele (`load_region_map()`). Dacă fișierul lipsește, întoarce un mesaj clar în loc
     să se blocheze.
  3. Calculează media națională și media fiecărei regiuni cu `subject_score()`, câte o regiune
     odată datorită lui `groupby("Region")`, și diferența fiecărei regiuni („Vs Bulgaria”).
  4. Sortează regiunile și scrie textul `"Hover"` al fiecăreia, cu numele ei în engleză din fișierul
     cu granițe. Găsește cea mai bună și cea mai slabă regiune și compară orașele („ГР.”) cu satele
     („С.”).
  5. Desenează harta (`region_map()`) și barele (`region_bars()`), ambele colorate după coloana
     „Vs Bulgaria”.
- **Exemplu de rezumat:** „Best region: СОФИЯ-ГРАД 60.22 (+13.34) · worst region: СЛИВЕН 33.43
  (−13.45) · gap: 26.79 points” (cea mai bună regiune · cea mai slabă regiune · decalaj), apoi
  „Cities (ГР.): 49.68 · villages (С.): 30.95 · gap: 18.73 points” (orașe · sate · decalaj).
- **Apelată de:** `map_view()` de pe pagină, pentru vederea „Difference from Bulgaria”.

#### `exam_years(exam_files, choice)`: [linia 969](alex_school_results.py#L969)
- **Într-o propoziție:** găsește toți anii examenului ales, cu cel mai vechi primul.
- **Cum:** o alegere arată ca „NVO 7th grade - 2025/2026”. `rsplit(" - ", 1)` o taie la **ultimul**
  „ - ” în examen („NVO 7th grade”) și an. Funcția păstrează fișierele aceluiași examen și le
  sortează. Sortarea textului funcționează pentru că fiecare an începe cu cele 4 cifre ale lui.
- **Exemplu:** pentru „NVO 7th grade - 2025/2026” dă cele 8 alegeri de la
  „NVO 7th grade - 2018/2019” la „NVO 7th grade - 2025/2026”.
- **Apelată de:** `show_change()` și `show_trends()`.

#### `region_gaps(exam_files, choices, subject)`: [linia 978](alex_school_results.py#L978)
- **Într-o propoziție:** pentru fiecare dintre anii de examen dați, cât de departe este fiecare
  regiune de media națională din acel an.
- **Primește:** fișierele, o listă de alegeri (2 ani pentru schimbare, toți anii pentru tendințe) și
  materia. **Dă înapoi trei valori:** un tabel cu un rând pentru fiecare regiune și o coloană pentru
  fiecare an școlar, mediile naționale și cât de împrăștiate au fost rezultatele școlilor în fiecare
  an (`school_spread()`). `show_change()` nu are nevoie de a treia, așa că scrie `_` pentru ea.
- **Cum:**
  1. Pentru fiecare an, încarcă tabelul, lasă deoparte școlile din străinătate și calculează media
     națională și media fiecărei regiuni cu `subject_score()`, iar împrăștierea cu
     `school_spread()`.
  2. `pd.DataFrame(scores)` face tabelul: regiunile devin rânduri, iar anii devin coloane.
  3. `.sub(national, axis=1)` scade media națională a fiecărui an din toată coloana acelui an.
- **De ce media națională:** testul este diferit în fiecare an. Media națională de la clasa a 7-a a
  scăzut de la 49,33 la 46,87 într-un singur an, mai ales pentru că testul a fost mai greu, nu
  pentru că fiecare școală s-a înrăutățit. Distanța unei regiuni față de media națională anulează
  acest efect, așa că anii pot fi comparați.
- **Apelată de:** `show_change()` și `show_trends()`.

#### `show_change(exam_files, choice, subject)`: [linia 999](alex_school_results.py#L999)
- **Într-o propoziție:** face vederea „Change since the previous year”: cât s-a mișcat fiecare
  regiune față de media națională, comparativ cu anul dinainte.
- **Dă înapoi trei valori,** ca `show_map()`: rezumatul, harta și graficul cu bare.
- **Cum:**
  1. Găsește locul anului ales în `exam_years()`. Dacă este primul an, nu are cu ce compara, așa că
     întoarce un mesaj și `None` pentru cele două grafice.
  2. `region_gaps()` dă distanța fiecărei regiuni față de media națională în ambii ani.
  3. `.dropna()` păstrează doar regiunile cu rezultate în ambii ani. Schimbarea este „acum” minus
     „înainte”.
  4. Scrie rezumatul și desenează harta și barele cu `region_map()` și `region_bars()`, colorate
     după coloana „Change”.
- **Rezumatul:** cele 3 regiuni care s-au îmbunătățit cel mai mult și cele 3 care au rămas cel mai
  mult în urmă, **mișcarea tipică** (mediana schimbărilor, fără a ține cont de semnul lor) și cum
  s-a mișcat media Bulgariei însăși.
- **Exemplu:** НВО clasa a 7-a 2024/2025 → 2025/2026, ambele materii: cel mai mult s-a îmbunătățit
  ДОБРИЧ +2,14, cel mai mult a rămas în urmă ЯМБОЛ −4,99, mișcarea tipică a fost de 0,98 puncte.
- **Apelată de:** `map_view()` de pe pagină.

#### `show_trends(exam_files, choice, subject)`: [linia 1044](alex_school_results.py#L1044)
- **Într-o propoziție:** face vederea „Trends over the years”: distanța fiecărei regiuni față de
  media națională, în fiecare an al examenului ales.
- **Dă înapoi trei valori:** rezumatul, grila regiunilor și anilor (`trend_heatmap()`) și graficul
  cu linie al decalajului dintre cea mai bună și cea mai slabă regiune (`gap_trend_chart()`).
- **Cum:**
  1. `exam_years()` dă toți anii, iar `region_gaps()` tabelul distanțelor.
  2. Sortează regiunile după ultimul an. Plotly desenează primul rând jos, așa că cea mai bună
     regiune ajunge sus.
  3. `gaps.max() - gaps.min()` dă, pentru fiecare an (fiecare coloană), distanța celei mai bune
     regiuni minus distanța celei mai slabe: **decalajul dintre regiuni**.
  4. `spread / school_spreads` împarte decalajul fiecărui an la cât de împrăștiate au fost
     rezultatele școlilor în acel an (`school_spread()`). Aceasta este măsura mai corectă, iar
     `drift_words()` descrie în cuvinte schimbarea ei.
  5. Compară ultimul an al fiecărei regiuni cu primul, ca să afle cine a recuperat și cine a rămas
     în urmă. Rezumatul avertizează că se folosesc doar acești doi ani.
- **Exemplu:** НВО clasa a 7-a, ambele materii: decalajul a crescut de la 20,58 puncte în 2018/2019
  la 26,79 în 2025/2026 (+30%). Raportat la împrăștiere, a crescut de la 1,37 la 1,53 (+12%):
  regiunile chiar s-au îndepărtat unele de altele, dar mai puțin decât sugerează punctele. 20 de
  regiuni au fost sub media națională în fiecare an.
- **Apelată de:** `map_view()` de pe pagină.

#### `drift_words(change)`: [linia 1089](alex_school_results.py#L1089)
- **Într-o propoziție:** descrie în cuvinte schimbarea decalajului (raportat la împrăștiere):
  „the regions drifted apart” (regiunile s-au îndepărtat), „the regions came closer” (regiunile
  s-au apropiat) sau „about the same” (cam la fel).
- **Cum:** două `if`-uri. O schimbare mai mică de 0,05 în oricare direcție contează ca „about the
  same”, pentru că e prea mică pentru a însemna ceva.
- **Exemplu:** decalajul de la clasa a 10-a a crescut cu 1,07 puncte, dar raportat la împrăștiere a
  scăzut de la 1,28 la 1,21, așa că `drift_words(-0.07)` dă „the regions came closer”.
- **Apelată de:** `show_trends()`.

#### `trend_heatmap(gaps, unit)`: [linia 1101](alex_school_results.py#L1101)
- **Într-o propoziție:** desenează grila cu un rând pentru fiecare regiune și o coloană pentru
  fiecare an școlar, fiecare celulă fiind colorată după distanța regiunii față de media națională și
  având numărul scris în ea.
- **Cum:**
  1. `go.Heatmap(...)` este grila de celule colorate din Plotly, cu aceleași culori și aceeași
     scară ca harta (`colour_key()`).
  2. `texttemplate="%{text}"` scrie numărul fiecărei celule (de la `signed()`). Plotly alege text
     alb sau negru, ca să se poată citi pe celulele închise și pe cele deschise.
  3. `xgap=2, ygap=2` lasă un mic spațiu între celule. Anii sunt sus, scriși de `year_labels()`.
- **Apelată de:** `show_trends()`.

#### `gap_trend_chart(spread, relative, unit)`: [linia 1136](alex_school_results.py#L1136)
- **Într-o propoziție:** un grafic cu linie al decalajului dintre cea mai bună și cea mai slabă
  regiune, an de an. O linie care urcă înseamnă că regiunile se îndepărtează unele de altele.
- **Primește:** decalajele în puncte sau note (`spread`), aceleași decalaje împărțite la
  împrăștierea rezultatelor școlilor (`relative`) și unitatea de măsură.
- **Cum:**
  1. `go.Scatter(mode="lines+markers+text")` desenează o linie cu puncte. Doar primul și ultimul an
     au numărul scris, ca linia să rămână ușor de citit.
  2. Axa începe de la 0, ca urcarea liniei să nu fie exagerată, și merge cu 20% peste cel mai înalt
     punct, ca numărul lui să încapă.
  3. `customdata=relative.values` dă fiecărui punct un număr în plus, pe care îl arată fereastra
     care apare la trecerea mouse-ului: „Gap: 26.79 points = 1.53 times the spread of the schools'
     results” (decalajul = de câte ori împrăștierea rezultatelor școlilor).
- **Apelată de:** `show_trends()`.

---

### Grupa 7: Pagina web și pornirea

#### `build_page(exam_files, regions)`: [linia 1170](alex_school_results.py#L1170)
- **Într-o propoziție:** construiește pagina web (liste, butoane, file, tabele) și hotărăște ce
  funcție rulează când dai clic pe ceva sau schimbi ceva.
- **Primește:** dicționarul de fișiere și lista regiunilor. **Dă înapoi:** pagina, pe care `main()`
  o deschide apoi.
- **Cum:**
  1. Creează mici **funcții interioare**: `show`, `overview`, `refresh_towns`, `map_view`,
     `difference_view`, `change_view`, `trends_view` și `check_for_new_results`. Ele țin minte
     `exam_files`, așa că Gradio trebuie să le transmită doar alegerile tale.
  2. `with gr.Blocks(...) as page:` înseamnă că tot ce e indentat dedesubt devine parte a paginii.
     `gr.Row()` pune lucrurile unul lângă altul; `gr.Tabs()` și `gr.Tab()` fac cele trei file.
  3. **Culorile butoanelor,** cu CSS transmis în `gr.Blocks(css=...)`:
     - `elem_id="check-button"` dă butonului verde un nume, iar regula
       `#check-button { background: #1a7f37 … }` colorează doar acel buton. Textul alb pe acest verde
       are un contrast de 5,1:1, așa că se citește ușor.
     - `elem_classes="grey-button"` pune celelalte butoane într-un grup, iar regula `.grey-button`
       le face pe toate gri deschis (text închis pe `#e9e9e7`, un contrast de 13,6:1).
     - `gr.Tabs(elem_id="main-tabs")` dă un nume barei de file, iar încă două reguli fac numele celor
       trei file centrate, îngroșate (`font-weight: 700`) și cu două mărimi mai mari (`--text-xl`, 22px,
       în loc de obișnuitul `--text-md`, 14px). `flex-wrap: wrap` le lasă să treacă pe un al doilea rând
       într-o fereastră îngustă: altfel filele centrate ar fi tăiate în ambele părți.
  4. **`gr.State("difference")`** ține minte care dintre cele trei vederi ale hărții ai ales
     ultima. Nu se desenează pe pagină: este o mică memorie, câte una pentru fiecare vizitator.
  5. Leagă **evenimentele**: `thing.event(function, inputs, outputs)` înseamnă „când se întâmplă
     asta, apelează această funcție cu valorile acestor intrări și pune rezultatele ei în aceste
     ieșiri”. `.then(...)` înseamnă „după aceea, fă și asta”.

| Când tu… | Gradio apelează |
|---|---|
| deschizi pagina | `show()` |
| schimbi examenul sau regiunea | `refresh_towns()`, apoi `show()` |
| alegi o localitate sau schimbi „Rank schools by” | `show()` |
| apeși „Show results” sau Enter în căsuța de căutare | `show_schools_tab()`, apoi `show()` |
| apeși „Write AI overview” | trece la a doua filă, apoi `overview()` |
| deschizi fila „Map and trends of the regions”, schimbi examenul sau schimbi „Colour by” | `map_view()`, cu vederea aleasă ultima |
| apeși „Difference from Bulgaria”, „Change since the previous year” sau „Trends over the years” | `difference_view()`, `change_view()` sau `trends_view()`, care apelează `map_view()` |
| apeși butonul verde „Check for new results” | `check_for_new_results()` |

- **Funcțiile interioare** (create în interiorul lui `build_page()`):
  - `show(choice, region, town, search, rank_by)` apelează `show_results(exam_files, …)`.
  - `overview(choice, region)` apelează `write_overview(exam_files, …)`. `yield from` transmite
    mai departe fiecare actualizare, așa că și ea este un generator.
  - `refresh_towns(choice, region, current_town)` apelează `town_choices()` și întoarce o listă
    derulantă nouă, cu lista nouă. Îți păstrează localitatea dacă aceasta este încă în listă.
  - `map_view(choice, subject, view)` apelează `show_map()`, `show_change()` sau `show_trends()`,
    în funcție de vedere. Dă înapoi vederea (pentru `gr.State`), rezumatul, cele două grafice cu
    numele lor și cele trei butoane, cu o bifă „✓” pe cel ales. Harta se desenează când îi deschizi
    fila, pentru că un grafic desenat într-o filă ascunsă poate ieși de o mărime greșită.
  - `difference_view`, `change_view` și `trends_view` au câte o singură linie: apelează `map_view()`
    cu vederea lor. Un buton nu poate transmite un cuvânt fix unei funcții, așa că fiecare primește
    propria lui funcție mică.
  - `check_for_new_results(current_choice)` este și ea un generator:
    1. Mai întâi arată „Checking data.egov.bg…” (se verifică data.egov.bg), apoi apelează
       `update_database()`.
    2. Umple din nou dicționarul comun `exam_files` (`clear()`, apoi `update()`), ca fiecare parte
       a paginii să vadă anii noi.
    3. Întoarce noul rând „Data” (`database_status()`) și o listă nouă „Exam and school year”,
       păstrând alegerea ta curentă.
    4. Dacă verificarea eșuează, de exemplu fără internet, arată eroarea în schimb.
  - `show_schools_tab()` întoarce `gr.Tabs(selected="schools")`, ceea ce înseamnă „mergi la fila
    Schools”.
  - O `lambda` minusculă, o funcție de o singură linie fără nume, trece la a doua filă.
- **`.input` sau `.change`?**
  - `.input` reacționează doar la **tine**.
  - `.change` reacționează și când **codul** schimbă valoarea.
  - Lista de localități folosește `.input`, ca rezultatele să nu fie afișate de două ori când
    `refresh_towns()` resetează localitatea.

#### `main()`: [linia 1351](alex_school_results.py#L1351)
- **Într-o propoziție:** punctul de pornire: pregătește datele din baza de date, construiește pagina
  și o deschide în browserul tău.
- **Cum:**
  1. `sys.stdout.reconfigure(...)` permite terminalului din Windows să afișeze caractere chirilice.
  2. `stored_files()` citește lista fișierelor din baza de date.
  3. **Dacă baza de date este goală** (chiar prima pornire sau fișierul a fost șters),
     `update_database()` o umple de pe internet, o singură dată, în aproximativ un minut. Apoi din
     nou `stored_files()`.
  4. `read_results()` pe primul fișier, doar ca să adune numele regiunilor.
  5. `build_page()`.
  6. Dacă ceva nu merge, afișează un singur mesaj clar și se oprește cu `sys.exit(1)`. `1` este
     codul de „eroare”.
  7. Avertizează dacă lipsește un examen sau dacă AI-ul nu este gata (`ollama_problem()`).
  8. `page.launch(inbrowser=True)` pornește serverul web și îți deschide browserul.
- **Nu e nevoie de internet:** când baza de date are date, nu se descarcă nimic la pornire.
- **Ultimele două linii ale fișierului:** `if __name__ == "__main__": main()` înseamnă „rulează
  `main()` doar când acest fișier este **pornit** direct (`uv run …`), nu când alt fișier îl
  **importă**”. Datorită acestui lucru, poți încerca funcții separat (vezi sfaturile de mai jos).

---

## 6. Sfaturi pentru explorarea codului

- **Încearcă o funcție separat.** Rulează asta din folderul proiectului (`-X utf8` face ca
  terminalul să afișeze corect caracterele chirilice):
  ```
  uv run python -X utf8 -c "from education_bulgaria.alex_school_results import tidy_town, to_number; print(tidy_town('ГР. СОФИЯ'), to_number('3,09'), to_number(''))"
  ```
  Afișează: `ГР.СОФИЯ 3.09 None`
- **Uită-te în baza de date** cu o singură linie de SQL, din folderul proiectului:
  ```
  uv run python -X utf8 -c "import sqlite3; db = sqlite3.connect('education_bulgaria/school_results.db'); print(db.execute('SELECT choice, COUNT(*) FROM results GROUP BY choice ORDER BY choice LIMIT 3').fetchall())"
  ```
  Afișează primele 3 examene și ani cu numărul lor de școli, începând cu
  `('DZI (matura) - 2021/2022', 951)`. Dacă preferi să dai clic prin ea, deschide fișierul în
  programul gratuit [DB Browser for SQLite](https://sqlitebrowser.org).
- **Uită-te într-o funcție:** adaugă un `print(...)` ca să-i vezi valorile în timp ce rulează
  programul, apoi scoate-l.
- **Schimbă o setare:** de exemplu `TOP = 10` la începutul fișierului dă primele 10 în loc de primele
  5. Repornește programul ca să vezi schimbarea.
- **Citește în ordinea parcursurilor:** începe cu `main()`, apoi urmărește apelurile așa cum sunt
  arătate în secțiunea 4.
