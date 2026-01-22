# Smart-Heizungs-Simulation

Über das Projekt:

Diese Simulation vergleicht drei Heizszenarien über 14 Tage (1.-14. Januar 2026) und rechnet basierend auf Daten aus 2025 auf ein ganzes Jahr hoch:

- Klassisch: Konstante 21°C keine Optimierung

- Smart: Dynamische Temperatursteuerung basierend auf Anwesenheit, Strompreisen und Wettervorhersage

- Smart + Dämmung: Smart-Steuerung mit verbesserter Gebäudedämmung

Features

- Echte Berliner Wetterdaten (Januar 2026)
- Dynamische Strompreise
- Vorausschauende Steuerung
- Schimmelschutz 
- Abwesenheitserkennung
- Jahreshochrechnung basierend auf 2025-Klimadaten
- Visualisierung mit Matplotlib

Installation:
pip install matplotlib numpy

Verwendung
Simulation.py ausführen

Ergebnisse
Die Simulation zeigt:

- 14-Tage-Einsparung 
- Jahresprognose
- CO₂-Reduktion

Output
Das Skript erzeugt:

- Detaillierte Konsolen-Ausgabe mit Monatswerten
- Interaktive Visualisierung mit 4 Plots:

- Temperaturverlauf
- Kostenentwicklung
- Jahreshochrechnung
- Setup & Results



Parameter

Wohnfläche: 40 m²
Heizleistung: 5 kW
U-Wert Standard: 1.5 W/(m²K)
U-Wert Gedämmt: 0.2 W/(m²K)
Strompreis: 0.30 €/kWh (Basis) + dynamische Schwankungen



