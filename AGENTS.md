# Entwicklungsregeln

- Zu Beginn jeder Session zuerst `HANDOFF.md` lesen, danach `README.md` und den tatsächlichen Git-Stand prüfen. Veraltete Angaben als solche korrigieren.
- `HANDOFF.md` nach relevanten Entscheidungen, Änderungen und Prüfungen laufend aktualisieren, nicht erst am Sessionende. Auch bei einem spontanen Handoff müssen Stand, offene Punkte und nächster Schritt nachvollziehbar sein. Beschlüsse, Vorschläge und ungeprüfte Annahmen getrennt halten.
- **KISS:** Wir bauen einen kleinen Forschungsprototyp, um die Paper-RQs zu evaluieren und zu beantworten. Keine komplexe OSS-Plattform und kein Overengineering.
- Kleine, lesbare Skripte und explizite Ein-/Ausgaben bevorzugen. Minimal, aber verständlich: keine versteckte Logik oder komplizierten Abkürzungen, nur um Code zu verkürzen.
- Komponenten, Abhängigkeiten und Abstraktionen nur hinzufügen, wenn der nächste konkrete Versuch sie braucht. Keine vorsorglichen Frameworks, Plugin-Systeme oder allgemeinen Pipeline-Engines.
- Nur den beauftragten Schritt umsetzen. Bestehende Änderungen erhalten; keine beiläufigen Refactorings.
- LLM-Claim-Extraktion ist keine Wahrheitsprüfung. Modellübereinstimmung zählt nicht als unabhängige Evidenz. Originalaussagen, Unsicherheit, Negation und Voraussetzungen erhalten.
- Referenzmaterial, Fix, PoV und Fallmanifest aus dem Finding-Generator-Kontext ausschließen. Bei Agenten den tatsächlichen Toolzugriff begrenzen; getrennte Ordner allein reichen nicht.
- Reproduzierbarkeit durch fixierte Revisionen, Quellen, Hashes und gespeicherte Eingaben/Rohantworten herstellen. Leere Findings und Fehler dokumentieren; keine Wiederholung bis zum gewünschten Ergebnis.
- Keine Zugangsdaten oder privaten Gesprächsinhalte einchecken. Generierte Falldaten bleiben unversioniert; Herkunft und Lizenzen erhalten.

## Prüfungen

Im Repo-Wurzelverzeichnis mit Python 3.9+; aktuell nur Standardbibliothek:

```bash
python3 -m unittest -v
git diff --check
```

Die drei Offline-Tests prüfen Referenztrennung/Byteerhalt/Hashes, Schutz bestehender Ausgaben und Downloadfehler ohne Teilausgabe. Bei Codeänderungen ausführen; weitere Tests nur für konkrete Risiken ergänzen.

Optionaler echter Vorbereitungslauf bei Änderungen am Download/Export (Netzzugriff auf `raw.githubusercontent.com`, Ziel muss neu sein):

```bash
python3 prepare_case.py --output data/VUL4J-18-check
```

Bestehende Versuchsdaten nicht löschen oder überschreiben; bei belegtem Ziel einen neuen Pfad wählen. Dieser Befehl führt **keinen Java-PoV** aus. Es gibt bisher keinen verifizierten lokalen Build-/PoV-Testbefehl für den vollständigen Benchmark.
