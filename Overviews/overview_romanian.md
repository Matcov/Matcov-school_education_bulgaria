# Rezultatele examenelor școlare din Bulgaria: Prezentare generală a proiectului

Acest document descrie arhitectura, datele și funcționalitatea proiectului realizat în [alex_school_results.py](../alex_school_results.py), cu baza de date locală [school_results.db](../school_results.db) și arhiva pe școli din folderul [schools/](../schools/).

---

## 1. Rezumat scurt

* **Sursa oficială a datelor:** Rezultatele pe școli nu sunt publicate ca tabele în paginile web ale Ministerului Educației și Științei (МОН, `mon.bg`), ci ca seturi de date deschise pe **Portalul de date deschise al Republicii Bulgaria** ([data.egov.bg](https://data.egov.bg)).
* **Acoperire:** Proiectul cuprinde **4 seturi de date principale** (НВО — evaluarea națională externă — pentru clasele a 4-a, a 7-a și a 10-a, precum și ДЗИ — examenele de bacalaureat — pentru clasa a 12-a) cu **25 de fișiere anuale**, care conțin date despre **2.379 de școli** pentru perioada din anul școlar 2018/2019 până în 2025/2026.
* **Aplicația:** [alex_school_results.py](../alex_school_results.py) oferă un panou web interactiv (prin Gradio), care permite filtrarea, compararea, clasamente, o hartă a inegalității dintre regiuni, schimbarea ei de-a lungul anilor și o analiză AI a rezultatelor.
* **Baza de date locală:** Rezultatele sunt păstrate în baza SQLite [school_results.db](../school_results.db) (8,1 MB). Aplicația pornește în câteva secunde, funcționează fără internet și se conectează la site-urile guvernamentale doar la apăsarea butonului verde **„Caută rezultate noi”** (Verifică dacă există rezultate noi).
* **Arhiva școlilor:** Folderul [schools/](../schools/) conține câte un fișier CSV pentru fiecare școală, cu istoricul tuturor rezultatelor ei (instantaneu la data de 17 noiembrie 2026).

---

## 2. Surse de date și integrarea cu API-ul

> Site-urile guvernamentale sunt folosite doar pentru completarea și actualizarea bazei de date locale: la prima pornire (dacă baza este goală) și la apăsarea butonului verde **„Caută rezultate noi”**.

### Ministerul Educației și Științei (МОН)
1. Scriptul citește pagina oficială [mon.bg → Date deschise](https://www.mon.bg/mon/dostap-do-informatsiya/otvoreni-danni/) cu ajutorul `BeautifulSoup`.
2. Extrage linkul către profilul ministerului pe portalul național de date deschise (`organisation id 117`).
3. Paginile publice ale МОН conțin variante de examen model și grile de evaluare, în timp ce rezultatele individuale ale elevilor se află pe `infopriem.mon.bg` (ele cer un număr de înregistrare și un cod, de aceea nu sunt publice și nu sunt prelucrate).

### Portalul de date deschise (data.egov.bg)
Toate cererile se fac prin HTTP `POST` către adresa API `https://data.egov.bg/api/<method>`, cu un corp JSON:
* `getOrganisationDetails`: Obține identificatorul numeric intern al МОН.
* `listDatasets`: Enumeră seturile de date ale ministerului (100 de înregistrări pe pagină).
* `listResources`: Întoarce lista fișierelor (resurselor) pentru un anumit set de date.
* `getResourceData`: Descarcă conținutul fișierului ales sub formă de rânduri de tabel.

#### Seturile de date principale:
| Examen | Numele setului pe portal | Ani acoperiți | Scara de notare |
|---|---|---|---|
| **НВО clasa a 4-a** | Резултати по училища от националното външно оценяване за IV клас | 2020/21 – 2025/26 | Puncte (max. 100) |
| **НВО clasa a 7-a** | Резултати по училища от националното външно оценяване за VII клас | 2018/19 – 2025/26 | Puncte (max. 100) |
| **НВО clasa a 10-a** | Резултати по училища от националното външно оценяване за X клас | 2020/21 – 2025/26 | Puncte (max. 100) |
| **ДЗИ (bacalaureat)** | Резултати от държавните зрелостни изпити по училища и по предмети | 2021/22 – 2025/26 | Notă (de la 2.00 la 6.00) |

> **Notă despre ДЗИ:** Pentru fiecare an se alege doar sesiunea obișnuită (mai–iunie), cu examenele obligatorii (БЕЛ — limba și literatura bulgară — și al doilea ДЗИ obligatoriu / ДИППК).

---

## 3. Prelucrarea și normalizarea datelor

Fișierele primite de la portalul guvernamental conțin o serie de diferențe de formatare, pe care scriptul le normalizează automat:
* **Cheie unică pentru școală:** Numele școlilor se schimbă și se prescurtează de-a lungul anilor. Proiectul folosește **codul НЕИСПУО (codul administrativ)** ca singurul identificator unic sigur.
* **Formatarea codurilor:** Se elimină spațiile (de ex. `2 216 001` devine `2216001`), ca să se evite dublarea artificială a școlilor.
* **Normalizarea localităților:** Se unifică scrieri precum `ГР. СОФИЯ` și `ГР.СОФИЯ`, sectoarele Sofiei sunt reduse la `ГР.СОФИЯ`, iar școlile din străinătate sunt marcate în mod consecvent.
* **Note și numere:** Sunt tratate virgulele zecimale (`3,09` → `3.09`), celulele goale și zerourile atunci când nu s-a prezentat niciun elev.
* **Al doilea examen obligatoriu la ДЗИ:** Deoarece absolvenții dau materii diferite la al doilea examen, scriptul calculează o singură notă medie pentru al doilea ДЗИ, ponderată după numărul de elevi prezentați la fiecare materie.
* **Medii ponderate:** Mediile generale pentru orașe, regiuni și toată țara sunt calculate întotdeauna ca medii ponderate după numărul de elevi, și nu ca medie aritmetică a mediilor școlilor.

---

## 4. Baza de date locală (`school_results.db`)

* **Format:** SQLite — inclus în Python (fără instalări suplimentare). Toată baza este un singur fișier și poate fi interogată cu SQL.
* **Tabele:**
  * `files` — câte un rând pentru fiecare fișier cu rezultate, adică un examen într-un an școlar (25 de rânduri): examenul, anul școlar, tipul (`nvo` sau `dzi`), identificatorul fișierului pe data.egov.bg și data descărcării.
  * `results` — câte un rând pentru fiecare școală din fiecare fișier (35.292 de rânduri), deja curățate și normalizate.
  * `checks` — câte un rând pentru fiecare verificare a rezultatelor noi.
* **Viteză:** Pornirea durează aproximativ 1 secundă în loc de aproximativ 15, iar încărcarea unui examen și an — aproximativ 20 de milisecunde în loc de aproximativ 1 secundă.
* **Actualizare:** Butonul verde **„Caută rezultate noi”** verifică portalul (aproximativ 20 de secunde) și descarcă doar fișierele care lipsesc din bază sau pe care ministerul le-a înlocuit cu o versiune corectată. Fiecare fișier este scris într-o singură tranzacție, așa că o actualizare întreruptă nu lasă o jumătate de fișier.
* **Prima pornire:** Dacă baza lipsește sau este goală, aplicația o completează automat (aproximativ un minut).
* **Verificare:** Baza construită din toate cele 25 de fișiere este identică cu o nouă descărcare a fiecărui fișier — fiecare școală, număr, celulă goală și tip de coloană.

---

## 5. Funcționalitățile aplicației web (alex_school_results.py)

Interfața cu utilizatorul este construită cu **Gradio** (`gr.Blocks`) și oferă trei file. Deasupra lor se află un rând cu starea bazei de date (numărul de fișiere și data ultimei verificări) și butonul verde **„Caută rezultate noi”**. Toate celelalte butoane sunt gri-deschis, astfel încât butonul verde iese în evidență. Cele trei file sunt butoane verzi în mijlocul paginii; fila deschisă este mai închisă și subliniată.

### Fila „Școli”
* **Filtrare:** Alegerea examenului și a anului școlar, a regiunii și a localității (lista de orașe și sate se filtrează dinamic după regiunea aleasă).
* **Căutare:** Căutare după text liber pentru școală, oraș sau comună (în chirilică).
* **Sortare:** Clasament după БЕЛ sau după matematică / al doilea examen.
* **Statistici rezumative:** 
  * Media rezultatelor și numărul de elevi prezentați pentru filtrul ales.
  * Comparație directă a rezultatului mediu cu media regiunii respective și cu media țării.
  * Locul orașului ales printre toate localitățile din Bulgaria și din regiune (se aplică un prag pentru numărul minim de elevi: minimum 100 de elevi la nivel național și minimum 30 de elevi în cadrul unei regiuni).

### Fila „Top 5 localități și școli + prezentare AI”
* **Clasamentul primelor 5 localități și școli:** Calculat după media generală a celor două materii.
* **Generarea unei analize textuale structurate:** Cu ajutorul unui model de limbaj local în **Ollama** (`gemma4`).
* **Principiu de arhitectură:** *Calculele sunt făcute în întregime de codul programului, nu de modelul de limbaj.* Codul calculează diferențele față de medie („Față de media zonei”) și transmite modelului datele numerice gata calculate, pentru a preveni greșelile matematice și halucinațiile.
* **Variantă de rezervă fără AI:** Dacă Ollama nu funcționează, modelul nu este descărcat sau apare o eroare în timpul scrierii, programul scrie singur rezumatul din aceleași numere — instantaneu, cu o notă care explică de ce.

### Fila „Harta și tendințele regiunilor”
* **Comparație întotdeauna față de media țării:** Astfel se neutralizează diferența de dificultate a testelor de la an la an, iar anii pot fi comparați corect.
* **Trei vizualizări, comutate cu trei butoane gri-deschis:**
  * **„Diferența față de Bulgaria”:** O hartă a celor 28 de regiuni, colorate după abaterea de la media țării: de la roșu închis (mult sub medie), prin galben (în jurul mediei), până la verde deschis (mult peste medie). Lângă ea se află o diagramă cu bare cu diferența exactă a fiecărei regiuni și un rezumat al diferențelor: cea mai bună regiune față de cea mai slabă, și orașele față de sate.
  * **„Schimbarea față de anul precedent”:** Aceeași hartă și diagramă, colorate după cât de mult s-a schimbat abaterea fiecărei regiuni de la media țării față de anul precedent. Rezumatul indică regiunile cu cea mai mare îmbunătățire și cu cea mai mare rămânere în urmă, precum și schimbarea tipică (mediana), pentru că schimbările mici sunt adesea fluctuații întâmplătoare.
  * **„Tendințele de-a lungul anilor”:** Un tabel cu celule colorate (câte un rând pentru fiecare regiune și câte o coloană pentru fiecare an) cu abaterea regiunii de la media țării, și o diagramă cu linii a decalajului dintre cea mai bună și cea mai slabă regiune. De exemplu, la clasa a 7-a acest decalaj crește de la 20,58 puncte (2018/19) la 26,79 puncte (2025/26).
    * În unii ani testul îi împrăștie mai mult pe elevi, iar asta, în sine, mărește decalajul. De aceea rezumatul compară decalajul și cu împrăștierea rezultatelor școlilor în același an (abaterea standard). După această măsură, decalajul la clasa a 7-a crește cu 12%, nu cu 30%, și doar până în 2021/22. La clasa a 10-a regiunile chiar se apropie ușor între ele.
* **Culorile devin tot mai deschise** pe măsură ce rezultatele se îmbunătățesc, astfel încât toate cele trei vizualizări pot fi citite și de persoanele cu daltonism, și în alb-negru.
* **Notă sub hartă:** culorile arată diferențe în rezultate, nu calitatea școlilor.
* **Granițele regiunilor:** Natural Earth (domeniu public), în fișierul [bulgaria_regions.geojson](../bulgaria_regions.geojson).

### Patru limbi
* **Butoanele albastre EN BG RU RO** de lângă titlu schimbă toată pagina: etichetele, rezumatele, diagramele și prezentarea AI. Versiunea bulgară se deschide la adresa principală (`http://127.0.0.1:7860`), iar cea engleză, rusă și română la `/en`, `/ru` și `/ro`.
* **Toate textele sunt într-un singur fișier,** [translations.py](../translations.py): 137 de texte, fiecare în cele 4 limbi. La pornire, aplicația verifică să nu lipsească nicio traducere.
* **Calculele sunt aceleași în fiecare limbă:** listele arată etichete traduse, dar transmit codului aceleași valori în engleză.
* **Rămân neschimbate:** numele școlilor, localităților și regiunilor (așa cum le scrie ministerul) și punctul zecimal (55.28). Numerele întregi au, în afara versiunii engleze, un spațiu între mii (53 739).

---

## 6. Structura folderului `schools/`

* **2.379 de fișiere CSV individuale:** Formatul numelor este `<име на училище> - <град> (<код>).csv` (numele școlii - oraș (cod)).
* **Fișier-index:** `_all_schools.csv` conține lista tuturor școlilor, cu codurile, regiunile, orașele lor și numărul de rezultate disponibile de-a lungul anilor.
* **Codificare:** Fișierele sunt salvate în `UTF-8 with BOM`, ceea ce asigură deschiderea fără probleme a chirilicei în Microsoft Excel.
* **Instantaneu:** Fișierele reflectă datele la 17 noiembrie 2026. Copia actuală, care se actualizează, este baza de date `school_results.db`.

---

## 7. Pornirea proiectului

### Cerințe:
1. Managerul de pachete Python `uv` instalat (sau bibliotecile din [requirements.txt](../requirements.txt): `gradio`, `pandas`, `plotly`, `requests`, `beautifulsoup4`, `ollama`).
2. (Opțional, pentru analiza AI) **Ollama** pornit, cu un model descărcat. Fără el, programul scrie singur un rezumat mai simplu.
   ```bash
   ollama pull gemma4
   ```

### Comanda de rulare:
Din directorul principal al proiectului:
```bash
uv run education_bulgaria/alex_school_results.py
```
Dintr-o copie descărcată a depozitului de pe GitHub:
```bash
python alex_school_results.py
```
Aplicația pornește în câteva secunde din baza de date și se deschide automat în browser (de obicei la adresa `http://127.0.0.1:7860`). Pentru a lucra cu ea nu este nevoie de internet — acesta este necesar doar pentru butonul **„Caută rezultate noi”**.
