import streamlit as st
import datetime
import calendar
import pandas as pd
import numpy as np
from datetime import timedelta, date
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
import os

# Correction des imports et gestion des dates
dt = datetime.datetime

# Fonctions de sauvegarde
def save_data():
    """Sauvegarde toutes les données dans un fichier JSON"""
    players_data = []
    for player in st.session_state.players:
        player_copy = player.copy()
        if player_copy.get('last_period_date'):
            if isinstance(player_copy['last_period_date'], date):
                player_copy['last_period_date'] = player_copy['last_period_date'].isoformat()
        players_data.append(player_copy)
    
    daily_entries_data = []
    for entry in st.session_state.daily_entries:
        entry_copy = entry.copy()
        if isinstance(entry_copy.get('date'), date):
            entry_copy['date'] = entry_copy['date'].isoformat()
        daily_entries_data.append(entry_copy)
    
    data = {
        'players': players_data,
        'daily_entries': daily_entries_data,
        'current_month': st.session_state.current_month,
        'current_year': st.session_state.current_year
    }
    
    try:
        with open('volley_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")

def load_data():
    """Charge les données depuis le fichier JSON"""
    if os.path.exists('volley_data.json'):
        try:
            with open('volley_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                players = data.get('players', [])
                for player in players:
                    if player.get('last_period_date'):
                        try:
                            player['last_period_date'] = date.fromisoformat(player['last_period_date'])
                        except (ValueError, TypeError):
                            player['last_period_date'] = None
                
                daily_entries = data.get('daily_entries', [])
                for entry in daily_entries:
                    if entry.get('date'):
                        try:
                            if isinstance(entry['date'], str):
                                entry['date'] = date.fromisoformat(entry['date'])
                        except (ValueError, TypeError):
                            entry['date'] = date.today()
                
                st.session_state.players = players
                st.session_state.daily_entries = daily_entries
                st.session_state.current_month = data.get('current_month', dt.now().month)
                st.session_state.current_year = data.get('current_year', dt.now().year)
                
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {e}")
            st.session_state.players = []
            st.session_state.daily_entries = []
            st.session_state.current_month = dt.now().month
            st.session_state.current_year = dt.now().year

# Chargement des données au démarrage
if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

# Configuration de la page
st.set_page_config(
    page_title="Suivi des Cycles Menstruels - Équipe de Volley",
    page_icon="🏐",
    layout="wide"
)

# Style CSS personnalisé avec meilleur contraste et lisibilité
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
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 3px;
            margin-top: 20px;
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .day {
            aspect-ratio: 1;
            border: 2px solid #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            position: relative;
            border-radius: 12px;
            transition: all 0.3s ease;
            cursor: pointer;
            padding: 8px;
            overflow: hidden;
            min-height: 120px;
        }
        
        .day-header {
            background: linear-gradient(135deg, #34495e, #2c3e50);
            color: white;
            font-weight: bold;
            padding: 15px 0;
            font-size: 14px;
            border: none;
        }
        
        .day-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            height: 100%;
            position: relative;
        }
        
        .date-display {
            font-size: 22px;
            font-weight: 900;
            margin-bottom: 5px;
            color: #2c3e50;
            text-shadow: 
                1px 1px 0px white,
                2px 2px 0px white,
                3px 3px 0px white,
                -1px -1px 0px white,
                -2px -2px 0px white;
            z-index: 10;
        }
        
        .day-name {
            font-size: 11px;
            margin-bottom: 8px;
            color: #34495e;
            font-weight: bold;
            text-shadow: 1px 1px 0px white, -1px -1px 0px white;
        }
        
        .player-indicator {
            width: 100%;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 3px;
        }
        
        .player-marker {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin: 1px;
            border: 2px solid #2c3e50;
            box-shadow: 0 0 3px rgba(0,0,0,0.3);
        }
        
        .legend {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 25px;
            border-radius: 15px;
            margin-top: 20px;
            border: 2px solid #dee2e6;
        }
        
        .legend h3, .legend h4 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            padding: 5px;
            background: white;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        
        .legend-color {
            width: 35px;
            height: 35px;
            border-radius: 8px;
            margin-right: 15px;
            border: 3px solid #2c3e50;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Nouvelles couleurs plus contrastées */
        .menstruation { 
            background: linear-gradient(135deg, #e74c3c, #c0392b);
        }
        .follicular { 
            background: linear-gradient(135deg, #f39c12, #d68910);
        }
        .ovulation { 
            background: linear-gradient(135deg, #27ae60, #229954);
        }
        .luteal { 
            background: linear-gradient(135deg, #8e44ad, #7d3c98);
        }
        
        .month-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #34495e, #2c3e50);
            padding: 15px 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .current-month {
            font-size: 1.8em;
            font-weight: bold;
            color: white;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .nav-button {
            padding: 10px 25px;
            border-radius: 8px;
            border: none;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        }
        
        .nav-button:hover {
            background: linear-gradient(135deg, #2980b9, #1f618d);
            transform: translateY(-2px);
        }
        
        .alert-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fff5f5;
            border-left: 6px solid #e74c3c;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border: 1px solid #fadbd8;
        }
        
        .correlation-alert {
            position: absolute;
            top: 5px;
            right: 5px;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 11px;
            box-shadow: 0 0 8px rgba(0,0,0,0.4);
            border: 2px solid white;
            z-index: 15;
        }
        
        /* Amélioration des contrastes pour les phases */
        .phase-menstruation {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
        }
        
        .phase-follicular {
            background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
            color: white;
        }
        
        .phase-ovulation {
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            color: white;
        }
        
        .phase-luteal {
            background: linear-gradient(135deg, #8e44ad 0%, #7d3c98 100%);
            color: white;
        }
        
        /* Amélioration de la lisibilité des textes */
        .legend-item span {
            color: #2c3e50;
            font-weight: 600;
            font-size: 14px;
        }
        
        .stRadio > label {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .stSelectbox > label {
            font-weight: bold;
            color: #2c3e50;
        }
    </style>
""", unsafe_allow_html=True)

# Initialisation de session_state
if 'players' not in st.session_state:
    st.session_state.players = []
    
if 'daily_entries' not in st.session_state:
    st.session_state.daily_entries = []
    
if 'current_month' not in st.session_state:
    st.session_state.current_month = dt.now().month
    
if 'current_year' not in st.session_state:
    st.session_state.current_year = dt.now().year
    
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'calendar'

# Fonctions utilitaires
def get_cycle_phase(day_in_cycle, cycle_length, period_duration):
    """Détermine la phase du cycle en fonction du jour"""
    if day_in_cycle <= period_duration:
        return 'menstruation'
    if day_in_cycle <= cycle_length * 0.35:
        return 'follicular'
    if day_in_cycle <= cycle_length * 0.45:
        return 'ovulation'
    return 'luteal'

def get_phase_name_fr(phase):
    """Traduit les noms de phases en français"""
    names = {
        'menstruation': 'Menstruation',
        'follicular': 'Phase folliculaire',
        'ovulation': 'Ovulation',
        'luteal': 'Phase lutéale'
    }
    return names.get(phase, phase)

def get_phase_color(phase):
    """Retourne la couleur associée à une phase avec meilleur contraste"""
    colors = {
        'menstruation': 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
        'follicular': 'linear-gradient(135deg, #f39c12 0%, #d68910 100%)',
        'ovulation': 'linear-gradient(135deg, #27ae60 0%, #229954 100%)',
        'luteal': 'linear-gradient(135deg, #8e44ad 0%, #7d3c98 100%)'
    }
    return colors.get(phase, '#ecf0f1')

def get_phase_solid_color(phase):
    """Retourne une couleur solide pour les éléments nécessitant une couleur unie"""
    colors = {
        'menstruation': '#e74c3c',
        'follicular': '#f39c12',
        'ovulation': '#27ae60',
        'luteal': '#8e44ad'
    }
    return colors.get(phase, '#95a5a6')

def add_player(name):
    """Ajoute une nouvelle joueuse"""
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
    save_data()

def remove_player(player_id):
    """Supprime une joueuse et ses données"""
    st.session_state.players = [p for p in st.session_state.players if p['id'] != player_id]
    st.session_state.daily_entries = [e for e in st.session_state.daily_entries if e['player_id'] != player_id]
    save_data()

def add_daily_entry(player_id, entry_date, energy_level, fatigue_level, notes):
    """Ajoute une entrée quotidienne"""
    if isinstance(entry_date, str):
        entry_date = date.fromisoformat(entry_date)
    
    entry = {
        'id': len(st.session_state.daily_entries) + 1,
        'player_id': player_id,
        'date': entry_date,
        'energy_level': energy_level,
        'fatigue_level': fatigue_level,
        'notes': notes
    }
    
    st.session_state.daily_entries = [
        e for e in st.session_state.daily_entries 
        if not (e['player_id'] == player_id and e['date'] == entry_date)
    ]
    
    st.session_state.daily_entries.append(entry)
    calculate_correlations()
    save_data()
    return entry

def calculate_correlations():
    """Calcule les corrélations pour toutes les joueuses"""
    for player in st.session_state.players:
        if not player['last_period_date']:
            continue
            
        for phase in player['correlation_data']:
            player['correlation_data'][phase] = {'total': 0, 'fatigue': 0}
        
        last_period = player['last_period_date']
        
        for entry in st.session_state.daily_entries:
            if entry['player_id'] != player['id']:
                continue
                
            entry_date = entry['date']
            diff_days = (entry_date - last_period).days
            
            if diff_days >= 0:
                day_in_cycle = (diff_days % player['cycle_length']) + 1
                phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                
                player['correlation_data'][phase]['total'] += 1
                if entry['fatigue_level'] >= 4:
                    player['correlation_data'][phase]['fatigue'] += 1

def get_energy_match_level(expected, actual):
    """Détermine le niveau de correspondance entre énergie attendue et réelle"""
    if expected == actual:
        return 'high'
    
    if (expected == 'high' and actual == 'medium') or \
       (expected == 'medium' and actual in ['high', 'low']) or \
       (expected == 'low' and actual == 'medium'):
        return 'medium'
    
    return 'low'

def render_calendar():
    """Affiche le calendrier avec les phases, correspondances et corrélations"""
    st.markdown(f"<div class='month-nav'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Mois précédent", key="prev_month", help="Aller au mois précédent"):
            st.session_state.current_month -= 1
            if st.session_state.current_month < 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            st.rerun()
    
    with col2:
        month_name = calendar.month_name[st.session_state.current_month]
        st.markdown(f"<div class='current-month'>{month_name} {st.session_state.current_year}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Mois suivant →", key="next_month", help="Aller au mois suivant"):
            st.session_state.current_month += 1
            if st.session_state.current_month > 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            st.rerun()
    
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
    first_day = date(st.session_state.current_year, st.session_state.current_month, 1)
    first_weekday = first_day.weekday()
    for _ in range(first_weekday):
        st.markdown(f"<div class='day'></div>", unsafe_allow_html=True)
    
    # Jours du mois
    for day in month_days:
        current_date = date(st.session_state.current_year, st.session_state.current_month, day)
        day_name = calendar.day_name[current_date.weekday()][:3]
        
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
            bg_gradient = get_phase_color(dominant_phase)
        else:
            dominant_phase = None
            bg_gradient = 'linear-gradient(135deg, #ecf0f1, #bdc3c7)'
        
        # Calculer la corrélation de fatigue pour ce jour
        total_players = 0
        fatigued_players = 0
        for player in st.session_state.players:
            player_entry = next((e for e in day_entries if e['player_id'] == player['id']), None)
            if player_entry:
                total_players += 1
                if player_entry['fatigue_level'] >= 4:
                    fatigued_players += 1
        
        correlation_percent = round((fatigued_players / total_players) * 100) if total_players > 0 else 0
        
        # Créer le contenu du jour avec meilleur contraste
        day_html = f"""
        <div class='day' style='background: {bg_gradient}; position: relative;'>
            <div class='day-content'>
                <div class='date-display'>{day}</div>
                <div class='day-name'>{day_name}</div>
                <div class='player-indicator'>
        """
        
        # Ajouter les marqueurs pour chaque joueuse avec des couleurs plus contrastées
        for player in st.session_state.players:
            player_entry = next((e for e in day_entries if e['player_id'] == player['id']), None)
            
            if player_entry and player['last_period_date']:
                last_period = player['last_period_date']
                diff_days = (current_date - last_period).days
                
                if diff_days >= 0:
                    day_in_cycle = (diff_days % player['cycle_length']) + 1
                    phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                    
                    expected_energy = player['expected_energy'][phase]
                    actual_energy = 'high' if player_entry['energy_level'] >= 4 else 'medium' if player_entry['energy_level'] == 3 else 'low'
                    match_level = get_energy_match_level(expected_energy, actual_energy)
                    
                    # Couleurs plus contrastées pour les marqueurs
                    match_color = {
                        'high': '#27ae60',    # Vert plus foncé
                        'medium': '#f39c12',  # Orange plus foncé
                        'low': '#e74c3c'      # Rouge plus foncé
                    }[match_level]
                    
                    day_html += f"<div class='player-marker' style='background-color: {match_color}' title='{player['name']}: Correspondance {match_level}'></div>"
        
        day_html += """
                </div>
            </div>
        """
        
        # Ajouter l'indicateur de corrélation avec des couleurs plus visibles
        if correlation_percent > 30:
            if correlation_percent > 70:
                alert_color = '#c0392b'  # Rouge très foncé
            elif correlation_percent > 50:
                alert_color = '#e74c3c'  # Rouge foncé
            else:
                alert_color = '#f39c12'  # Orange foncé
                
            day_html += f"""
            <div class='correlation-alert' style='background-color: {alert_color};'>
                {correlation_percent}%
            </div>
            """
        
        day_html += "</div>"
        
        st.markdown(day_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Légende améliorée
    st.markdown("""
    <div class='legend'>
        <h3>🎨 Légende des phases du cycle</h3>
        <div class='legend-item'>
            <div class='legend-color menstruation'></div>
            <span>Menstruation - Phase des règles</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color follicular'></div>
            <span>Phase folliculaire - Croissance des follicules</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color ovulation'></div>
            <span>Ovulation - Période de fertilité maximale</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color luteal'></div>
            <span>Phase lutéale - Préparation à la menstruation</span>
        </div>
        
        <h4 style='margin-top: 20px; color: #2c3e50;'>📊 Correspondance énergie attendue/réelle :</h4>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #27ae60; width: 25px; height: 25px;'></div>
            <span>Correspondance élevée - Énergie conforme aux attentes</span>
        </div>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #f39c12; width: 25px; height: 25px;'></div>
            <span>Correspondance moyenne - Légère différence</span>
        </div>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #e74c3c; width: 25px; height: 25px;'></div>
            <span>Correspondance faible - Énergie très différente</span>
        </div>
        
        <h4 style='margin-top: 20px; color: #2c3e50;'>⚠️ Indicateur de fatigue collective :</h4>
        <div class='legend-item'>
            <div style='background-color: #f39c12; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; border: 2px solid white;'>30%</div>
            <span>Risque modéré - 30-50% des joueuses fatiguées</span>
        </div>
        <div class='legend-item'>
            <div style='background-color: #e74c3c; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; border: 2px solid white;'>50%</div>
            <span>Risque élevé - 50-70% des joueuses fatiguées</span>
        </div>
        <div class='legend-item'>
            <div style='background-color: #c0392b; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; border: 2px solid white;'>70%</div>
            <span>Risque très élevé - Plus de 70% des joueuses fatiguées</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_player_management():
    """Interface de gestion des joueuses"""
    st.subheader("Ajouter une nouvelle joueuse")
    
    with st.form("add_player_form"):
        player_name = st.text_input("Nom de la joueuse")
        submitted = st.form_submit_button("Ajouter")
        if submitted and player_name:
            add_player(player_name)
            st.success(f"Joueuse {player_name} ajoutée avec succès!")
            st.rerun()
    
    st.subheader("Gestion des joueuses")
    
    for player in st.session_state.players:
        with st.expander(f"🔧 {player['name']}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                last_period = st.date_input(
                    "Date des dernières règles",
                    value=player['last_period_date'] or date.today(),
                    key=f"last_period_{player['id']}"
                )
                if last_period != player['last_period_date']:
                    player['last_period_date'] = last_period
                    save_data()
                
            with col2:
                if st.button("Supprimer", key=f"del_{player['id']}"):
                    remove_player(player['id'])
                    st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                cycle_length = st.slider(
                    "Durée du cycle (jours)",
                    min_value=21,
                    max_value=35,
                    value=player['cycle_length'],
                    key=f"cycle_{player['id']}"
                )
                if cycle_length != player['cycle_length']:
                    player['cycle_length'] = cycle_length
                    save_data()
            
            with col2:
                period_duration = st.slider(
                    "Durée des règles (jours)",
                    min_value=2,
                    max_value=9,
                    value=player['period_duration'],
                    key=f"period_{player['id']}"
                )
                if period_duration != player['period_duration']:
                    player['period_duration'] = period_duration
                    save_data()
            
            st.subheader("Énergie attendue par phase")
            cols = st.columns(4)
            phases = ['menstruation', 'follicular', 'ovulation', 'luteal']
            phase_names = ['Menstruation', 'Phase folliculaire', 'Ovulation', 'Phase lutéale']
            
            for i, phase in enumerate(phases):
                with cols[i]:
                    st.markdown(f"**{phase_names[i]}**")
                    
                    energy_translation = {
                        'low': 'Faible',
                        'medium': 'Moyenne',
                        'high': 'Élevée'
                    }
                    
                    current_value = energy_translation.get(
                        player['expected_energy'][phase], 
                        'Moyenne'
                    )
                    
                    energy_option = st.radio(
                        "Énergie",
                        options=['Élevée', 'Moyenne', 'Faible'],
                        index=['Élevée', 'Moyenne', 'Faible'].index(current_value),
                        key=f"energy_{player['id']}_{phase}",
                        horizontal=False
                    )
                    
                    reverse_translation = {
                        'Faible': 'low',
                        'Moyenne': 'medium',
                        'Élevée': 'high'
                    }
                    new_energy = reverse_translation[energy_option]
                    if new_energy != player['expected_energy'][phase]:
                        player['expected_energy'][phase] = new_energy
                        save_data()

def render_daily_entry():
    """Interface de saisie quotidienne avec contexte de cycle et recommandations"""
    st.subheader("📝 Saisie quotidienne")
    
    if not st.session_state.get('players'):
        st.warning("⚠️ Aucune joueuse enregistrée. Ajoutez d'abord des joueuses dans l'onglet 'Gestion'.")
        return
    
    with st.form("daily_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            player_options = {p['id']: p['name'] for p in st.session_state.players}
            player_id = st.selectbox(
                "Sélectionnez une joueuse",
                options=list(player_options.keys()),
                format_func=lambda x: player_options[x],
                index=0
            )
            selected_player = next(p for p in st.session_state.players if p['id'] == player_id)
        
        with col2:
            entry_date = st.date_input(
                "Date de l'entrée",
                value=date.today(),
                max_value=date.today()
            )
            
            existing_entry = next(
                (e for e in st.session_state.daily_entries 
                 if e['player_id'] == player_id and e['date'] == entry_date),
                None
            )
            if existing_entry:
                st.warning("⚠️ Une entrée existe déjà pour cette date. Elle sera mise à jour.")
        
        st.markdown("---")
        st.subheader("🔁 Contexte du cycle menstruel")
        
        if selected_player.get('last_period_date'):
            last_period = selected_player['last_period_date']
            diff_days = (entry_date - last_period).days
            
            if diff_days >= 0:
                day_in_cycle = (diff_days % selected_player['cycle_length']) + 1
                current_phase = get_cycle_phase(
                    day_in_cycle, 
                    selected_player['cycle_length'], 
                    selected_player['period_duration']
                )
                
                phase_data = selected_player['correlation_data'][current_phase]
                total_days = phase_data['total']
                fatigue_days = phase_data['fatigue']
                correlation = round((fatigue_days / total_days) * 100) if total_days > 0 else 0
                
                cols = st.columns([1, 2])
                
                with cols[0]:
                    st.markdown(f"**Phase actuelle:**")
                    st.markdown(
                        f"<div style='background-color: {get_phase_color(current_phase)}; "
                        f"padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold;'>"
                        f"{get_phase_name_fr(current_phase)}"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                
                with cols[1]:
                    st.markdown(f"**Jour du cycle:** {day_in_cycle}/{selected_player['cycle_length']}")
                    st.markdown(f"**Énergie attendue:** {selected_player['expected_energy'][current_phase].capitalize()}")
                    
                    if total_days > 0:
                        st.markdown(f"**Corrélation historique fatigue:**")
                        
                        progress_color = "#2ed573" if correlation < 30 else "#ffa502" if correlation < 50 else "#ff4757"
                        st.markdown(
                            f"<div style='display: flex; align-items: center;'>"
                            f"<div style='width: 100%; background: #f0f0f0; border-radius: 10px;'>"
                            f"<div style='width: {correlation}%; background: {progress_color}; "
                            f"border-radius: 10px; text-align: center; color: white; padding: 5px;'>"
                            f"{correlation}%"
                            f"</div></div></div>",
                            unsafe_allow_html=True
                        )
                        
                        if correlation > 50:
                            st.error("**🔴 Phase à risque élevé de fatigue**")
                            st.markdown("Recommandation: Adaptez l'intensité de l'entraînement")
                        elif correlation > 30:
                            st.warning("**🟠 Phase à risque modéré de fatigue**")
                    else:
                        st.info("ℹ️ Pas encore de données pour cette phase")
            else:
                st.warning("⚠️ Date antérieure aux dernières règles enregistrées")
        else:
            st.warning("ℹ️ Aucune date de dernières règles enregistrée pour cette joueuse")
        
        st.markdown("---")
        st.subheader("📊 Évaluation du jour")
        
        col1, col2 = st.columns(2)
        with col1:
            energy_level = st.slider(
                "**Niveau d'énergie (1-5)**",
                min_value=1, 
                max_value=5, 
                value=3,
                help="1 = Très faible, 3 = Moyen, 5 = Très énergique"
            )
        with col2:
            fatigue_level = st.slider(
                "**Niveau de fatigue (1-5)**",
                min_value=1, 
                max_value=5, 
                value=3,
                help="1 = Aucune fatigue, 3 = Fatigué(e), 5 = Épuisé(e)"
            )
        
        st.markdown("### 🛠 Aménagements d'entraînement")
        adjustments = st.multiselect(
            "Sélectionnez les aménagements appliqués",
            options=[
                "Réduction intensité", 
                "Exercices adaptés", 
                "Pause supplémentaire", 
                "Hydratation renforcée",
                "Récupération active",
                "Travail technique léger"
            ],
            help="Ces informations aideront à affiner les recommandations futures"
        )
        
        st.markdown("### 📝 Notes et observations")
        notes = st.text_area(
            "Décrivez les symptômes, douleurs ou observations particulières",
            placeholder="Ex: Crampes abdominales, maux de tête, besoin de pauses fréquentes...",
            height=100
        )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer les données", 
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            try:
                full_notes = notes
                if adjustments:
                    full_notes += "\n\nAménagements appliqués: " + ", ".join(adjustments)
                
                result = add_daily_entry(
                    player_id=player_id,
                    entry_date=entry_date,
                    energy_level=energy_level,
                    fatigue_level=fatigue_level,
                    notes=full_notes
                )
                
                if result:
                    st.success("✅ Données enregistrées avec succès !")
                    st.balloons()
                else:
                    st.error("❌ Erreur lors de l'enregistrement")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

def render_coach_dashboard():
    """Tableau de bord pour l'entraîneur avec alertes et analyses"""
    st.subheader("🚨 Alertes du jour")
    
    today = date.today()
    alerts = []
    
    for player in st.session_state.players:
        if not player['last_period_date']:
            continue
            
        last_period = player['last_period_date']
        diff_days = (today - last_period).days
        
        if diff_days >= 0:
            day_in_cycle = (diff_days % player['cycle_length']) + 1
            phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
            
            total_entries = player['correlation_data'][phase]['total']
            fatigue_entries = player['correlation_data'][phase]['fatigue']
            correlation = round((fatigue_entries / total_entries) * 100) if total_entries > 0 else 0
            
            if correlation > 30 or player['expected_energy'][phase] == 'low':
                alerts.append({
                    'player': player['name'],
                    'phase': phase,
                    'day_in_cycle': day_in_cycle,
                    'correlation': correlation,
                    'expected_energy': player['expected_energy'][phase],
                    'total_entries': total_entries
                })
    
    if not alerts:
        st.success("✅ Aucune alerte significative pour aujourd'hui")
    else:
        for alert in alerts:
            st.markdown(f"""
            <div class='alert-item'>
                <div>
                    <strong>{alert['player']}</strong> - {get_phase_name_fr(alert['phase'])} (J{alert['day_in_cycle']})
                    <br>
                    <small>
                        Énergie attendue: {alert['expected_energy'].capitalize()} | 
                        Corrélation fatigue: {alert['correlation']}% ({alert['total_entries']} jours analysés)
                    </small>
                </div>
                <div style='color: #ff6b6b; font-weight: bold;'>
                    {'⚠️ ALERTE FORTE' if alert['correlation'] > 50 else '⚠️ Attention'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.subheader("🔍 Analyse des corrélations")
    
    if not st.session_state.players:
        st.info("ℹ️ Aucune joueuse enregistrée")
        return
    
    st.markdown("### Corrélations par joueuse")
    for player in st.session_state.players:
        if not player['last_period_date']:
            continue
            
        with st.expander(f"📊 {player['name']}", expanded=False):
            cols = st.columns(4)
            phases = ['menstruation', 'follicular', 'ovulation', 'luteal']
            
            for i, phase in enumerate(phases):
                data = player['correlation_data'][phase]
                total = data['total']
                fatigue = data['fatigue']
                correlation = round((fatigue / total) * 100) if total > 0 else 0
                
                with cols[i]:
                    color = '#2ed573' if correlation < 30 else '#ffa502' if correlation < 50 else '#ff4757'
                    
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; border-radius: 10px; 
                                background-color: #f8f9fa; border: 2px solid {color};">
                        <b>{get_phase_name_fr(phase)}</b>
                        <div style="font-size: 24px; font-weight: bold; color: {color};">{correlation}%</div>
                        <small>Jours: {total}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            high_corr_phases = [p for p in phases 
                               if player['correlation_data'][p]['total'] > 5 and 
                               (player['correlation_data'][p]['fatigue'] / player['correlation_data'][p]['total']) > 0.5]
            
            if high_corr_phases:
                st.warning("**Recommandations d'entraînement:**")
                st.markdown(f"- Pendant les phases suivantes, réduire l'intensité des exercices: {', '.join([get_phase_name_fr(p) for p in high_corr_phases])}")
                st.markdown("- Prévoir des périodes de récupération supplémentaires")
                st.markdown("- Adapter les exercices en fonction du niveau de fatigue rapporté")
    
    st.markdown("### Tendance globale")
    phase_data = []
    for phase in ['menstruation', 'follicular', 'ovulation', 'luteal']:
        total_fatigue = 0
        total_entries = 0
        
        for player in st.session_state.players:
            data = player['correlation_data'][phase]
            total_fatigue += data['fatigue']
            total_entries += data['total']
        
        correlation = round((total_fatigue / total_entries) * 100) if total_entries > 0 else 0
        phase_data.append({
            'phase': get_phase_name_fr(phase),
            'correlation': correlation,
            'total_entries': total_entries
        })
    
    if phase_data:
        df = pd.DataFrame(phase_data)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='phase', y='correlation', data=df, ax=ax, palette=['#ff4757', '#ffa502', '#2ed573', '#3742fa'])
        ax.set_title("Corrélation moyenne entre phase du cycle et fatigue")
        ax.set_ylabel("Pourcentage de jours avec fatigue (%)")
        ax.set_xlabel("Phase du cycle")
        ax.set_ylim(0, 100)
        
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.0f}%", 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        xytext=(0, 10), 
                        textcoords='offset points')
        
        st.pyplot(fig)
    else:
        st.info("ℹ️ Pas assez de données pour l'analyse globale")

# Interface principale
st.title("🏐 Suivi des Cycles Menstruels - Équipe de Volley")

# Onglets
tabs = ["📅 Calendrier", "👤 Gestion des joueuses", "📝 Saisie quotidienne", "👨‍🏫 Tableau de bord coach"]
current_tab = st.radio("", tabs, horizontal=True, label_visibility="collapsed")

if current_tab == tabs[0]:
    render_calendar()
elif current_tab == tabs[1]:
    render_player_management()
elif current_tab == tabs[2]:
    render_daily_entry()
elif current_tab == tabs[3]:
    render_coach_dashboard()
