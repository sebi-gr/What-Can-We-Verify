# Handoff: What Can We Verify?

Stand: 2026-09-23. Grundlage: zugänglicher Projektkontext, Research Map/Arbeitsentwurf und aktuell gelesene GitHub-Dateien. Keine endgültige RQ-Fassung oder vollständige Paper-Spezifikation im Repo vorhanden.

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

- Implementierungsbranch: `prepare-vul4j-18`; [PR #1](https://github.com/sebi-gr/What-Can-We-Verify/pull/1) offen, nicht gemergt (am Stichtag).
- Implementierung: `224f248856572e9fc980a616347e5d16f068182b`; README-Änderung: `c0e5eb23520e6ce95ad8faed06d1ef7a9ba6b901`; zuletzt geprüfter Stand vor der Arbeitsplan-Ergänzung: `8894dabb04abf442f5e62d678370756d092b5f8a` (erste Übergabedateien).
- `main` steht noch auf `04baf6af5c2cd416e93f31fbf3b5003b53b44265` und enthält die Implementierung nicht.
- Aktuelle Dokumentationsänderung: Arbeitsentwurf in `WORKPLAN.md` überführt und Pflegepflicht in `AGENTS.md`/`HANDOFF.md` verankert; Code unverändert. Aktuellen Dokumentationscommit mit `git log -1 -- AGENTS.md HANDOFF.md WORKPLAN.md` ermitteln.

| Vorhanden | Verhalten |
|---|---|
| `prepare_case.py` | Python-CLI, Standardbibliothek; lädt fixierte Quellen, prüft die Dataset-Zeile, verweigert vorhandene Ziele und veröffentlicht erst die vollständige Ausgabe. |
| `model_input/` (generiert) | WikiServlet, DefaultURLConstructor, URLConstructor, jspwiki.properties und web.xml, unveränderte Bytes/Pfade/Zeilennummern. |
| `reference/` (generiert) | Dataset-Zeile, gefixter Constructor, WikiServletTest-PoV, LICENSE und NOTICE. |
| `manifest.json` (generiert) | Quellrevisionen, URLs, SHA-256-Hashes und `pov_status: not_run`. |
| `test_prepare_case.py`, `README.md` | Drei Offline-Tests; Bedienung, Provenienz und Grenzen. |

Standardausgabe: `data/VUL4J-18/`, durch Git ignoriert. Fixierte Dataset-/Fall-/Fix-Revisionen stehen in `prepare_case.py` und `README.md`. Ein frischer Clone enthält keine generierten Falldaten.
**Nicht implementiert:** Finding-Generator, Modellaufrufe, Claim-Decomposer, Claim-Validierung, Annotation und Verifikatoren.

## Prüfstand und Grenzen

- **Beim ersten Handoff (23.09.2026) geprüft:** Python-Dateien stimmen bytegenau mit GitHub-Stand `c0e5eb2` überein; `python3 -m unittest -v`: 3/3 bestanden. Dokumentationsdiff ohne Whitespace-Fehler. Bei der anschließenden WORKPLAN-Ergänzung nur Dokumentation geprüft; Python-Tests nicht erneut ausgeführt.
- **Zuvor ausgeführt, in PR #1 dokumentiert:** echter Vorbereitungslauf; alle neun heruntergeladenen Datei-Hashes geprüft; verwundbarer Constructor bytegleich mit Upstream-Fix-Parent; Fix/PoV-Testmethoden inspiziert; `git diff --check` bestanden. Downloadlauf bei dieser Übergabe nicht wiederholt.
- **Nicht ausgeführt:** Java-Build und PoV an verwundbarer/gefixter Version. Es liegt nur ein Quelltextausschnitt vor, kein ausführbares JSPWiki-Checkout.
- Der PoV prüft Forwarding-URLs mit Servlet-Mocks. Daraus folgt allein kein Nachweis beliebiger Dateizugriffe oder unauthentifizierter Ausnutzbarkeit.
- Fehlende Filter, andere URL-Constructor, WikiEngine und reale Deployment-Konfiguration begrenzen Aussagen. Quellkonfiguration ist kein Beleg für ein laufendes Deployment.
- Der Snapshot kann Benchmark-Anpassungen enthalten. Modellvorwissen über die CVE ist trotz getrennter Referenzen möglich. Keine empirischen Claim-Ergebnisse vorhanden.

## Nächster Schritt und offene Planung

Weiter mit **Schritt 2 in [WORKPLAN.md](WORKPLAN.md)**: einen minimalen Finding-Generator ergänzen und einen nachvollziehbaren Review-Lauf speichern. Anbieter, Modell und Budget sind offen. Die separate PoV-Reproduktion (Schritt 1b) ist weiterhin unerledigt.

WORKPLAN.md enthält den aus dem Arbeitsentwurf übernommenen Ablauf, Abschlusskriterien, Prompt-/Schemaentwürfe und die ausdrücklich als Vorschläge markierten Pilot- und Verifikationsoptionen. Die endgültige RQ-Fassung, Taxonomie und Evaluationsplanung sind noch nicht beschlossen.
