import streamlit as st
import datetime
import calendar
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Configuration de la page
st.set_page_config(
    page_title="Suivi des Cycles Menstruels - Équipe de Volley",
    page_icon="🏐",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .main-container {
            max-width: 1600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 5px;
        }
        
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        
        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
            margin-top: 20px;
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .day {
            aspect-ratio: 1;
            border: 1px solid #eee;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            position: relative;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            padding: 5px;
            overflow: hidden;
        }
        
        .day-header {
            background: #f8f9fa;
            font-weight: bold;
            color: #666;
        }
        
        .day-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            height: 100%;
        }
        
        .day-number {
            font-size: 14px;
            margin-bottom: 2px;
            align-self: flex-start;
        }
        
        .player-indicator {
            width: 100%;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .player-marker {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin: 1px;
        }
        
        .player-card {
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
        }
        
        .player-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .player-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .phase-settings {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .phase-card {
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            background: #f8f9fa;
        }
        
        .fatigue-log {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }
        
        .fatigue-entry {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            background: white;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        
        .legend {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .legend-color {
            width: 30px;
            height: 30px;
            border-radius: 6px;
            margin-right: 10px;
            border: 2px solid #ddd;
        }
        
        .menstruation { background-color: #ff4757; }
        .follicular { background-color: #ffa502; }
        .ovulation { background-color: #2ed573; }
        .luteal { background-color: #3742fa; }
        
        .energy-high { background-color: #2ed573; }
        .energy-medium { background-color: #ffa502; }
        .energy-low { background-color: #ff4757; }
        
        .match-high { border: 3px solid #2ed573 !important; }
        .match-medium { border: 3px solid #ffa502 !important; }
        .match-low { border: 3px solid #ff4757 !important; }
        
        .alert-dashboard {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        
        .alert-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: white;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #ff6b6b;
        }
        
        .month-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .current-month {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

# Initialisation de session_state
if 'players' not in st.session_state:
    st.session_state.players = []
    
if 'daily_entries' not in st.session_state:
    st.session_state.daily_entries = []
    
if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.datetime.now().month
    
if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.datetime.now().year
    
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'calendar'

# Fonctions utilitaires
def get_cycle_phase(day_in_cycle, cycle_length, period_duration):
    if day_in_cycle <= period_duration:
        return 'menstruation'
    if day_in_cycle <= cycle_length * 0.35:
        return 'follicular'
    if day_in_cycle <= cycle_length * 0.45:
        return 'ovulation'
    return 'luteal'

def get_phase_name_fr(phase):
    names = {
        'menstruation': 'Menstruation',
        'follicular': 'Phase folliculaire',
        'ovulation': 'Ovulation',
        'luteal': 'Phase lutéale'
    }
    return names.get(phase, phase)

def get_phase_color(phase):
    colors = {
        'menstruation': '#ff4757',
        'follicular': '#ffa502',
        'ovulation': '#2ed573',
        'luteal': '#3742fa'
    }
    return colors.get(phase, '#ccc')

def add_player(name):
    player = {
        'id': len(st.session_state.players) + 1,
        'name': name,
        'last_period_date': None,
        'cycle_length': 28,
        'period_duration': 5,
        'expected_energy': {
            'menstruation': 'low',
            'follicular': 'medium',
            'ovulation': 'high',
            'luteal': 'medium'
        },
        'correlation_data': {
            'menstruation': {'total': 0, 'fatigue': 0},
            'follicular': {'total': 0, 'fatigue': 0},
            'ovulation': {'total': 0, 'fatigue': 0},
            'luteal': {'total': 0, 'fatigue': 0}
        }
    }
    st.session_state.players.append(player)

def remove_player(player_id):
    st.session_state.players = [p for p in st.session_state.players if p['id'] != player_id]
    st.session_state.daily_entries = [e for e in st.session_state.daily_entries if e['player_id'] != player_id]

def add_daily_entry(player_id, date, energy_level, fatigue_level, notes):
    entry = {
        'id': len(st.session_state.daily_entries) + 1,
        'player_id': player_id,
        'date': date,
        'energy_level': energy_level,
        'fatigue_level': fatigue_level,
        'notes': notes
    }
    
    # Supprimer les entrées existantes pour cette date/joueuse
    st.session_state.daily_entries = [
        e for e in st.session_state.daily_entries 
        if not (e['player_id'] == player_id and e['date'] == date)
    ]
    
    st.session_state.daily_entries.append(entry)
    calculate_correlations(player_id)
    return entry

def calculate_correlations(player_id):
    player = next((p for p in st.session_state.players if p['id'] == player_id), None)
    if not player or not player['last_period_date']:
        return
    
    # Réinitialiser les données de corrélation
    for phase in player['correlation_data']:
        player['correlation_data'][phase] = {'total': 0, 'fatigue': 0}
    
    last_period = player['last_period_date']
    
    for entry in st.session_state.daily_entries:
        if entry['player_id'] != player_id:
            continue
            
        entry_date = entry['date']
        diff_days = (entry_date - last_period).days
        
        if diff_days >= 0:
            day_in_cycle = (diff_days % player['cycle_length']) + 1
            phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
            
            player['correlation_data'][phase]['total'] += 1
            if entry['fatigue_level'] >= 4:  # Fatigue élevée
                player['correlation_data'][phase]['fatigue'] += 1

def get_phase_correlation(player, phase):
    data = player['correlation_data'][phase]
    if data['total'] == 0:
        return 0
    return round((data['fatigue'] / data['total']) * 100)

def get_energy_match(player, phase, energy_level):
    expected = player['expected_energy'][phase]
    
    if expected == 'high':
        return 'high' if energy_level >= 4 else 'medium' if energy_level == 3 else 'low'
    elif expected == 'medium':
        return 'high' if energy_level == 5 else 'medium' if energy_level >= 3 else 'low'
    else:  # low
        return 'high' if energy_level >= 4 else 'medium' if energy_level == 3 else 'low'

def get_energy_match_level(expected, actual):
    if expected == actual:
        return 'high'
    
    if (expected == 'high' and actual == 'medium') or \
       (expected == 'medium' and actual in ['high', 'low']) or \
       (expected == 'low' and actual == 'medium'):
        return 'medium'
    
    return 'low'

def render_calendar():
    st.markdown(f"<div class='month-nav'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Mois précédent"):
            st.session_state.current_month -= 1
            if st.session_state.current_month < 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            st.experimental_rerun()
    
    with col2:
        month_name = calendar.month_name[st.session_state.current_month]
        st.markdown(f"<div class='current-month'>{month_name} {st.session_state.current_year}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Mois suivant →"):
            st.session_state.current_month += 1
            if st.session_state.current_month > 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Création du calendrier
    cal = calendar.monthcalendar(st.session_state.current_year, st.session_state.current_month)
    month_days = [day for week in cal for day in week if day != 0]
    
    st.markdown("<div class='calendar'>", unsafe_allow_html=True)
    
    # En-têtes des jours
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    for day in days:
        st.markdown(f"<div class='day day-header'>{day}</div>", unsafe_allow_html=True)
    
    # Jours vides au début du mois
    first_day = datetime.date(st.session_state.current_year, st.session_state.current_month, 1)
    first_weekday = first_day.weekday()
    for _ in range(first_weekday):
        st.markdown(f"<div class='day'></div>", unsafe_allow_html=True)
    
    # Jours du mois
    for day in month_days:
        current_date = datetime.date(st.session_state.current_year, st.session_state.current_month, day)
        day_entries = [e for e in st.session_state.daily_entries if e['date'] == current_date]
        
        # Déterminer la phase dominante pour la journée
        phase_info = []
        for player in st.session_state.players:
            if player['last_period_date']:
                last_period = player['last_period_date']
                diff_days = (current_date - last_period).days
                
                if diff_days >= 0:
                    day_in_cycle = (diff_days % player['cycle_length']) + 1
                    phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                    phase_info.append({
                        'player_id': player['id'],
                        'phase': phase
                    })
        
        # Trouver la phase la plus fréquente
        if phase_info:
            phase_counter = defaultdict(int)
            for info in phase_info:
                phase_counter[info['phase']] += 1
            dominant_phase = max(phase_counter, key=phase_counter.get)
        else:
            dominant_phase = None
        
        # Créer le contenu du jour
        day_html = f"""
        <div class='day' style='background-color: {get_phase_color(dominant_phase) if dominant_phase else '#fff'}'>
            <div class='day-content'>
                <div class='day-number'>{day}</div>
                <div class='player-indicator'>
        """
        
        # Ajouter les marqueurs pour chaque joueuse
        for player in st.session_state.players:
            player_entry = next((e for e in day_entries if e['player_id'] == player['id']), None)
            
            if player_entry:
                # Déterminer la correspondance énergie attendue/réelle
                if player['last_period_date']:
                    last_period = player['last_period_date']
                    diff_days = (current_date - last_period).days
                    
                    if diff_days >= 0:
                        day_in_cycle = (diff_days % player['cycle_length']) + 1
                        phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                        
                        # Énergie attendue pour cette phase
                        expected_energy = player['expected_energy'][phase]
                        
                        # Énergie réelle
                        actual_energy = 'high' if player_entry['energy_level'] >= 4 else 'medium' if player_entry['energy_level'] == 3 else 'low'
                        
                        # Niveau de correspondance
                        match_level = get_energy_match_level(expected_energy, actual_energy)
                        
                        # Couleur en fonction de la correspondance
                        match_color = {
                            'high': '#2ed573',
                            'medium': '#ffa502',
                            'low': '#ff4757'
                        }[match_level]
                        
                        day_html += f"<div class='player-marker' style='background-color: {match_color}' title='{player['name']}: Correspondance {match_level}'></div>"
        
        day_html += """
                </div>
            </div>
        </div>
        """
        
        st.markdown(day_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Légende
    st.markdown("""
    <div class='legend'>
        <h3>Légende</h3>
        <div class='legend-item'>
            <div class='legend-color menstruation'></div>
            <span>Menstruation</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color follicular'></div>
            <span>Phase folliculaire</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color ovulation'></div>
            <span>Ovulation</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color luteal'></div>
            <span>Phase lutéale</span>
        </div>
        
        <h4 style='margin-top: 15px;'>Correspondance énergie :</h4>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #2ed573; width: 20px; height: 20px;'></div>
            <span>Correspondance élevée</span>
        </div>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #ffa502; width: 20px; height: 20px;'></div>
            <span>Correspondance moyenne</span>
        </div>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #ff4757; width: 20px; height: 20px;'></div>
            <span>Correspondance faible</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Remplacez la fonction render_player_management par ce code corrigé
def render_player_management():
    st.subheader("Ajouter une nouvelle joueuse")
    
    with st.form("add_player_form"):
        player_name = st.text_input("Nom de la joueuse")
        submitted = st.form_submit_button("Ajouter")
        if submitted and player_name:
            add_player(player_name)
            st.success(f"Joueuse {player_name} ajoutée avec succès!")
    
    st.subheader("Gestion des joueuses")
    
    for player in st.session_state.players:
        with st.expander(f"🔧 {player['name']}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                last_period = st.date_input(
                    "Date des dernières règles",
                    value=player['last_period_date'] or datetime.date.today(),
                    key=f"last_period_{player['id']}"
                )
                player['last_period_date'] = last_period
                
            with col2:
                if st.button("Supprimer", key=f"del_{player['id']}"):
                    remove_player(player['id'])
                    st.experimental_rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                player['cycle_length'] = st.slider(
                    "Durée du cycle (jours)",
                    min_value=21,
                    max_value=35,
                    value=player['cycle_length'],
                    key=f"cycle_{player['id']}"
                )
            
            with col2:
                player['period_duration'] = st.slider(
                    "Durée des règles (jours)",
                    min_value=2,
                    max_value=9,
                    value=player['period_duration'],
                    key=f"period_{player['id']}"
                )
            
            st.subheader("Énergie attendue par phase")
            cols = st.columns(4)
            phases = ['menstruation', 'follicular', 'ovulation', 'luteal']
            phase_names = ['Menstruation', 'Phase folliculaire', 'Ovulation', 'Phase lutéale']
            
            for i, phase in enumerate(phases):
                with cols[i]:
                    st.markdown(f"<div class='phase-card'>{phase_names[i]}</div>", unsafe_allow_html=True)
                    
                    # Dictionnaire de traduction
                    energy_translation = {
                        'low': 'Faible',
                        'medium': 'Moyenne',
                        'high': 'Élevée'
                    }
                    
                    # Valeur actuelle traduite
                    current_value = energy_translation.get(
                        player['expected_energy'][phase], 
                        'Moyenne'  # Valeur par défaut
                    )
                    
                    energy_option = st.radio(
                        "",
                        options=['Élevée', 'Moyenne', 'Faible'],
                        index=['Élevée', 'Moyenne', 'Faible'].index(current_value),
                        key=f"energy_{player['id']}_{phase}",
                        horizontal=False
                    )
                    
                    # Stockage en anglais pour la logique interne
                    reverse_translation = {
                        'Faible': 'low',
                        'Moyenne': 'medium',
                        'Élevée': 'high'
                    }
                    player['expected_energy'][phase] = reverse_translation[energy_option]
            
            st.subheader("Analyse de correspondance")
            if player['last_period_date']:
                # Calculer les correspondances
                match_data = []
                for entry in st.session_state.daily_entries:
                    if entry['player_id'] == player['id']:
                        entry_date = entry['date']
                        diff_days = (entry_date - player['last_period_date']).days
                        
                        if diff_days >= 0:
                            day_in_cycle = (diff_days % player['cycle_length']) + 1
                            phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                            
                            # Énergie attendue pour cette phase
                            expected_energy = player['expected_energy'][phase]
                            
                            # Énergie réelle
                            actual_energy = 'high' if entry['energy_level'] >= 4 else 'medium' if entry['energy_level'] == 3 else 'low'
                            
                            # Niveau de correspondance
                            match_level = get_energy_match_level(expected_energy, actual_energy)
                            
                            match_data.append({
                                'date': entry_date,
                                'phase': phase,
                                'expected': expected_energy,
                                'actual': actual_energy,
                                'match': match_level
                            })
                
                if match_data:
                    df = pd.DataFrame(match_data)
                    
                    # Calculer le pourcentage de correspondance
                    match_counts = df['match'].value_counts(normalize=True) * 100
                    
                    st.metric("Correspondance globale", f"{match_counts.get('high', 0):.1f}% élevée")
                    
                    # Graphique
                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.countplot(data=df, x='match', order=['high', 'medium', 'low'], 
                                 palette=['#2ed573', '#ffa502', '#ff4757'])
                    ax.set_title("Correspondance énergie attendue/réelle")
                    ax.set_xlabel("Niveau de correspondance")
                    ax.set_ylabel("Nombre de jours")
                    st.pyplot(fig)
                else:
                    st.info("Aucune donnée de correspondance disponible pour cette joueuse")
            else:
                st.warning("Veuillez définir la date des dernières règles pour activer l'analyse")

def render_daily_entry():
    st.subheader("Saisie quotidienne d'énergie et de fatigue")
    
    with st.form("daily_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            player_id = st.selectbox(
                "Joueuse",
                options=[(p['id'], p['name']) for p in st.session_state.players],
                format_func=lambda x: next(p['name'] for p in st.session_state.players if p['id'] == x),
                index=0 if st.session_state.players else None
            )
            
            entry_date = st.date_input(
                "Date",
                value=datetime.date.today()
            )
        
        with col2:
            energy_level = st.slider(
                "Niveau d'énergie (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Très faible, 3 = Moyen, 5 = Très élevé"
            )
            
            fatigue_level = st.slider(
                "Niveau de fatigue (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Très faible, 3 = Moyen, 5 = Très élevé"
            )
        
        notes = st.text_area("Notes (symptômes, aménagements, etc.)")
        
        submitted = st.form_submit_button("Enregistrer")
        
        if submitted and player_id:
            add_daily_entry(player_id, entry_date, energy_level, fatigue_level, notes)
            st.success("Entrée enregistrée avec succès!")
    
    st.subheader("Historique des saisies")
    
    if not st.session_state.daily_entries:
        st.info("Aucune saisie enregistrée")
        return
    
    # Filtrer les entrées des 30 derniers jours
    recent_entries = [
        e for e in st.session_state.daily_entries 
        if e['date'] >= datetime.date.today() - timedelta(days=30)
    ]
    
    if not recent_entries:
        st.info("Aucune saisie récente")
        return
    
    for entry in sorted(recent_entries, key=lambda e: e['date'], reverse=True):
        player = next((p for p in st.session_state.players if p['id'] == entry['player_id']), None)
        if not player:
            continue
            
        energy_text = ["Très faible", "Faible", "Moyenne", "Élevée", "Très élevée"][entry['energy_level'] - 1]
        fatigue_text = ["Très faible", "Faible", "Moyenne", "Élevée", "Très élevée"][entry['fatigue_level'] - 1]
        
        # Afficher la correspondance si possible
        match_info = ""
        if player['last_period_date']:
            diff_days = (entry['date'] - player['last_period_date']).days
            if diff_days >= 0:
                day_in_cycle = (diff_days % player['cycle_length']) + 1
                phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                
                expected_energy = player['expected_energy'][phase]
                actual_energy = 'high' if entry['energy_level'] >= 4 else 'medium' if entry['energy_level'] == 3 else 'low'
                
                match_level = get_energy_match_level(expected_energy, actual_energy)
                match_text = {
                    'high': "Correspondance ÉLEVÉE",
                    'medium': "Correspondance MOYENNE",
                    'low': "Correspondance FAIBLE"
                }[match_level]
                
                match_color = {
                    'high': '#2ed573',
                    'medium': '#ffa502',
                    'low': '#ff4757'
                }[match_level]
                
                match_info = f"<div style='color: {match_color}; font-weight: bold; margin-top: 5px;'>{match_text}</div>"
        
        st.markdown(f"""
        <div class='player-card'>
            <div class='player-header'>
                <div class='player-name'>{player['name']}</div>
                <div>{entry['date'].strftime('%d/%m/%Y')}</div>
            </div>
            <div>
                <strong>Énergie:</strong> {entry['energy_level']} - {energy_text}<br>
                <strong>Fatigue:</strong> {entry['fatigue_level']} - {fatigue_text}
            </div>
            {match_info}
            <div style='margin-top: 10px;'><strong>Notes:</strong> {entry['notes'] or 'Aucune'}</div>
        </div>
        """, unsafe_allow_html=True)

def render_coach_dashboard():
    st.subheader("🚨 Alertes du jour")
    
    today = datetime.date.today()
    alerts = []
    
    for player in st.session_state.players:
        if not player['last_period_date']:
            continue
            
        last_period = player['last_period_date']
        diff_days = (today - last_period).days
        
        if diff_days >= 0:
            day_in_cycle = (diff_days % player['cycle_length']) + 1
            phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
            correlation = get_phase_correlation(player, phase)
            
            # Vérifier si c'est une période à risque
            if player['expected_energy'][phase] == 'low' and correlation > 30:
                alerts.append({
                    'player': player['name'],
                    'phase': phase,
                    'day_in_cycle': day_in_cycle,
                    'correlation': correlation,
                    'expected_energy': player['expected_energy'][phase]
                })
    
    if not alerts:
        st.success("Aucune alerte pour aujourd'hui")
    else:
        for alert in alerts:
            st.markdown(f"""
            <div class='alert-item'>
                <div>
                    <strong>{alert['player']}</strong> - {get_phase_name_fr(alert['phase'])} (J{alert['day_in_cycle']})
                    <br><small>Énergie attendue: {alert['expected_energy'].capitalize()} | Risque de fatigue: {alert['correlation']}%</small>
                </div>
                <div style='color: #ff6b6b; font-weight: bold;'>
                    ⚠️ ALERTE
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.subheader("📊 Analyse des tendances")
    
    if not st.session_state.players:
        st.info("Aucune joueuse enregistrée")
        return
    
    # Calcul des correspondances globales
    match_data = []
    for player in st.session_state.players:
        if not player['last_period_date']:
            continue
            
        player_matches = []
        for entry in st.session_state.daily_entries:
            if entry['player_id'] == player['id']:
                entry_date = entry['date']
                diff_days = (entry_date - player['last_period_date']).days
                
                if diff_days >= 0:
                    day_in_cycle = (diff_days % player['cycle_length']) + 1
                    phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                    
                    # Énergie attendue pour cette phase
                    expected_energy = player['expected_energy'][phase]
                    
                    # Énergie réelle
                    actual_energy = 'high' if entry['energy_level'] >= 4 else 'medium' if entry['energy_level'] == 3 else 'low'
                    
                    # Niveau de correspondance
                    match_level = get_energy_match_level(expected_energy, actual_energy)
                    
                    player_matches.append(match_level)
        
        if player_matches:
            match_counts = pd.Series(player_matches).value_counts(normalize=True) * 100
            match_data.append({
                'player': player['name'],
                'high_match': match_counts.get('high', 0),
                'medium_match': match_counts.get('medium', 0),
                'low_match': match_counts.get('low', 0)
            })
    
    if not match_data:
        st.info("Aucune donnée disponible pour l'analyse")
        return
    
    df = pd.DataFrame(match_data)
    
    # Graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    df.set_index('player').plot(kind='bar', stacked=True, 
                              color=['#2ed573', '#ffa502', '#ff4757'],
                              ax=ax)
    ax.set_title("Correspondance énergie attendue/réelle par joueuse")
    ax.set_ylabel("Pourcentage (%)")
    ax.set_xlabel("Joueuse")
    ax.legend(['Correspondance élevée', 'Correspondance moyenne', 'Correspondance faible'])
    st.pyplot(fig)
    
    # Détails par phase
    st.subheader("Détails par phase du cycle")
    
    phase_data = []
    for phase in ['menstruation', 'follicular', 'ovulation', 'luteal']:
        phase_matches = []
        for player in st.session_state.players:
            if not player['last_period_date']:
                continue
                
            for entry in st.session_state.daily_entries:
                if entry['player_id'] == player['id']:
                    entry_date = entry['date']
                    diff_days = (entry_date - player['last_period_date']).days
                    
                    if diff_days >= 0:
                        day_in_cycle = (diff_days % player['cycle_length']) + 1
                        current_phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                        
                        if current_phase == phase:
                            expected_energy = player['expected_energy'][phase]
                            actual_energy = 'high' if entry['energy_level'] >= 4 else 'medium' if entry['energy_level'] == 3 else 'low'
                            match_level = get_energy_match_level(expected_energy, actual_energy)
                            phase_matches.append(match_level)
        
        if phase_matches:
            match_counts = pd.Series(phase_matches).value_counts(normalize=True) * 100
            phase_data.append({
                'phase': get_phase_name_fr(phase),
                'high_match': match_counts.get('high', 0),
                'medium_match': match_counts.get('medium', 0),
                'low_match': match_counts.get('low', 0)
            })
    
    if phase_data:
        df_phase = pd.DataFrame(phase_data)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        df_phase.set_index('phase').plot(kind='bar', stacked=True, 
                                       color=['#2ed573', '#ffa502', '#ff4757'],
                                       ax=ax)
        ax.set_title("Correspondance énergie attendue/réelle par phase")
        ax.set_ylabel("Pourcentage (%)")
        ax.legend(['Correspondance élevée', 'Correspondance moyenne', 'Correspondance faible'])
        st.pyplot(fig)
    else:
        st.info("Aucune donnée disponible pour l'analyse par phase")

# Interface principale
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.markdown("<h1>🏐 Suivi des Cycles Menstruels - Équipe de Volley</h1>", unsafe_allow_html=True)

# Tabs
tabs = ["Calendrier", "Gestion Joueuses", "Tableau de Bord Entraîneur", "Saisie Quotidienne"]
current_tab = st.session_state.current_tab

# Créer les onglets
tab1, tab2, tab3, tab4 = st.tabs(tabs)

with tab1:
    render_calendar()

with tab2:
    render_player_management()

with tab3:
    render_coach_dashboard()

with tab4:
    render_daily_entry()

st.markdown("</div>", unsafe_allow_html=True)
