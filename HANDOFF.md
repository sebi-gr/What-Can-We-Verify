# Handoff: What Can We Verify?

Stand: 2026-09-23. Grundlage: zugänglicher Projektkontext, Research Map/Arbeitsentwurf, bisheriger GitHub-Abgleich und aktueller lokaler Git-/Code-/Datenstand. Keine endgültige RQ-Fassung oder vollständige Paper-Spezifikation im Repo vorhanden.

Der aktuelle Arbeitsplan steht verbindlich in [WORKPLAN.md](WORKPLAN.md). Zu Sessionbeginn mitlesen und nach Fortschritt oder Planänderungen laufend aktuell halten, auch bei einem spontanen Handoff. Diese Datei dokumentiert den überprüften Übergabestand.

## Ziel und Arbeitsfragen

LLM-Security-Findings in einzelne prüfbare Aussagen zerlegen und untersuchen, welche unabhängige Evidenz diese Aussagen trägt. Arbeitsfragen aus dem Forschungsentwurf, noch keine final verabschiedeten Paper-RQs:

- **RQ-A:** Welche wiederkehrenden Claim-Typen enthalten LLM-generierte Security-Findings?
- **RQ-B:** Welche unabhängigen Evidenzformen eignen sich je Claim-Typ?
- **RQ-C:** Wie unterscheiden sich ausgewählte Verifikationsverfahren hinsichtlich Korrektheit, Abdeckung, unentscheidbarer Fälle und Prüfaufwand?

Zielpipeline: bekannter verwundbarer Code → LLM/Security-Report → Claim-Zerlegung → claimbezogene Prüfung durch Codeanalyse, Konfiguration oder Ausführung.

## Festgelegte Leitlinien und umgesetzte Entscheidungen

- **KISS** gemäß `AGENTS.md`: Forschungsprototyp für die RQs, kleine nachvollziehbare Schritte.
- Einstieg **VUL4J-18 / Apache JSPWiki / CVE-2019-0225 / CWE-22 (Path Traversal)**.
- Zunächst `localized_review` mit fünf vollständigen Originaldateien: überschaubarer, fixierter Kontext. Daraus keine Erkennungsleistung für ganze Repositories ableiten.
- Modellkontext und Referenzmaterial getrennt halten, damit Fix/PoV/Benchmarkantworten das Review nicht vorgeben.
- Claim-Extraktion erfasst, was der Report behauptet; sie bestätigt keine Wahrheit. Ein zweiter LLM-Aufruf ist dafür sinnvoll, aber keine unabhängige Verifikation. Auch dasselbe Modell in frischem Kontext ist möglich.
- Arbeitskategorien: Location, Data-flow, Protection/precondition, Exploitability/impact. Ausnutzbarkeit und Wirkung bei getrennten Behauptungen einzeln extrahieren. Das Schema ist noch keine validierte Taxonomie.

## Tatsächlicher Repo-Stand

- **Korrigierte Dokumentationsabweichung (23.09.2026):** Beim Sessionstart war `main` auf `3a4eb9e` mit sauberem Arbeitsbaum ausgecheckt. Der lokale Merge-Commit belegt die Integration von [PR #1](https://github.com/sebi-gr/What-Can-We-Verify/pull/1); die bisherigen Angaben „PR offen“ und „Implementierung nicht auf main“ waren veraltet. `origin/main` zeigte lokal denselben Stand; kein erneuter Remote-Abgleich.
- Implementierung der Vorbereitung: `224f248`; letzte bisherige Plan-/Übergabedokumentation: `0d9d93f`.
- Für Schritt 2 wurde der lokale Branch `finding-generator` von `3a4eb9e` angelegt. `generate_findings.py` und `review_prompt_v1.txt` sind implementiert und offline geprüft; Änderungen bisher lokal und uncommitted. Vorläufiger Aufrufweg: OpenAI Responses; **Planabweichung:** Umsetzung vor endgültiger Anbieter-/Modell-/Budgetauswahl (siehe WORKPLAN). Noch kein echter Modellaufruf ausgeführt.

| Vorhanden | Verhalten |
|---|---|
| `prepare_case.py` | Python-CLI, Standardbibliothek; lädt fixierte Quellen, prüft die Dataset-Zeile, verweigert vorhandene Ziele und veröffentlicht erst die vollständige Ausgabe. |
| `model_input/` (generiert) | WikiServlet, DefaultURLConstructor, URLConstructor, jspwiki.properties und web.xml, unveränderte Bytes/Pfade/Zeilennummern. |
| `reference/` (generiert) | Dataset-Zeile, gefixter Constructor, WikiServletTest-PoV, LICENSE und NOTICE. |
| `manifest.json` (generiert) | Quellrevisionen, URLs, SHA-256-Hashes und `pov_status: not_run`. |
| `test_prepare_case.py`, `README.md` | Drei Offline-Tests; Bedienung, Provenienz und Grenzen. |
| `generate_findings.py`, `review_prompt_v1.txt` | Ein OpenAI-Responses-Aufruf ohne Tools/Retry; fünf erlaubte Dateien, gespeicherte Originalbytes, Request, Rohantwort, Findings und Laufmanifest. Modell/Tokenlimit sind Pflichtargumente. |
| `test_generate_findings.py` | Sieben synthetische Offline-Tests zu Kontexttrennung, Byte-/Texterhalt, leeren/ungültigen Ausgaben, Fehlern, Überschreibschutz und Symlinks. |

Standardausgabe: `data/VUL4J-18/`, durch Git ignoriert. Fixierte Dataset-/Fall-/Fix-Revisionen stehen in `prepare_case.py` und `README.md`. Ein frischer Clone enthält keine generierten Falldaten.
**Noch nicht implementiert:** Claim-Decomposer, Claim-Validierung, Annotation und Verifikatoren. Ein echter Review-Lauf fehlt; Schritt 2 ist deshalb noch nicht abgeschlossen.

## Prüfstand und Grenzen

- **Beim ersten Handoff (23.09.2026) geprüft:** Python-Dateien stimmen bytegenau mit GitHub-Stand `c0e5eb2` überein; `python3 -m unittest -v`: 3/3 bestanden. Dokumentationsdiff ohne Whitespace-Fehler. Bei der anschließenden WORKPLAN-Ergänzung nur Dokumentation geprüft; Python-Tests nicht erneut ausgeführt.
- **Aktuelle Session (23.09.2026):** Vorbereitungsimplementierung und Tests vollständig gelesen; 3/3 Offline-Tests und `git diff --check` bestanden. Die neun vorhandenen Quelldateien stimmen mit ihren lokalen Manifest-Hashes überein; kein neuer Download-/Upstream-Abgleich. Fünf Modelldateien vorhanden, keine Treffer für `CVE-` oder `VUL4J` darin. Die üblichen API-Key-Umgebungsvariablen sind nicht gesetzt (nur Vorhandensein geprüft, keine Zugangsdaten gelesen).
- **Nach Generatorimplementierung:** `python3 -m unittest -v`: 10/10 bestanden; `git diff --check` ohne Befund. CLI-Hilfe und UTF-8-Lesbarkeit der fünf echten Modelldateien geprüft (71.907 Originalbytes). Rohantworten bleiben bytegleich, Titel/Reports unverändert; Refusal, unvollständige Antworten und Formatfehler werden nicht als Null-Ergebnis behandelt. Vorhandene Laufverzeichnisse bleiben erhalten. Kein Netzzugriff in den Tests, keine Live-API-Kompatibilität nachgewiesen. Das Ausgabetokenlimit ist kein Geldbudget; Tokenusage wird übernommen, Kosten bleiben unbekannt (`null`).
- **Zuvor ausgeführt, in PR #1 dokumentiert:** echter Vorbereitungslauf; alle neun heruntergeladenen Datei-Hashes geprüft; verwundbarer Constructor bytegleich mit Upstream-Fix-Parent; Fix/PoV-Testmethoden inspiziert; `git diff --check` bestanden. Downloadlauf bei dieser Übergabe nicht wiederholt.
- **Nicht ausgeführt:** Java-Build und PoV an verwundbarer/gefixter Version. Es liegt nur ein Quelltextausschnitt vor, kein ausführbares JSPWiki-Checkout.
- Der PoV prüft Forwarding-URLs mit Servlet-Mocks. Daraus folgt allein kein Nachweis beliebiger Dateizugriffe oder unauthentifizierter Ausnutzbarkeit.
- Fehlende Filter, andere URL-Constructor, WikiEngine und reale Deployment-Konfiguration begrenzen Aussagen. Quellkonfiguration ist kein Beleg für ein laufendes Deployment.
- Der Snapshot kann Benchmark-Anpassungen enthalten. Modellvorwissen über die CVE ist trotz getrennter Referenzen möglich. Keine empirischen Claim-Ergebnisse vorhanden.

## Nächster Schritt und offene Planung

Weiter mit **Schritt 2 in [WORKPLAN.md](WORKPLAN.md)**: Anbieter-/Modell-/Budgetauswahl abschließen und mit verfügbarem API-Key einen nachvollziehbaren echten Review-Lauf speichern. Generator und Prompt sind vorbereitet, der echte Lauf ist mangels Auswahl/API-Zugang offen. Keine synthetische Testantwort als Finding verwenden. Die separate PoV-Reproduktion (Schritt 1b) ist weiterhin unerledigt.

WORKPLAN.md enthält den aus dem Arbeitsentwurf übernommenen Ablauf, Abschlusskriterien, Prompt-/Schemaentwürfe und die ausdrücklich als Vorschläge markierten Pilot- und Verifikationsoptionen. Die endgültige RQ-Fassung, Taxonomie und Evaluationsplanung sind noch nicht beschlossen.
