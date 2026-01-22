import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

def smart_heating_student_project():
    # Echte Berliner Wetterdaten (1.-14. Januar 2026)
    berlin_wetter = [2.9, 1.7, -0.4, -2.1, -2.2, -7.0, -6.7, -7.0, -6.0, -5.4, -6.4, -6.9, 1.4, 2.9]
    
    # Berliner Monatsdurchschnittstemperaturen 2025 für Jahresprognose
    monatsdaten_2025 = {
        'Jan': 3.2, 'Feb': 5.8, 'Mär': 7.1, 'Apr': 10.2, 'Mai': 14.8, 'Jun': 18.9,
        'Jul': 20.1, 'Aug': 19.3, 'Sep': 15.2, 'Okt': 10.8, 'Nov': 6.4, 'Dez': 2.1
    }
    
    # === PARAMETER ===
    u_standard = 0.15      # Unsanierter Altbau
    u_gedaemmt = 0.020     # Nach EnEV-Standard gedämmt
    max_heizleistung = 50  # kW
    
    # Dynamischer Strompreis
    def strompreis(stunde):
        h = stunde % 24
        basis = 0.30
        schwankung = 0.15 * np.sin((h - 15) * 2 * np.pi / 12) + 0.15
        return round(basis + schwankung, 2)
    
    # Szenarien
    temp = {'klassisch': 19.0, 'smart': 19.0, 'smart_daemm': 19.0}
    
    # Daten speichern
    kosten = {k: [] for k in temp.keys()}
    temp_verlauf = {k: [] for k in temp.keys()}
    heizleistung = {k: [] for k in temp.keys()}
    preisverlauf = []
    aussenverlauf = []
    solltemp_verlauf = []
    gesamt_kosten = {k: 0.0 for k in temp.keys()}
    energie_kwh = {k: [] for k in temp.keys()}
    
    # SIMULATION (14 Tage)
    for stunde in range(14 * 24):
        aussen_temp = berlin_wetter[stunde // 24]
        aussenverlauf.append(aussen_temp)
        h = stunde % 24
        preis = strompreis(stunde)
        preisverlauf.append(preis)
        
        # Wärmeverlust
        temp['klassisch'] -= (temp['klassisch'] - aussen_temp) * u_standard
        temp['smart'] -= (temp['smart'] - aussen_temp) * u_standard
        temp['smart_daemm'] -= (temp['smart_daemm'] - aussen_temp) * u_gedaemmt
        
        # Solltemperatur
        if 22 <= h or h < 6:
            soll = 17.0
        elif 8 <= h < 17:
            soll = 15.0
        else:
            soll = 21.0
        solltemp_verlauf.append(soll)
        
        # Schimmelschutz 
        if aussen_temp < 0:
            soll = max(soll, 16.5)
        
        # Predictive Control
        if strompreis(stunde + 3) > preis * 1.20:
            soll += 1.5
        
        # Heizleistung berechnen
        def berechne_leistung(ist, ziel):
            differenz = ziel - ist
            if differenz <= 0:
                return 0
            return min(max_heizleistung, differenz * 4.0)
        
        leistung = {
            'klassisch': berechne_leistung(temp['klassisch'], 21.0),
            'smart': berechne_leistung(temp['smart'], soll),
            'smart_daemm': berechne_leistung(temp['smart_daemm'], soll)
        }
        
        # Update
        for key in temp.keys():
            temp[key] += leistung[key] * 0.25
            energie = leistung[key] * (1/24)
            kosten_h = energie * preis
            gesamt_kosten[key] += kosten_h
            
            temp_verlauf[key].append(temp[key])
            heizleistung[key].append(leistung[key])
            energie_kwh[key].append(energie)
            kosten[key].append(gesamt_kosten[key])
    
    #AUSWERTUNG
    # X-Achsen für Plots
    tage = [i/24.0 for i in range(len(temp_verlauf['klassisch']))]
    stunden = [i/24.0 for i in range(len(solltemp_verlauf))]
    
    energie_gesamt = {k: sum(energie_kwh[k]) for k in temp.keys()}
    co2_faktor = 0.420
    co2_emissionen = {k: energie_gesamt[k] * co2_faktor for k in temp.keys()}
    
    # JAHRESHOCHRECHNUNG BASIEREND AUF 2025-DATEN 
    # Berechne Kosten pro Tag für Januar-Simulation
    kosten_pro_tag = {k: gesamt_kosten[k] / 14 for k in temp.keys()}
    
    # Monatliche Korrekturfaktoren basierend auf 2025-Temperaturen
    jan_temp = monatsdaten_2025['Jan']
    tage_pro_monat = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monate_namen = list(monatsdaten_2025.keys())
    
    jahres_kosten_2025 = {k: 0.0 for k in temp.keys()}
    monatliche_kosten_2025 = {k: [] for k in temp.keys()}
    
    for i, (monat, temp_monat) in enumerate(monatsdaten_2025.items()):
        # Heizgrenze: Bei Temperaturen über 15°C keine Heizung
        if temp_monat > 15:
            faktor = 0.0
        else:
            # Faktor basiert auf Temperaturdifferenz zur Behaglichkeit (21°C)
            temp_diff_monat = max(0, 21 - temp_monat)
            temp_diff_jan = max(0, 21 - jan_temp)
            faktor = temp_diff_monat / temp_diff_jan if temp_diff_jan > 0 else 0
        
        tage = tage_pro_monat[i]
        
        for key in temp.keys():
            kosten_monat = kosten_pro_tag[key] * tage * faktor
            monatliche_kosten_2025[key].append(kosten_monat)
            jahres_kosten_2025[key] += kosten_monat
    
    einsparung = gesamt_kosten['klassisch'] - gesamt_kosten['smart_daemm']
    prozent = einsparung / gesamt_kosten['klassisch'] * 100
    einsparung_jahr = jahres_kosten_2025['klassisch'] - jahres_kosten_2025['smart_daemm']
    prozent_jahr = einsparung_jahr / jahres_kosten_2025['klassisch'] * 100
    
    #VISUALISIERUNG
    plt.style.use('seaborn-v0_8-darkgrid')
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor('white')
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3, 
                  left=0.08, right=0.95, top=0.92, bottom=0.08)
    
    farben = {'klassisch': '#E74C3C', 'smart': '#F39C12', 'smart_daemm': '#27AE60'}
    
    # 1. TEMPERATURVERLAUF
    ax1 = fig.add_subplot(gs[0, :])
    tage_plot = [i/24.0 for i in range(len(temp_verlauf['klassisch']))]
    aussenverlauf_extended = aussenverlauf + [aussenverlauf[-1]]
    ax1.fill_between(tage_plot, -10, aussenverlauf, 
                     alpha=0.12, color='#3498DB', zorder=1)
    ax1.plot(tage_plot, temp_verlauf['klassisch'], color=farben['klassisch'], 
             linewidth=2, alpha=0.7, label='Klassisch', zorder=3)
    ax1.plot(tage_plot, temp_verlauf['smart'], color=farben['smart'], 
             linewidth=2.5, label='Smart', zorder=4)
    ax1.plot(tage_plot, temp_verlauf['smart_daemm'], color=farben['smart_daemm'], 
             linewidth=3, label='Smart + Dämmung', zorder=5)
    ax1.plot(stunden, solltemp_verlauf, color='#95A5A6', linestyle='--', 
             linewidth=1.5, alpha=0.6, label='Sollwert', zorder=2)
    ax1.axhline(16.5, color='#C0392B', linestyle=':', linewidth=2, 
                alpha=0.5, label='Schimmelschutz', zorder=2)
    ax1.set_ylabel('Temperatur (°C)', fontsize=12, fontweight='600')
    ax1.set_xlabel('Tage', fontsize=11)
    ax1.set_title('Temperaturverlauf', fontsize=14, fontweight='700', pad=15)
    ax1.legend(loc='lower right', framealpha=0.95, fontsize=10)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_xlim(0, 14)
    
    # 2. KOSTENVERGLEICH
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(tage_plot, kosten['klassisch'], color=farben['klassisch'], linewidth=3, alpha=0.8)
    ax2.plot(tage_plot, kosten['smart'], color=farben['smart'], linewidth=3.5)
    ax2.plot(tage_plot, kosten['smart_daemm'], color=farben['smart_daemm'], linewidth=4)
    ax2.fill_between(tage_plot, kosten['klassisch'], kosten['smart_daemm'], 
                     color=farben['smart_daemm'], alpha=0.15)
    ax2.set_xlabel('Tage', fontsize=11)
    ax2.set_ylabel('Kumulative Kosten (€)', fontsize=12, fontweight='600')
    ax2.set_title('Kostenentwicklung', fontsize=13, fontweight='700', pad=12)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_xlim(0, 14)
    ax2.text(0.5, 0.95, f'Einsparung: {einsparung:.2f}€ ({prozent:.0f}%)', 
             transform=ax2.transAxes, fontsize=11, ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#D5F4E6', 
                      edgecolor='#27AE60', linewidth=2))
    
    # 3. JAHRESHOCHRECHNUNG
    ax3 = fig.add_subplot(gs[1, 1])
    systeme = ['Klassisch', 'Smart', 'Smart +\nDämmung']
    jahres = [jahres_kosten_2025['klassisch'], jahres_kosten_2025['smart'], jahres_kosten_2025['smart_daemm']]
    bars = ax3.bar(systeme, jahres, 
                   color=[farben['klassisch'], farben['smart'], farben['smart_daemm']], 
                   alpha=0.85, edgecolor='white', linewidth=2, width=0.6)
    for bar, wert in zip(bars, jahres):
        ax3.text(bar.get_x() + bar.get_width()/2, wert + 15, f'{wert:.0f}€', 
                ha='center', fontsize=11, fontweight='700')
    ax3.set_ylabel('Jahreskosten (€)', fontsize=12, fontweight='600')
    ax3.set_title('Jahreshochrechnung\n(basierend auf 2025-Klima)', fontsize=13, fontweight='700', pad=12)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.set_ylim(0, max(jahres) * 1.15)
    
    # 4. WOHNUNGSDATEN & RESULTS
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.axis('off')
    
    # Oberer Teil
    wohnung_text = """WOHNUNGSDATEN
Fläche: 40 m²
Bewohner: 1 Person
Abwesenheit: Mo-Fr 8-17 Uhr
Heizleistung: 5 kW

Gebäudehülle:
  Ungedämmt (Klasse F): U = 1.50 W/(m²K)
  Gedämmt (Klasse A): U = 0.20 W/(m²K)

Strompreis:
  Basis: 0.30 €/kWh
  Dynamisch: 0.15-0.60 €/kWh"""
    
    ax4.text(0.05, 0.98, wohnung_text, transform=ax4.transAxes, 
             fontsize=9, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.8', facecolor='#E8F4F8', 
                      edgecolor='#3498DB', linewidth=2))
    
    # Unterer Teil
    metrics_text = f"""ERGEBNISSE (14 Tage)
Einsparung: {einsparung:.2f} € ({prozent:.0f}%)
Energie: -{energie_gesamt['klassisch']-energie_gesamt['smart_daemm']:.0f} kWh
CO₂-Reduktion: -{co2_emissionen['klassisch']-co2_emissionen['smart_daemm']:.1f} kg

JAHRESPROGNOSE (2025-Klima)
Einsparung: {einsparung_jahr:.0f} € ({prozent_jahr:.0f}%)
Heizmonate: Okt-Apr (ca. 210 Tage)"""
    
    ax4.text(0.05, 0.30, metrics_text, transform=ax4.transAxes, 
             fontsize=9, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.8', facecolor='#D5F4E6', 
                      edgecolor='#27AE60', linewidth=2))
    
    ax4.set_title('Setup & Results', fontsize=13, fontweight='700', pad=12, loc='left')
    
  
    fig.suptitle('Smart Heating Simulation', 
                 fontsize=16, fontweight='700', x=0.52, y=0.98)
    
    #KONSOLEN-OUTPUT
    print("\n" + "="*70)
    print("SMART HEATING SIMULATION".center(70))
    print(" Berlin, 1.-14. Januar 2026".center(70))
    print("="*70)
    
    print("\n WOHNUNGSDATEN:")
    print("-"*70)
    print("  Fläche: 40 m²")
    print("  Bewohner: 1 Person")
    print("  Abwesenheit: Mo-Fr 8-17 Uhr")
    print("  Heizleistung: 5 kW")
    print("  U-Wert Standard: 0.15 W/(m²K)")
    print("  U-Wert Gedämmt: 0.020 W/(m²K)")
    
    print("\n ERGEBNISSE (14 Tage):")
    print("-"*70)
    print(f"{'System':<20} {'Kosten':>12} {'Energie':>12} {'CO₂':>12}")
    print("-"*70)
    print(f"{'Klassisch':<20} {gesamt_kosten['klassisch']:>10.2f} € {energie_gesamt['klassisch']:>9.0f} kWh {co2_emissionen['klassisch']:>9.1f} kg")
    print(f"{'Smart':<20} {gesamt_kosten['smart']:>10.2f} € {energie_gesamt['smart']:>9.0f} kWh {co2_emissionen['smart']:>9.1f} kg")
    print(f"{'Smart + Dämmung':<20} {gesamt_kosten['smart_daemm']:>10.2f} € {energie_gesamt['smart_daemm']:>9.0f} kWh {co2_emissionen['smart_daemm']:>9.1f} kg")
    
    print(f"\n EINSPARUNG (Smart + Dämmung):")
    print(f"  Kosten: {einsparung:.2f}€ ({prozent:.0f}%)")
    print(f"  Energie: {energie_gesamt['klassisch']-energie_gesamt['smart_daemm']:.0f} kWh")
    print(f"  CO₂: {co2_emissionen['klassisch']-co2_emissionen['smart_daemm']:.1f} kg")
    
    print(f"\n JAHRESHOCHRECHNUNG (basierend auf 2025-Klima Berlin):")
    print("-"*70)
    print(f"{'Monat':<8} {'Temp-Ø':>10} {'Klassisch':>12} {'Smart+Dämm':>12} {'Einsparung':>12}")
    print("-"*70)
    for i, monat in enumerate(monate_namen):
        temp_m = list(monatsdaten_2025.values())[i]
        einsparung_m = monatliche_kosten_2025['klassisch'][i] - monatliche_kosten_2025['smart_daemm'][i]
        print(f"{monat:<8} {temp_m:>8.1f}°C {monatliche_kosten_2025['klassisch'][i]:>10.2f} € {monatliche_kosten_2025['smart_daemm'][i]:>10.2f} € {einsparung_m:>10.2f} €")
    print("-"*70)
    print(f"{'GESAMT':<8} {' ':>10} {jahres_kosten_2025['klassisch']:>10.0f} € {jahres_kosten_2025['smart_daemm']:>10.0f} € {einsparung_jahr:>10.0f} €")
    
    print(f"\n  → Jahreseinsparung: {einsparung_jahr:.0f}€ ({prozent_jahr:.0f}%)")
    print(f"  → Methodik: Skalierung basierend auf Temperaturdifferenz zu 21°C")
    print(f"  → Heizgrenze: Keine Heizung bei Außentemperaturen > 15°C")
    
    plt.show()


smart_heating_student_project()