# Audio Multi-Source Organizer (AMSO)

<!-- lang-nav:start -->
<p align="right">
  <a href="../../README.fr.md">Français</a> • <a href="../../README.md">English</a> • <a href="README.es.md">Español</a> • <a href="README.de.md">Deutsch</a> • <a href="README.it.md">Italiano</a> • <a href="README.pt.md">Português</a> • <a href="README.zh_cn.md">简体中文</a> • <a href="README.ja.md">日本語</a> • <a href="README.ru.md">Русский</a> • <a href="README.ar.md">العربية</a>
</p>
<details open>
<summary>🌐 Other languages / Autres langues (33)</summary>
<p align="right">
  <a href="README.pl.md">Polski</a> • <a href="README.tr.md">Türkçe</a> • <a href="README.nl.md">Nederlands</a> • <a href="README.sv.md">Svenska</a> • <a href="README.id.md">Bahasa Indonesia</a> • <a href="README.bg.md">Български</a> • <a href="README.sr.md">Српски</a> • <a href="README.be.md">Беларуская</a> • <b>Ελληνικά</b> • <a href="README.ca.md">Català</a> • <a href="README.eu.md">Euskara</a> • <a href="README.gl.md">Galego</a> • <a href="README.cs.md">Čeština</a> • <a href="README.sk.md">Slovenčina</a> • <a href="README.hu.md">Magyar</a> • <a href="README.hr.md">Hrvatski</a> • <a href="README.sl.md">Slovenščina</a> • <a href="README.bs.md">Bosanski</a> • <a href="README.et.md">Eesti</a> • <a href="README.lv.md">Latviešu</a> • <a href="README.lt.md">Lietuvių</a> • <a href="README.no.md">Norsk</a> • <a href="README.da.md">Dansk</a> • <a href="README.fi.md">Suomi</a> • <a href="README.is.md">Íslenska</a> • <a href="README.ms.md">Bahasa Melayu</a> • <a href="README.tl.md">Tagalog</a> • <a href="README.sw.md">Kiswahili</a> • <a href="README.eo.md">Esperanto</a> • <a href="README.zh_tw.md">繁體中文</a> • <a href="README.ko.md">한국어</a> • <a href="README.he.md">עברית</a> • <a href="README.vi.md">Tiếng Việt</a>
</p>
</details>
<!-- lang-nav:end -->

[![CI Tests](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/LEF97/Audio-Multi-Source-Organizer/actions)
[![Release](https://img.shields.io/github/v/release/LEF97/Audio-Multi-Source-Organizer?include_prereleases&color=orange)](https://github.com/LEF97/Audio-Multi-Source-Organizer/releases)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-blue.svg)](../../CHANGELOG.md)
[![Roadmap](https://img.shields.io/badge/Roadmap-Jalons%20futurs-purple.svg)](../../ROADMAP.md)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **AMSO** (Audio Multi-Source Organizer) είναι ένα σύγχρονο, διαδραστικό και multiplateforme πρόγραμμα αναπαραγωγής ήχου για desktop (Windows, Linux, macOS). Σχεδιασμένο για να προσφέρει στους λάτρεις του ήχου (audiophiles) πλήρη έλεγχο της τοπικής μουσικής βιβλιοθήκης τους (MP3, FLAC, OGG…), υποστηρίζει πλέον плейλίστες (M3U, PLS, XSPF, WPL), αρχεία CUE (αλμπουμ ενός αρχείου που χωρίζονται σε κομμάτια) και ενσωματώνει μια εντελώς νέα λειτουργία blind test ήχου! Το έργο εξελίσσεται για να γίνει ένα ενιαίο κέντρο διαχείρισης ικανό να οργανώνει, να αφαιρεί διπλότυπα και να συγχρονίζει υβριδικές μουσικές συλλογές που διανέμονται μεταξύ τοπικών δίσκων, cloud αποθήκευσης (Google Drive) και υπηρεσιών streaming (Spotify, Deezer, Amazon Music).

---

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0%2002.png" alt="Audio Multi-Source Organizer (AMSO) - Arborescence par dossiers & feuille CUE 💿 (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-25%20v0.4.0.png" alt="Audio Multi-Source Organizer (AMSO) - Liste de lecture d'une feuille CUE (pistes virtuelles)" width="850">
</p>

<p align="center">
  <img src="../../screenshots/2026-10-18%20v0.3.0%20blind%20test.png" alt="Audio Multi-Source Organizer (AMSO) - Mini-jeu Blind Test & Décompte dynamique" width="850">
</p>

---

## 📌 Χαρακτηριστικά & Κατάσταση του έργου

| Χαρακτηριστικό | Περιγραφή | Κατάσταση |
| :--- | :---: | :---: |
| **Ενσωματωμένος κινητήρας αναπαραγωγής VLC** | Ελαφρύ και αυτόνομο audio player με αυτόματη εγκατάσταση VLC portable και ομαλή διαχείριση του όγκου | 🟢 Υλοποιημένο |
| **Πολυματις τοπικός σαρωτής** | Αναδρομική και γρήγορη ανακάλυψη τοπικών audio αρχείων (MP3, FLAC, AAC, OGG...) | 🟢 Υλοποιημένο |
| **Εξαγωγή μεταδεδομένων** | Ανάγνωση/εγγραφή ID3, Vorbis Comments και υπολογισμός ακουστικής εντύπωσης (`mutagen`) | 🟢 Υλοποιημένο |
| **Υποστήριξη Playlists (M3U, PLS, XSPF, WPL) & φύλλα CUE** | Δένδρωση (🎶), σειριακή σειρά εκκίνησης, οπτική ανίχνευση λείπουν κομματιών; τα αρχεία `.cue` (💿) ανοίγουν ως φάκελος εικονικών κομματιών με τη διάρκεια τους και αναπαράγονται ως πραγματικά κομμάτια | 🟢 Υλοποιημένο |
| **Διαχειριστής Playlist & Σύστημα Drag & Drop** | Εικονική λίστα αναμονής, ομαλό drag & drop, αναστρέψιμο τυχαίο (shuffle) και βρόχοι | 🟢 Υλοποιημένο |
| **Διαδραστική λειτουργία « 🎲 Blind Test »** | Ενυπάρχμαστο μουσικό παιχνίδι με κινούμενη μετρητική, ήπια φθορά ήχου, απαλή αποκάλυψη και αυτόματη συνέχεια | 🟢 Υλοποιημένο |
| **Ενημερώσεις εντός εφαρμογής** | Αυτόματη/ε χειροκίνητη επαλήθευση εκδόσεων μέσω GitHub Releases | 🟢 Υλοποιήθηκε |
| **Διαχείριση καλλιτεχνών & Δισκογραφία** | Ιστοσελίδα αφιερωμένη σε καλλιτέχνη με άλμπουμ, singles και πλήρη δισκογραφία | 🟡 Σχεδιασμένο |
| **Γραφικό εξισορροπωτής (EQ)** | Ηχητικά presets και παραμετρικός πολυζώνης εξισορροπωτής | 🟡 Σχεδιασμένο |
| **Συνδέτης Google Drive** | Σάρωση και συγχρονισμός απομακρυσμένων ήχου συλλογών μέσω OAuth 2.0 | ⚪ Σχεδιαστεί |
| **Συνδέτης Amazon Music** | Σάρωση και συγχρονισμός απομακρυσμένων συλλογών μέσω OAuth 2.0 | ⚪ Σχεδιαστεί |
| **Συνδέτης Spotify / Deezer** | Εισαγωγή плейลิστες και αντιστοίχιση κομματιών | ⚪ Σχεδιαστεί |
| **Έξυπνη αφαιροποίηση διπλότυπων** | Ανίχνευση διπλότυπων (ατίτλος/τεμάニア + ακουστικές αποτυπώσεις) | ⚪ Σχεδιαστεί |

> 💡 *Για να δείτε τα λεπτομέरिया των προγραμματισμένων ορόσημων και εκδόσεων, ανατρέξτε στο [Feuille de route (Roadmap)](../../ROADMAP.md).*

---

## 📌 Διαθέσιμες γλώσσες

Αγγλικά, Γαλλικά, Ισπανικά, Γερμανικά, Ιταλικά, Πορτογαλικά, Ιαπωνικά, Ρωσικά, Πολωνικά, Τουρκικά, Ολλανδικά, Σουεδικά, Ινδονησιακά, Βουλγαρικά, Σέρβικά, Βεларуτικά, Ελληνικά, Καταλανικά, Βασκάνικη, Γαลิκικά, Τσεχικά, Σλοβακικά, Ουγγρικά, Κροατικά, Σλοβεννικά, Βοσνιακά, Estoniana, Λατビアτικά, Λιθουανικά, Νορβηγικά, Δανικά, Φινλανδικά, Ισλανδικά, Μαλαισικά, Ταγαλοέ, Σβαχίλί, Εσπεրանτο, Απλοποιημένα Κινεζικά, Παραδοσιακά Κινεζικά, Κορεατικά, Αραβικά, Εβραϊκά, Βιετναμέζικά

---

## 🚀 Γρήγορη εκκίνηση

### Προαπαιτούμενα

- **Python 3.11** ή υψηλότερο εγκατεστημένο
- Git

### Εγκατάσταση

```bash
# 1. Cloner le dépôt
git clone https://github.com/LEF97/Audio-Multi-Source-Organizer.git
cd audio-multi-source-organizer

# 2. Créer l'environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
# Sous Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sous Linux / macOS :
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# Pour le développement et les tests :
pip install -e .[dev]

# 5. Configurer les variables d'environnement
cp .env.example .env

# 6. Lancer l'application
python main.py
```

---

## 🧪 Έναρξη των δοκιμών

Το έργο χρησιμοποιεί `pytest` με ένα σύνολο δοκιμών μονάδων και ενσωμάτωσης:

```bash
pytest -v
```

Οι δοκιμές εκτελούνται αυτόματα σε **Windows, macOS και Ubuntu** με κάθε push μέσω GitHub Actions.

---

## 🔒 Ασφάλεια & Κλειδιά API

- **Μην commit ποτέ πραγματικούς κλειδιά API ή tokens प्रमाणीποίησης.**
- Το αρχείο `.gitignore` είναι προ-ρυθμισμένο για να μπλοκάρει το `.env`, `credentials.json`, `token.json` και όλες τις τοπικές βάσεις δεδομένων SQLite.
- Χρησιμοποιήστε το `.env.example` ως πρότυπο για το περιβάλλον ανάπτυξής σας.

---

## 📋 Τεκμηρίωση & Παρακολούθηση του έργου

- 📜 **[CHANGELOG.fr.md](../../CHANGELOG.md)** : Αναλυτικό καταχώρισμα εκδόσεων, νέων λειτουργιών και διορθώσεων σφαλμάτων.
- 🗺️ **[ROADMAP.fr.md](../../ROADMAP.md)** : Χάρτης πορείας των μελλοντικών ορόσημων (Καλλιτέχνες, Cloud, Spotify, Αποδιπλωτοποίηση).
- 📐 **[CODE_QUALITY.md](../../CODE_QUALITY.md)** : Χάρτα αρχιτεκτονικής λογισμικού και κανόνες ποιότητας κώδικα.

---

## 💖 Υποστήριξη του έργου & Διανομή

AMSO είναι ένα δωρεάν και ελεύθερο λογισμικό (open source). Εάν εκτιμάτε την εφαρμογή και θέλετε να ενισχύσετε την ανάπτυξή της:

- 🎮 **Λήψη & Πληρώστε όσο θέλετε :** [Page Itch.io d'AMSO](https://lef97.itch.io/audio-multi-source-organizer) (προεγκατεστημένο εκτελέσιμο έτοιμο προς χρήση)
- ☕ **Κάντε μια άμερη δωρεά :** [Ko-fi (@lef97)](https://ko-fi.com/lef97)
- ⭐ **GitHub Sponsors :** [Σπονσοράρετε το LEF97](https://github.com/sponsors/LEF97)

---

## 📄 Άδεια

Αυτό το έργο είναι υπό άδεια **GNU General Public License v3.0 (GPL-3.0)** — ρισκατε το αρχείο [LICENSE](../../LICENSE) για περισσότερες λεπτομέρειες.
