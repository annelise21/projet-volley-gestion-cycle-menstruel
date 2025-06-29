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
        :root {
            --menstruation: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            --follicular: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
            --ovulation: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            --luteal: linear-gradient(135deg, #8e44ad 0%, #7d3c98 100%);
        }
        
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
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
        }
        
        h1 {
            text-align: center;
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
        
        .alert-energy {
            background: #fff5f5;
            border-left: 6px solid #ff6b6b;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border: 1px solid #ffc9c9;
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
                0 0 5px white,
                0 0 10px white;
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
            width: 25px;
            height: 25px;
            border-radius: 50%;
            margin: 2px;
            border: 2px solid #2c3e50;
            box-shadow: 0 0 3px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            color: white;
            text-shadow: 1px 1px 1px #000;
        }
        
        .player-risk {
            position: absolute;
            top: 5px;
            left: 5px;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            z-index: 15;
            box-shadow: 0 0 3px rgba(0,0,0,0.5);
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
        
        .phase-menstruation { background: var(--menstruation); }
        .phase-follicular { background: var(--follicular); }
        .phase-ovulation { background: var(--ovulation); }
        .phase-luteal { background: var(--luteal); }
        
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
        
        .player-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 6px solid #3498db;
        }
        
        .fatigue-input {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .fatigue-bar {
            height: 20px;
            border-radius: 10px;
            background: #ecf0f1;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .fatigue-level {
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #f39c12, #e74c3c);
        }
        
        .explanation-box {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .correlation-explanation {
            background: #fff8e1;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
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

def get_phase_range(cycle_length, period_duration):
    """Retourne les plages de jours pour chaque phase"""
    return {
        'menstruation': f"J1-J{period_duration}",
        'follicular': f"J{period_duration + 1}-J{int(cycle_length * 0.35)}",
        'ovulation': f"J{int(cycle_length * 0.35) + 1}-J{int(cycle_length * 0.45)}",
        'luteal': f"J{int(cycle_length * 0.45) + 1}-J{cycle_length}"
    }

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

def get_player_risk_level(player, current_date):
    """Détermine le niveau de risque pour une joueuse à une date donnée"""
    if not player['last_period_date']:
        return None
        
    last_period = player['last_period_date']
    diff_days = (current_date - last_period).days
    
    if diff_days < 0:
        return None
        
    day_in_cycle = (diff_days % player['cycle_length']) + 1
    phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
    
    # Vérification de la fatigue historique pour ce jour spécifique
    if day_in_cycle in player['daily_fatigue']:
        if player['daily_fatigue'][str(day_in_cycle)] >= 4:
            return 'high'
        elif player['daily_fatigue'][str(day_in_cycle)] >= 3:
            return 'medium'
    
    return 'low'

def add_player(name, last_period_date, daily_fatigue):
    """Ajoute une nouvelle joueuse avec son historique de fatigue quotidien"""
    player = {
        'id': len(st.session_state.players) + 1,
        'name': name,
        'last_period_date': last_period_date,
        'cycle_length': 28,
        'period_duration': 5,
        'daily_fatigue': daily_fatigue,  # Historique de fatigue par jour du cycle
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
    
    # Supprimer les entrées existantes pour la même date et joueuse
    st.session_state.daily_entries = [
        e for e in st.session_state.daily_entries 
        if not (e['player_id'] == player_id and e['date'] == entry_date)
    ]
    
    st.session_state.daily_entries.append(entry)
    save_data()
    return entry

def render_calendar():
    """Affiche le calendrier avec les phases, correspondances et risques individuels"""
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
        
        # Créer le contenu du jour
        day_html = f"""
        <div class='day' style='background: {bg_gradient}; position: relative;'>
            <div class='day-content'>
                <div class='date-display'>{day}</div>
                <div class='day-name'>{day_name}</div>
                <div class='player-indicator'>
        """
        
        # Ajouter les marqueurs pour chaque joueuse
        for player in st.session_state.players:
            player_entry = next((e for e in day_entries if e['player_id'] == player['id']), None)
            
            if player['last_period_date']:
                last_period = player['last_period_date']
                diff_days = (current_date - last_period).days
                
                if diff_days >= 0:
                    day_in_cycle = (diff_days % player['cycle_length']) + 1
                    phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
                    
                    # Déterminer le niveau de risque
                    risk_level = get_player_risk_level(player, current_date)
                    
                    # Couleur en fonction du risque
                    risk_color = {
                        'low': '#27ae60',    # Vert
                        'medium': '#f39c12', # Orange
                        'high': '#e74c3c'    # Rouge
                    }.get(risk_level, '#bdc3c7')  # Gris par défaut
                    
                    # Créer le marqueur avec l'initiale du prénom
                    initial = player['name'][0].upper()
                    day_html += f"""
                    <div class='player-marker' style='background-color: {risk_color};'
                         title='{player["name"]} - {current_date.strftime("%d/%m/%Y")}
Phase: {get_phase_name_fr(phase)} (Jour {day_in_cycle})
État: {risk_level.capitalize() if risk_level else "Normal"}'>
                        {initial}
                    </div>
                    """
        
        day_html += """
                </div>
            </div>
        </div>
        """
        
        st.markdown(day_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Légende avec explications
    st.markdown("""
    <div class='legend'>
        <h3>🎨 Légende des phases du cycle</h3>
        <div class='legend-item'>
            <div class='legend-color menstruation'></div>
            <span><strong>Menstruation</strong> - Phase des règles</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color follicular'></div>
            <span><strong>Phase folliculaire</strong> - Croissance des follicules</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color ovulation'></div>
            <span><strong>Ovulation</strong> - Période de fertilité maximale</span>
        </div>
        <div class='legend-item'>
            <div class='legend-color luteal'></div>
            <span><strong>Phase lutéale</strong> - Préparation à la menstruation</span>
        </div>
        
        <h4 style='margin-top: 20px;'>👤 État des joueuses :</h4>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #27ae60; width: 25px; height: 25px;'>J</div>
            <span><strong>Faible risque</strong> - Énergie normale</span>
        </div>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #f39c12; width: 25px; height: 25px;'>J</div>
            <span><strong>Risque modéré</strong> - Fatigue possible</span>
        </div>
        <div class='legend-item'>
            <div class='player-marker' style='background-color: #e74c3c; width: 25px; height: 25px;'>J</div>
            <span><strong>Risque élevé</strong> - Fatigue probable</span>
        </div>
        
        <div class='correlation-explanation'>
            <h4>📊 Explication des corrélations</h4>
            <p>
                La <strong>corrélation historique</strong> représente le pourcentage de jours 
                où la joueuse a signalé une fatigue élevée pendant cette phase de son cycle.
                Plus ce pourcentage est élevé, plus il y a de chances que la joueuse ressente 
                de la fatigue pendant cette phase dans le futur.
            </p>
            <p>
                <strong>Exemple :</strong> Une corrélation de 75% pendant la phase lutéale signifie 
                que dans 3 cas sur 4, la joueuse a signalé une fatigue élevée pendant 
                cette phase lors des cycles précédents.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_player_management():
    """Interface de gestion des joueuses"""
    st.subheader("Ajouter une nouvelle joueuse")
    
    with st.form("add_player_form"):
        player_name = st.text_input("Nom de la joueuse", placeholder="Prénom Nom")
        
        # Section pour la date des dernières règles
        st.subheader("Début du cycle (J1)")
        col1, col2 = st.columns(2)
        with col1:
            last_period = st.date_input(
                "Date des dernières règles",
                value=date.today()
            )
        
        # Section pour la fatigue quotidienne
        st.subheader("État de fatigue par jour du cycle")
        st.markdown("""
            <div class='explanation-box'>
                <p>Veuillez indiquer pour chaque jour de votre cycle typique (de J1 à la fin) votre niveau de fatigue :</p>
                <ul>
                    <li><strong>1-2</strong> : Très énergique, pas de fatigue</li>
                    <li><strong>3</strong> : Fatigue légère, normale</li>
                    <li><strong>4-5</strong> : Fatigue importante, besoin de repos</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        # Saisie de la fatigue par jour
        daily_fatigue = {}
        cycle_length = st.slider(
            "Durée de votre cycle (jours)",
            min_value=21,
            max_value=35,
            value=28,
            key="new_player_cycle"
        )
        
        period_duration = st.slider(
            "Durée habituelle de vos règles (jours)",
            min_value=2,
            max_value=9,
            value=5,
            key="new_player_period"
        )
        
        st.markdown("**Niveau de fatigue par jour :**")
        cols = st.columns(5)
        for day in range(1, cycle_length + 1):
            with cols[(day-1) % 5]:
                # Déterminer la phase pour le jour
                phase = get_cycle_phase(day, cycle_length, period_duration)
                phase_color = get_phase_solid_color(phase)
                
                fatigue_level = st.slider(
                    f"Jour {day}",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"fatigue_day_{day}",
                    help=f"Phase: {get_phase_name_fr(phase)}"
                )
                daily_fatigue[str(day)] = fatigue_level
                
                # Barre de visualisation
                fatigue_percent = (fatigue_level / 5) * 100
                st.markdown(f"""
                    <div style="margin-top: -10px; margin-bottom: 20px;">
                        <div class="fatigue-bar">
                            <div class="fatigue-level" style="width: {fatigue_percent}%; background-color: {phase_color};"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Ajouter la joueuse")
        if submitted and player_name:
            add_player(player_name, last_period, daily_fatigue)
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
            
            # Afficher les plages de phases
            phase_ranges = get_phase_range(player['cycle_length'], player['period_duration'])
            st.subheader("Phases du cycle")
            cols = st.columns(4)
            phases = ['menstruation', 'follicular', 'ovulation', 'luteal']
            
            for i, phase in enumerate(phases):
                with cols[i]:
                    phase_name = get_phase_name_fr(phase)
                    st.markdown(f"""
                        <div style="
                            background: {get_phase_color(phase)};
                            color: white;
                            padding: 15px;
                            border-radius: 10px;
                            text-align: center;
                            margin-bottom: 15px;
                        ">
                            <strong>{phase_name}</strong><br>
                            {phase_ranges[phase]}
                        </div>
                    """, unsafe_allow_html=True)

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
                
                # Obtenir la fatigue historique pour ce jour
                historical_fatigue = selected_player['daily_fatigue'].get(str(day_in_cycle), 3)
                
                cols = st.columns(2)
                
                with cols[0]:
                    st.markdown(f"**Phase actuelle:**")
                    st.markdown(
                        f"<div style='background-color: {get_phase_color(current_phase)}; "
                        f"padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold;'>"
                        f"{get_phase_name_fr(current_phase)}"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**Jour du cycle:** {day_in_cycle}/{selected_player['cycle_length']}")
                
                with cols[1]:
                    st.markdown(f"**Fatigue historique ce jour:**")
                    # Barre de visualisation
                    fatigue_percent = (historical_fatigue / 5) * 100
                    phase_color = get_phase_solid_color(current_phase)
                    st.markdown(f"""
                        <div style="margin-top: 10px;">
                            <div class="fatigue-bar">
                                <div class="fatigue-level" style="width: {fatigue_percent}%; background-color: {phase_color};"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"Niveau historique: {historical_fatigue}/5")
                    
                    # Recommandation basée sur l'historique
                    if historical_fatigue >= 4:
                        st.error("**🔴 Jour à risque élevé de fatigue**")
                        st.markdown("Recommandation: Réduisez l'intensité de l'entraînement")
                    elif historical_fatigue >= 3:
                        st.warning("**🟠 Risque modéré de fatigue**")
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
    """Tableau de bord complet pour l'entraîneur avec alertes, analyses et recommandations"""
    st.title("📊 Tableau de bord de l'entraîneur")
    
    # Section des alertes du jour
    st.subheader("🚨 Alertes du jour")
    
    today = date.today()
    alerts = []
    
    # Analyse de chaque joueuse
    for player in st.session_state.players:
        if not player['last_period_date']:
            continue
            
        last_period = player['last_period_date']
        diff_days = (today - last_period).days
        
        if diff_days >= 0:
            day_in_cycle = (diff_days % player['cycle_length']) + 1
            phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
            
            # Détection des jours à risque de fatigue
            historical_fatigue = player['daily_fatigue'].get(str(day_in_cycle), 3)
            
            if historical_fatigue >= 4:
                alerts.append({
                    'player': player['name'],
                    'phase': phase,
                    'day_in_cycle': day_in_cycle,
                    'fatigue_level': historical_fatigue,
                    'message': "Jour historiquement associé à une fatigue importante",
                    'alert_color': "#e74c3c",
                    'icon': "🔥",
                    'priority': 1
                })
            elif historical_fatigue >= 3:
                alerts.append({
                    'player': player['name'],
                    'phase': phase,
                    'day_in_cycle': day_in_cycle,
                    'fatigue_level': historical_fatigue,
                    'message': "Jour historiquement associé à une fatigue modérée",
                    'alert_color': "#f39c12",
                    'icon': "⚠️",
                    'priority': 2
                })
    
    # Affichage des alertes
    if not alerts:
        st.success("✅ Aucune alerte significative pour aujourd'hui")
    else:
        # Tri des alertes par priorité
        alerts.sort(key=lambda x: x['priority'])
        
        for alert in alerts:
            with st.container():
                col1, col2 = st.columns([1, 20])
                with col1:
                    st.markdown(f"<div style='font-size: 24px;'>{alert['icon']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style='
                        padding: 15px;
                        border-radius: 10px;
                        background-color: #f8f9fa;
                        border-left: 5px solid {alert['alert_color']};
                        margin-bottom: 15px;
                    '>
                        <div style='font-weight: bold; font-size: 16px;'>
                            {alert['player']} - {get_phase_name_fr(alert['phase'])} (Jour {alert['day_in_cycle']})
                        </div>
                        <div style='
                            display: inline-block;
                            background-color: {alert['alert_color']};
                            color: white;
                            padding: 3px 10px;
                            border-radius: 15px;
                            margin: 8px 0;
                            font-size: 14px;
                        '>
                            Fatigue historique: {alert['fatigue_level']}/5
                        </div>
                        <div style='color: #555; font-size: 14px;'>
                            {alert['message']}
                        </div>
                        <div style='margin-top: 5px; font-size: 13px;'>
                            Recommandation: Surveillez la joueuse et adaptez l'entraînement si nécessaire
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Section d'analyse détaillée par joueuse
    st.subheader("🔍 Analyse détaillée par joueuse")
    
    if not st.session_state.players:
        st.info("ℹ️ Aucune joueuse enregistrée")
        return
    
    for player in st.session_state.players:
        with st.expander(f"📊 Analyse complète pour {player['name']}", expanded=False):
            
            # Affichage des informations de base
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📅 Dernières règles**")
                if player['last_period_date']:
                    st.info(player['last_period_date'].strftime("%d/%m/%Y"))
                else:
                    st.warning("Non renseigné")
                
            with col2:
                st.markdown("**🔄 Cycle actuel**")
                if player['last_period_date']:
                    diff_days = (today - player['last_period_date']).days
                    day_in_cycle = (diff_days % player['cycle_length']) + 1
                    st.info(f"Jour {day_in_cycle}/{player['cycle_length']}")
                else:
                    st.warning("Indisponible")
            
            # Graphique de fatigue quotidienne
            st.markdown("**📈 Profil de fatigue quotidien**")
            
            days = list(range(1, player['cycle_length'] + 1))
            fatigue_levels = [player['daily_fatigue'].get(str(day), 3) for day in days]
            phases = [get_cycle_phase(day, player['cycle_length'], player['period_duration']) for day in days]
            
            # Création du graphique
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(days, fatigue_levels, 'o-', color='#3498db', linewidth=2)
            
            # Ajouter des zones colorées pour les phases
            phase_colors = {
                'menstruation': '#e74c3c',
                'follicular': '#f39c12',
                'ovulation': '#27ae60',
                'luteal': '#8e44ad'
            }
            
            current_phase = None
            phase_start = 1
            for i, day in enumerate(days):
                if phases[i] != current_phase or i == len(days) - 1:
                    if current_phase:
                        phase_end = day - 0.5 if i < len(days) - 1 else day
                        ax.axvspan(phase_start, phase_end, alpha=0.2, color=phase_colors[current_phase])
                        ax.text((phase_start + phase_end) / 2, 5.2, 
                                get_phase_name_fr(current_phase), 
                                ha='center', va='center', 
                                color=phase_colors[current_phase], 
                                fontweight='bold')
                    current_phase = phases[i]
                    phase_start = day - 0.5
            
            ax.set_ylim(0.5, 5.5)
            ax.set_xlim(0.5, player['cycle_length'] + 0.5)
            ax.set_xlabel('Jour du cycle')
            ax.set_ylabel('Niveau de fatigue')
            ax.set_title('Profil de fatigue quotidien')
            ax.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Recommandations spécifiques
            st.markdown("**🎯 Recommandations personnalisées**")
            
            if not player['last_period_date']:
                st.warning("Données insuffisantes pour générer des recommandations")
                continue
            
            current_phase = get_cycle_phase(day_in_cycle, player['cycle_length'], player['period_duration'])
            historical_fatigue = player['daily_fatigue'].get(str(day_in_cycle), 3)
            
            if historical_fatigue >= 4:
                st.warning(f"**Adaptation recommandée pendant la phase {get_phase_name_fr(current_phase)}**")
                
                recommendations = {
                    'menstruation': [
                        "Réduire l'intensité des exercices physiques de 30%",
                        "Privilégier les exercices techniques légers",
                        "Augmenter les temps de récupération entre les séries",
                        "Surveiller l'hydratation et l'apport en fer"
                    ],
                    'follicular': [
                        "Intensité progressive sur la semaine",
                        "Travail technique approfondi",
                        "Exercices d'endurance à intensité modérée"
                    ],
                    'ovulation': [
                        "Entraînements intenses possibles",
                        "Travail sur l'explosivité et la puissance",
                        "Exercices compétitifs et matchs d'entraînement"
                    ],
                    'luteal': [
                        "Maintenir une intensité modérée",
                        "Focus sur la stratégie d'équipe",
                        "Exercices de coordination et de précision"
                    ]
                }
                
                for rec in recommendations[current_phase]:
                    st.markdown(f"- {rec}")
                
                st.markdown(f"*Basé sur un niveau de fatigue historique de {historical_fatigue}/5 pour ce jour*")
            else:
                st.success("Aucune adaptation spécifique nécessaire pour la phase actuelle")
            
            # Historique des entrées récentes
            st.markdown("**📝 Dernières observations**")
            player_entries = sorted(
                [e for e in st.session_state.daily_entries if e['player_id'] == player['id']],
                key=lambda x: x['date'],
                reverse=True
            )[:5]
            
            if player_entries:
                for entry in player_entries:
                    with st.container():
                        entry_date = entry['date'].strftime("%d/%m/%Y")
                        st.markdown(f"**{entry_date}** - Énergie: {entry['energy_level']}/5 - Fatigue: {entry['fatigue_level']}/5")
                        if entry['notes']:
                            st.caption(f"Notes: {entry['notes']}")
                        st.markdown("---")
            else:
                st.info("Aucune entrée enregistrée pour cette joueuse")

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

# Sauvegarde automatique
save_data()
