import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="HotelPulse AI | Accor Paris Guest Sentiment & Action Engine",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern SaaS styling, KPI cards, and priority badges
st.markdown(
    """
    <style>
    /* Main background and typography adjustments */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }
    
    /* KPI Metric Card Styling */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        height: 135px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card-alert {
        background-color: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 6px solid #e11d48;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 6px rgba(225, 29, 72, 0.06);
        height: 135px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 2.0rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-subtext-positive {
        font-size: 0.85rem;
        font-weight: 600;
        color: #16a34a;
    }
    .kpi-subtext-neutral {
        font-size: 0.85rem;
        font-weight: 500;
        color: #475569;
    }
    .kpi-alert-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #be123c;
        line-height: 1.35;
    }
    .kpi-alert-subtext {
        font-size: 0.82rem;
        font-weight: 500;
        color: #9f1239;
    }

    /* Priority Action Matrix Cards */
    .action-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.04);
    }
    .action-high {
        border-left: 7px solid #ef4444;
    }
    .action-medium {
        border-left: 7px solid #f59e0b;
    }
    .action-low {
        border-left: 7px solid #10b981;
    }
    .action-addressed {
        border-left: 7px solid #64748b;
        background-color: #f8fafc;
        opacity: 0.88;
    }

    /* Priority & Department Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-right: 8px;
    }
    .badge-high {
        background-color: #fee2e2;
        color: #b91c1c;
    }
    .badge-medium {
        background-color: #fef3c7;
        color: #b45309;
    }
    .badge-low {
        background-color: #d1fae5;
        color: #047857;
    }
    .badge-dept {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    .badge-status-open {
        background-color: #f1f5f9;
        color: #475569;
    }
    .badge-status-assigned {
        background-color: #e0e7ff;
        color: #4338ca;
    }
    .badge-status-done {
        background-color: #dcfce7;
        color: #15803d;
    }

    .action-headline {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0f172a;
        margin-top: 12px;
        margin-bottom: 8px;
    }
    .action-meta {
        font-size: 0.86rem;
        color: #64748b;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Liste des hôtels Accor réels à Paris
ACCOR_HOTELS = [
    "Pullman Paris Tour Eiffel",
    "Hôtel Novotel Paris les Halles",
    "Sofitel Paris Le Faubourg",
    "Hôtel Mercure Paris Centre Tour Eiffel",
    "Hôtel ibis Paris Tour Eiffel Cambronne",
]

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "action_states" not in st.session_state:
    st.session_state.action_states = {
        hotel: {
            "card_1": {"status": "Open", "assigned_to": None},
            "card_2": {"status": "Open", "assigned_to": None},
            "card_3": {"status": "Open", "assigned_to": None},
        }
        for hotel in ACCOR_HOTELS
    }


# ==========================================
# MOCK DATA GENERATOR (ACCOR REAL HOTELS)
# ==========================================
def get_hotel_configuration(hotel_name: str, date_range: str):
    """Returns realistic KPI metrics, action matrix items, and chart data per Accor hotel."""
    multiplier = 1.0 if date_range == "Last 30 Days" else (2.5 if date_range == "Q3 2026" else 0.6)

    if hotel_name == "Pullman Paris Tour Eiffel":
        total_reviews = int(620 * multiplier)
        kpis = {
            "score": "4.6 / 5.0",
            "trend": "+0.4 vs prior period",
            "total_reviews": total_reviews,
            "languages_count": 4,
            "alert_title": "⚠️ Spike sur les ascenseurs aux heures de pointe",
            "alert_sub": "28 mentions négatives entre 8h30 et 10h (attente > 10 min)",
        }
        actions = [
            {
                "id": "card_1",
                "priority": "High Priority",
                "priority_level": "high",
                "department": "Maintenance",
                "dept_head": "Marc Dubois (Directeur Technique)",
                "recommendation": "Reprogrammer la régulation des ascenseurs de la tour aux heures de petit-déjeuner.",
                "impact": "Gain estimé de +0.20 sur la note globale | Aspect: Temps d'attente Ascenseur (3.2/5.0)",
                "languages_affected": "English (14), French (9), German (5)",
            },
            {
                "id": "card_2",
                "priority": "Medium Priority",
                "priority_level": "medium",
                "department": "Front Desk",
                "dept_head": "Sophie Laurent (Cheffe de Réception)",
                "recommendation": "Activer la ligne enregistrement express ALL (Accor Live Limitless) les jours de congrès.",
                "impact": "Gain estimé de +0.15 sur la note globale | Aspect: Rapidité Check-in (3.6/5.0)",
                "languages_affected": "English (10), Spanish (6)",
            },
            {
                "id": "card_3",
                "priority": "Low Priority",
                "priority_level": "low",
                "department": "F&B",
                "dept_head": "Antoine Mercier (Responsable Restauration - FR/AME)",
                "recommendation": "Augmenter le réapprovisionnement des options sans gluten sur le buffet Frame.",
                "impact": "Gain estimé de +0.05 sur la note globale | Aspect: Variété Buffet (4.1/5.0)",
                "languages_affected": "French (4), English (3)",
            },
        ]
        dept_sentiment = pd.DataFrame({
            "Department": ["Housekeeping", "F&B", "Front Desk", "Maintenance"],
            "Positive (%)": [92, 84, 76, 61],
            "Neutral (%)": [5, 10, 12, 14],
            "Negative (%)": [3, 6, 12, 25],
        })
        aspect_scores = pd.DataFrame({
            "Aspect": ["Vue Tour Eiffel", "Propreté", "Wi-Fi Haut Débit", "Service Bar", "Check-in Speed", "Attente Ascenseurs"],
            "Score": [4.9, 4.8, 4.7, 4.3, 3.6, 3.2],
            "Department": ["Housekeeping", "Housekeeping", "Maintenance", "F&B", "Front Desk", "Maintenance"],
        })

    elif hotel_name == "Hôtel Novotel Paris les Halles":
        total_reviews = int(510 * multiplier)
        kpis = {
            "score": "4.6 / 5.0",
            "trend": "+0.2 vs prior period",
            "total_reviews": total_reviews,
            "languages_count": 4,
            "alert_title": "⚠️ File d'attente enregistrement l'après-midi",
            "alert_sub": "31 retours négatifs signalant plus de 20 min d'attente vers 15h",
        }
        actions = [
            {
                "id": "card_1",
                "priority": "High Priority",
                "priority_level": "high",
                "department": "Front Desk",
                "dept_head": "Claire Moreau (Cheffe de Réception)",
                "recommendation": "Renforcer l'équipe d'accueil à l'arrivée des flux RER/Métro entre 14h30 et 17h.",
                "impact": "Gain estimé de +0.22 sur la note globale | Aspect: Fluidité Arrivée (3.1/5.0)",
                "languages_affected": "English (15), French (10), German (6)",
            },
            {
                "id": "card_2",
                "priority": "Medium Priority",
                "priority_level": "medium",
                "department": "Maintenance",
                "dept_head": "Jean-Luc Bernard (Responsable Technique)",
                "recommendation": "Contrôler l'isolation phonique des fenêtres donnant sur la Place Marguerite de Navarre.",
                "impact": "Gain estimé de +0.10 sur la note globale | Aspect: Insonorisation (3.5/5.0)",
                "languages_affected": "French (8), German (5)",
            },
            {
                "id": "card_3",
                "priority": "Low Priority",
                "priority_level": "low",
                "department": "F&B",
                "dept_head": "Julien Petit (Manager Jardin Privé)",
                "recommendation": "Proposer des laits végétaux (avoine/amande) en accès libre au petit-déjeuner.",
                "impact": "Gain estimé de +0.07 sur la note globale | Aspect: Offre Boissons Chaudes (4.0/5.0)",
                "languages_affected": "English (5), Spanish (3)",
            },
        ]
        dept_sentiment = pd.DataFrame({
            "Department": ["Housekeeping", "F&B", "Maintenance", "Front Desk"],
            "Positive (%)": [88, 80, 65, 52],
            "Neutral (%)": [8, 12, 15, 16],
            "Negative (%)": [4, 8, 20, 32],
        })
        aspect_scores = pd.DataFrame({
            "Aspect": ["Emplacement Châtelet", "Propreté", "Wi-Fi Connectivity", "Jardin & Terrasse", "Bruit Extérieur", "Check-in Speed"],
            "Score": [4.9, 4.7, 4.5, 4.4, 3.5, 3.1],
            "Department": ["Front Desk", "Housekeeping", "Maintenance", "F&B", "Maintenance", "Front Desk"],
        })

    elif hotel_name == "Sofitel Paris Le Faubourg":
        total_reviews = int(340 * multiplier)
        kpis = {
            "score": "4.6 / 5.0",
            "trend": "+0.1 vs prior period",
            "total_reviews": total_reviews,
            "languages_count": 4,
            "alert_title": "⚠️ Délais de réponse Conciergerie / Voiturier",
            "alert_sub": "12 demandes de voiturier ralenties lors des pics de la Fashion Week / Shopping",
        }
        actions = [
            {
                "id": "card_1",
                "priority": "High Priority",
                "priority_level": "high",
                "department": "Front Desk",
                "dept_head": "Alexandre de Saint-Germain (Chef Concierge)",
                "recommendation": "Optimiser le service voiturier Rue Boissy d'Anglas pendant les départs du matin.",
                "impact": "Gain estimé de +0.15 sur la note globale | Aspect: Service Voiturier/Bagages (3.7/5.0)",
                "languages_affected": "English (7), Spanish (4)",
            },
            {
                "id": "card_2",
                "priority": "Medium Priority",
                "priority_level": "medium",
                "department": "F&B",
                "dept_head": "Chef Jérôme Charles (Restaurant Blossom)",
                "recommendation": "Élargir les horaires de service du Room Service de nuit.",
                "impact": "Gain estimé de +0.08 sur la note globale | Aspect: Room Service Nocturne (3.9/5.0)",
                "languages_affected": "English (5), French (3)",
            },
            {
                "id": "card_3",
                "priority": "Low Priority",
                "priority_level": "low",
                "department": "Housekeeping",
                "dept_head": "Marie-Thérèse Blanc (Gouvernante Générale)",
                "recommendation": "Ajuster l'intensité des parfums d'ambiance en chambre sur demande des clients.",
                "impact": "Gain estimé de +0.04 sur la note globale | Aspect: Confort Sensorielles (4.2/5.0)",
                "languages_affected": "German (3), French (2)",
            },
        ]
        dept_sentiment = pd.DataFrame({
            "Department": ["Housekeeping", "Front Desk", "F&B", "Maintenance"],
            "Positive (%)": [94, 88, 85, 78],
            "Neutral (%)": [4, 7, 10, 14],
            "Negative (%)": [2, 5, 5, 8],
        })
        aspect_scores = pd.DataFrame({
            "Aspect": ["Literie MyBed", "Service Conciergerie", "Gastronomie Blossom", "Calme Rue Boissy", "Service Voiturier", "Room Service Nuit"],
            "Score": [4.9, 4.8, 4.7, 4.6, 3.7, 3.9],
            "Department": ["Housekeeping", "Front Desk", "F&B", "Maintenance", "Front Desk", "F&B"],
        })

    elif hotel_name == "Hôtel Mercure Paris Centre Tour Eiffel":
        total_reviews = int(480 * multiplier)
        kpis = {
            "score": "3.9 / 5.0",
            "trend": "+0.2 vs prior period",
            "total_reviews": total_reviews,
            "languages_count": 4,
            "alert_title": "⚠️ Température des chambres (Climatisation)",
            "alert_sub": "24 signalements négatifs sur le réglage chaud/froid au 4ème étage",
        }
        actions = [
            {
                "id": "card_1",
                "priority": "High Priority",
                "priority_level": "high",
                "department": "Maintenance",
                "dept_head": "Gérard Lefebvre (Chef Électricien & HVAC)",
                "recommendation": "Purger et calibrer les vannes de climatisation des chambres côté Rue Jean Rey.",
                "impact": "Gain estimé de +0.28 sur la note globale | Aspect: Climatisation Chambre (2.9/5.0)",
                "languages_affected": "English (12), German (7), French (5)",
            },
            {
                "id": "card_2",
                "priority": "Medium Priority",
                "priority_level": "medium",
                "department": "Front Desk",
                "dept_head": "Emmanuelle Vasseur (Responsable Accueil)",
                "recommendation": "Améliorer la signalétique d'accès aux ascenseurs depuis le hall secondaire.",
                "impact": "Gain estimé de +0.10 sur la note globale | Aspect: Orientation Client (3.4/5.0)",
                "languages_affected": "Spanish (6), English (5)",
            },
            {
                "id": "card_3",
                "priority": "Low Priority",
                "priority_level": "low",
                "department": "F&B",
                "dept_head": "David Perrin (Responsable Petit-Déjeuner)",
                "recommendation": "Réorganiser le réapprovisionnement des viennoiseries chaudes aux heures d'affluence.",
                "impact": "Gain estimé de +0.06 sur la note globale | Aspect: Fraîcheur Buffet (3.8/5.0)",
                "languages_affected": "French (4), German (3)",
            },
        ]
        dept_sentiment = pd.DataFrame({
            "Department": ["Housekeeping", "F&B", "Front Desk", "Maintenance"],
            "Positive (%)": [82, 74, 68, 48],
            "Neutral (%)": [10, 14, 15, 18],
            "Negative (%)": [8, 12, 17, 34],
        })
        aspect_scores = pd.DataFrame({
            "Aspect": ["Proximité Tour Eiffel", "Propreté", "Wi-Fi", "Qualité Petit-Déjeuner", "Signalétique", "Climatisation"],
            "Score": [4.8, 4.4, 4.2, 3.8, 3.4, 2.9],
            "Department": ["Front Desk", "Housekeeping", "Maintenance", "F&B", "Front Desk", "Maintenance"],
        })

    else: # Hôtel ibis Paris Tour Eiffel Cambronne
        total_reviews = int(580 * multiplier)
        kpis = {
            "score": "3.8 / 5.0",
            "trend": "+0.1 vs prior period",
            "total_reviews": total_reviews,
            "languages_count": 4,
            "alert_title": "⚠️ Dimensionnement des salles de bain",
            "alert_sub": "36 remarques sur l'espace restreint des cabines de douche",
        }
        actions = [
            {
                "id": "card_1",
                "priority": "High Priority",
                "priority_level": "high",
                "department": "Housekeeping",
                "dept_head": "Nathalie Caron (Gouvernante)",
                "recommendation": "Remplacer les distributeurs de savon défectueux signalés dans le bâtiment Rue Cambronne.",
                "impact": "Gain estimé de +0.18 sur la note globale | Aspect: Équipement Salle de Bain (3.0/5.0)",
                "languages_affected": "French (14), English (12), German (10)",
            },
            {
                "id": "card_2",
                "priority": "Medium Priority",
                "priority_level": "medium",
                "department": "Maintenance",
                "dept_head": "Luc Rossi (Maintenance Bâtiment)",
                "recommendation": "Vérifier la fermeture automatique des portes de couloir (bruit nocturne).",
                "impact": "Gain estimé de +0.14 sur la note globale | Aspect: Isolation Acoustique Couloir (3.2/5.0)",
                "languages_affected": "German (9), French (7)",
            },
            {
                "id": "card_3",
                "priority": "Low Priority",
                "priority_level": "low",
                "department": "F&B",
                "dept_head": "Karim Haddad (Bar & Snack Lead)",
                "recommendation": "Ajouter des prises de recharge supplémentaires près du comptoir bar/lounge.",
                "impact": "Gain estimé de +0.05 sur la note globale | Aspect: Confort Lounge (3.9/5.0)",
                "languages_affected": "English (6), Spanish (3)",
            },
        ]
        dept_sentiment = pd.DataFrame({
            "Department": ["Housekeeping", "Front Desk", "F&B", "Maintenance"],
            "Positive (%)": [79, 75, 69, 45],
            "Neutral (%)": [11, 13, 16, 20],
            "Negative (%)": [10, 12, 15, 35],
        })
        aspect_scores = pd.DataFrame({
            "Aspect": ["Accès Métro Cambronne", "Literie Sweet Bed", "Wi-Fi Gratuit", "Bar & Snack 24/7", "Bruit Couloir", "Taille Salle de Bain"],
            "Score": [4.7, 4.3, 4.1, 3.9, 3.2, 3.0],
            "Department": ["Front Desk", "Housekeeping", "Maintenance", "F&B", "Maintenance", "Housekeeping"],
        })

    lang_distribution = pd.DataFrame({
        "Language": ["English", "French", "German", "Spanish"],
        "Share (%)": [42, 32, 14, 12],
        "Review Count": [
            int(total_reviews * 0.42),
            int(total_reviews * 0.32),
            int(total_reviews * 0.14),
            int(total_reviews * 0.12),
        ],
    })

    return kpis, actions, dept_sentiment, lang_distribution, aspect_scores


def get_multilingual_reviews(hotel_name: str) -> pd.DataFrame:
    """Generates realistic multilingual guest reviews tailored to specific Accor Paris hotels."""
    today = datetime.today()
    
    if hotel_name == "Pullman Paris Tour Eiffel":
        raw_reviews = [
            {
                "Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "Platform": "TripAdvisor",
                "Original Language": "French 🇫🇷",
                "Original Text": "La vue sur la Tour Eiffel depuis le 8ème étage est époustouflante ! Seul bémol : 15 minutes d'attente pour l'ascenseur à 9h du matin.",
                "Auto-Translated English Text": "The Eiffel Tower view from the 8th floor is breathtaking! Only downside: 15 minutes wait for the elevator at 9 AM.",
                "Extracted Aspect": "Attente Ascenseurs",
                "Department": "Maintenance",
                "Sentiment": "Negative",
            },
            {
                "Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "Platform": "Booking.com",
                "Original Language": "English 🇬🇧",
                "Original Text": "Immaculate room and friendly staff. Check-in was fast thanks to the ALL Accor priority desk.",
                "Auto-Translated English Text": "Immaculate room and friendly staff. Check-in was fast thanks to the ALL Accor priority desk.",
                "Extracted Aspect": "Check-in Speed",
                "Department": "Front Desk",
                "Sentiment": "Positive",
            },
            {
                "Date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "Platform": "Google Reviews",
                "Original Language": "German 🇩🇪",
                "Original Text": "Tolles Frühstück im Restaurant Frame, aber die Aufzüge sind morgens extrem überlastet.",
                "Auto-Translated English Text": "Great breakfast at Frame restaurant, but elevators are extremely congested in the morning.",
                "Extracted Aspect": "Attente Ascenseurs",
                "Department": "Maintenance",
                "Sentiment": "Negative",
            },
        ]
    elif hotel_name == "Hôtel Novotel Paris les Halles":
        raw_reviews = [
            {
                "Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "Platform": "TripAdvisor",
                "Original Language": "French 🇫🇷",
                "Original Text": "Emplacement imbattable à Châtelet. Par contre, file d'attente interminable à la réception vers 15h30 (une seule hôtesse).",
                "Auto-Translated English Text": "Unbeatable location at Châtelet. However, endless queue at reception around 3:30 PM (only one desk agent).",
                "Extracted Aspect": "Fluidité Arrivée",
                "Department": "Front Desk",
                "Sentiment": "Negative",
            },
            {
                "Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "Platform": "Google Reviews",
                "Original Language": "German 🇩🇪",
                "Original Text": "Zimmer sehr sauber und modern. Das Frühstück im Innenhof ist traumhaft.",
                "Auto-Translated English Text": "Rooms very clean and modern. Breakfast in the courtyard is delightful.",
                "Extracted Aspect": "Jardin & Terrasse",
                "Department": "F&B",
                "Sentiment": "Positive",
            },
            {
                "Date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
                "Platform": "Booking.com",
                "Original Language": "Spanish 🇪🇸",
                "Original Text": "Excelente atención en recepción, pero falta más variedad de leches vegetales en el buffet.",
                "Auto-Translated English Text": "Excellent reception service, but missing more plant milk varieties at the buffet.",
                "Extracted Aspect": "Offre Boissons Chaudes",
                "Department": "F&B",
                "Sentiment": "Neutral",
            },
        ]
    elif hotel_name == "Sofitel Paris Le Faubourg":
        raw_reviews = [
            {
                "Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "Platform": "Booking.com",
                "Original Language": "English 🇬🇧",
                "Original Text": "The MyBed experience is unrivaled. Perfect sleep near Place de la Concorde. Concierge service was top-tier.",
                "Auto-Translated English Text": "The MyBed experience is unrivaled. Perfect sleep near Place de la Concorde. Concierge service was top-tier.",
                "Extracted Aspect": "Literie MyBed",
                "Department": "Housekeeping",
                "Sentiment": "Positive",
            },
            {
                "Date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "Platform": "TripAdvisor",
                "Original Language": "French 🇫🇷",
                "Original Text": "Magnifique séjour. Petit retard pour récupérer la voiture au voiturier lors du départ à 11h.",
                "Auto-Translated English Text": "Magnificent stay. Slight delay retrieving the car from valet during 11 AM checkout.",
                "Extracted Aspect": "Service Voiturier",
                "Department": "Front Desk",
                "Sentiment": "Neutral",
            },
        ]
    elif hotel_name == "Hôtel Mercure Paris Centre Tour Eiffel":
        raw_reviews = [
            {
                "Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "Platform": "Google Reviews",
                "Original Language": "German 🇩🇪",
                "Original Text": "Die Klimaanlage im 4. Stock war sehr laut und hat das Zimmer kaum gekühlt.",
                "Auto-Translated English Text": "The air conditioning on the 4th floor was very noisy and barely cooled the room.",
                "Extracted Aspect": "Climatisation",
                "Department": "Maintenance",
                "Sentiment": "Negative",
            },
            {
                "Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "Platform": "Booking.com",
                "Original Language": "English 🇬🇧",
                "Original Text": "Superb location just minutes away from the Eiffel Tower! Room was very clean.",
                "Auto-Translated English Text": "Superb location just minutes away from the Eiffel Tower! Room was very clean.",
                "Extracted Aspect": "Proximité Tour Eiffel",
                "Department": "Front Desk",
                "Sentiment": "Positive",
            },
        ]
    else: # Ibis Cambronne
        raw_reviews = [
            {
                "Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "Platform": "TripAdvisor",
                "Original Language": "French 🇫🇷",
                "Original Text": "Lit Sweet Bed très confortable, mais la cabine de douche est vraiment étroite.",
                "Auto-Translated English Text": "Very comfortable Sweet Bed, but the shower cabin is really tight.",
                "Extracted Aspect": "Taille Salle de Bain",
                "Department": "Housekeeping",
                "Sentiment": "Neutral",
            },
            {
                "Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "Platform": "Google Reviews",
                "Original Language": "German 🇩🇪",
                "Original Text": "Türen im Flur knallen nachts lauthals zu. Bitte Türschließer reparieren.",
                "Auto-Translated English Text": "Corridor doors slam loudly at night. Please fix the door closers.",
                "Extracted Aspect": "Bruit Couloir",
                "Department": "Maintenance",
                "Sentiment": "Negative",
            },
        ]

    return pd.DataFrame(raw_reviews)


# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("## 🏨 HotelPulse AI")
    st.caption("Accor Paris Multilingual ABSA Engine")
    st.markdown("---")

    # 1. Hotel Selector Dropdown (Accor Real Hotels)
    selected_hotel = st.selectbox(
        "📍 Sélectionner un établissement Accor",
        options=ACCOR_HOTELS,
        index=0,
    )

    # 2. Date Range Filter Dropdown
    selected_date_range = st.selectbox(
        "📅 Date Range",
        options=["Last 30 Days", "Q3 2026", "Custom Range"],
        index=0,
    )

    if selected_date_range == "Custom Range":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.date_input("Start", datetime.today() - timedelta(days=14))
        with col_d2:
            st.date_input("End", datetime.today())

    st.markdown("---")
    st.markdown("**🌐 Review Platforms**")

    # 3. Platform Filter Checkboxes
    plat_google = st.checkbox("Google Reviews", value=True)
    plat_tripadvisor = st.checkbox("TripAdvisor", value=True)
    plat_booking = st.checkbox("Booking.com", value=True)

    selected_platforms = []
    if plat_google:
        selected_platforms.append("Google Reviews")
    if plat_tripadvisor:
        selected_platforms.append("TripAdvisor")
    if plat_booking:
        selected_platforms.append("Booking.com")

    st.markdown("---")
    st.markdown("**🤖 AI Pipeline Status**")
    st.success("● XLM-RoBERTa ABSA Active")
    st.caption("Auto-Translation: Neural MT v4.2\nLanguages: EN, FR, DE, ES")

    if st.button("🔄 Reset Demo Action States", use_container_width=True):
        for h in st.session_state.action_states:
            for c in st.session_state.action_states[h]:
                st.session_state.action_states[h][c] = {"status": "Open", "assigned_to": None}
        st.toast("All Priority Action cards reset to Open!", icon="🔄")
        st.rerun()


# ==========================================
# LOAD DATA BASED ON FILTERS
# ==========================================
if not selected_platforms:
    st.warning("Please select at least one review platform in the sidebar to display analytics.")
    st.stop()

kpis, actions, dept_sentiment, lang_distribution, aspect_scores = get_hotel_configuration(
    selected_hotel, selected_date_range
)
reviews_df = get_multilingual_reviews(selected_hotel)

platform_ratio = len(selected_platforms) / 3.0
displayed_review_count = max(1, int(kpis["total_reviews"] * platform_ratio))


# ==========================================
# HEADER & TOP METRICS KPI CARDS
# ==========================================
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.title("HotelPulse AI: Accor Guest Sentiment & Action Engine")
    st.markdown(
        f"**Établissement:** `{selected_hotel}` &nbsp;|&nbsp; **Période:** `{selected_date_range}` &nbsp;|&nbsp; "
        f"**Canaux actifs:** `{', '.join(selected_platforms)}`"
    )
with head_col2:
    st.markdown("<div style='text-align: right; padding-top: 18px;'>", unsafe_allow_html=True)
    st.button(
        "📥 Export Weekly Executive PDF",
        type="secondary",
        use_container_width=True,
        on_click=lambda: st.toast("Executive Weekly Brief queued for export!", icon="📄"),
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# Top KPI Cards
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Overall Guest Satisfaction Score</div>
            <div class="kpi-value">⭐ {kpis["score"]}</div>
            <div class="kpi-subtext-positive">▲ {kpis["trend"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Reviews Analyzed</div>
            <div class="kpi-value">{displayed_review_count} Reviews</div>
            <div class="kpi-subtext-neutral">🌍 Analyzed across {kpis["languages_count"]} languages (EN, FR, DE, ES)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col3:
    st.markdown(
        f"""
        <div class="kpi-card-alert">
            <div class="kpi-title" style="color: #9f1239;">Urgent Attention Alerts</div>
            <div class="kpi-alert-value">{kpis["alert_title"]}</div>
            <div class="kpi-alert-subtext">{kpis["alert_sub"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


# ==========================================
# MAIN NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(
    [
        "🔥 Priority Action Matrix",
        "🏢 Departmental Deep-Dive & Sentiment Analysis",
        "🌍 Multilingual Feed & Auto-Translation",
    ]
)


# ------------------------------------------
# TAB 1: PRIORITY ACTION MATRIX
# ------------------------------------------
with tab1:
    st.subheader("Weekly Priority Action Matrix")
    st.markdown(
        "Recommandations opérationnelles générées par IA via le regroupement d'avis clients **Aspect-Based Sentiment Analysis (ABSA)**."
    )

    hotel_states = st.session_state.action_states[selected_hotel]
    completed_count = sum(1 for v in hotel_states.values() if v["status"] == "Addressed")
    st.progress(
        completed_count / len(actions),
        text=f"Weekly Resolution Progress: {completed_count} of {len(actions)} priority actions addressed",
    )

    for idx, item in enumerate(actions):
        card_id = item["id"]
        current_state = hotel_states[card_id]["status"]
        assigned_person = hotel_states[card_id]["assigned_to"]

        if current_state == "Addressed":
            border_class = "action-addressed"
        elif item["priority_level"] == "high":
            border_class = "action-high"
        elif item["priority_level"] == "medium":
            border_class = "action-medium"
        else:
            border_class = "action-low"

        priority_badge_class = f"badge-{item['priority_level']}"

        if current_state == "Addressed":
            status_badge = '<span class="badge badge-status-done">✓ Addressed</span>'
        elif assigned_person:
            status_badge = f'<span class="badge badge-status-assigned">👤 Assigned: {assigned_person}</span>'
        else:
            status_badge = '<span class="badge badge-status-open">● Pending Action</span>'

        st.markdown(
            f"""
            <div class="action-card {border_class}">
                <div>
                    <span class="badge {priority_badge_class}">{item["priority"]}</span>
                    <span class="badge badge-dept">🏢 {item["department"]}</span>
                    {status_badge}
                </div>
                <div class="action-headline">Action {idx + 1}: "{item["recommendation"]}"</div>
                <div class="action-meta">
                    <strong>📊 Impact projeté:</strong> {item["impact"]} &nbsp;|&nbsp;
                    <strong>🗣️ Langues impactées:</strong> {item["languages_affected"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_col1, btn_col2, btn_col3 = st.columns([1.3, 1.8, 4])
        with btn_col1:
            is_done = current_state == "Addressed"
            if st.button(
                "✓ Mark as Addressed" if not is_done else "↺ Reopen Action",
                key=f"btn_done_{selected_hotel}_{card_id}",
                type="primary" if not is_done else "secondary",
                use_container_width=True,
            ):
                new_status = "Open" if is_done else "Addressed"
                st.session_state.action_states[selected_hotel][card_id]["status"] = new_status
                st.toast(
                    f"Action {idx + 1} ({item['department']}) marquée comme {new_status}!",
                    icon="✅" if new_status == "Addressed" else "🔄",
                )
                st.rerun()

        with btn_col2:
            if st.button(
                f"📋 Assigner à {item['dept_head'].split(' ')[0]}",
                key=f"btn_assign_{selected_hotel}_{card_id}",
                use_container_width=True,
                disabled=(current_state == "Addressed"),
            ):
                st.session_state.action_states[selected_hotel][card_id]["assigned_to"] = item["dept_head"]
                st.toast(
                    f"Notification transmise à {item['dept_head']} via Teams & Email!",
                    icon="📨",
                )
                st.rerun()

        st.markdown("<hr style='margin: 12px 0 22px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)


# ------------------------------------------
# TAB 2: DEPARTMENTAL DEEP-DIVE & SENTIMENT
# ------------------------------------------
with tab2:
    st.subheader("Analyse de Sentiment par Département et Aspects Operatifs")
    st.markdown(
        "Répartition granulaire du sentiment des clients par service et évaluation des aspects clés identifiés par IA."
    )

    chart_col1, chart_col2 = st.columns([1.4, 1])

    with chart_col1:
        dept_melted = dept_sentiment.melt(
            id_vars="Department",
            value_vars=["Positive (%)", "Neutral (%)", "Negative (%)"],
            var_name="Sentiment",
            value_name="Percentage",
        )
        fig_dept = px.bar(
            dept_melted,
            x="Percentage",
            y="Department",
            color="Sentiment",
            orientation="h",
            title="Répartition du Sentiment par Département (%)",
            text="Percentage",
            color_discrete_map={
                "Positive (%)": "#10b981",
                "Neutral (%)": "#94a3b8",
                "Negative (%)": "#ef4444",
            },
        )
        fig_dept.update_traces(texttemplate="%{text}%", textposition="inside")
        fig_dept.update_layout(
            barmode="stack",
            xaxis_title="Part des mentions (%)",
            yaxis_title="",
            legend_title="Sentiment",
            height=370,
            margin=dict(l=10, r=10, t=45, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    with chart_col2:
        fig_lang = px.pie(
            lang_distribution,
            names="Language",
            values="Share (%)",
            hole=0.52,
            title="Répartition des Avis par Langue",
            color="Language",
            color_discrete_map={
                "English": "#2563eb",
                "French": "#0ea5e9",
                "German": "#f59e0b",
                "Spanish": "#10b981",
            },
        )
        fig_lang.update_traces(
            textposition="inside",
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Part: %{value}%<extra></extra>",
        )
        fig_lang.update_layout(
            height=370,
            margin=dict(l=10, r=10, t=45, b=10),
            showlegend=True,
        )
        st.plotly_chart(fig_lang, use_container_width=True)

    st.markdown("---")

    st.subheader("Évaluation Granulaire des Aspects Clés (/ 5.0)")
    st.caption("Performance des aspects opérationnels évaluée par rapport à l'objectif cible (4.0/5.0).")

    aspect_sorted = aspect_scores.sort_values(by="Score", ascending=True).copy()

    def get_score_tier(score: float) -> str:
        if score >= 4.0:
            return "Satisfaisant (≥ 4.0)"
        elif score >= 3.5:
            return "À Surveiller (3.5 - 3.9)"
        else:
            return "Critique (< 3.5)"

    aspect_sorted["Tier"] = aspect_sorted["Score"].apply(get_score_tier)

    fig_aspects = px.bar(
        aspect_sorted,
        x="Score",
        y="Aspect",
        orientation="h",
        text="Score",
        color="Tier",
        color_discrete_map={
            "Satisfaisant (≥ 4.0)": "#10b981",
            "À Surveiller (3.5 - 3.9)": "#f59e0b",
            "Critique (< 3.5)": "#ef4444",
        },
        title="Notes Moyennes par Aspect vs Objectif de Performance (4.0)",
    )
    fig_aspects.add_vline(
        x=4.0,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Objectif Cible (4.0)",
        annotation_position="top right",
    )
    fig_aspects.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_aspects.update_layout(
        xaxis=dict(range=[0, 5.5], title="Note Moyenne (1-5)"),
        yaxis_title="",
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=45, b=10),
    )
    st.plotly_chart(fig_aspects, use_container_width=True)


# ------------------------------------------
# TAB 3: MULTILINGUAL FEED & AUTO-TRANSLATION
# ------------------------------------------
with tab3:
    st.subheader("Flux d'Avis Multilingues en Temps Réel")
    st.markdown(
        "Avis bruts collectés sur les plateformes, traduction automatique et étiquetage d'aspects par le modèle **XLM-RoBERTa**."
    )

    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    with f_col1:
        sentiment_filter = st.selectbox("Filtrer par sentiment", ["Tous", "Positive", "Neutral", "Negative"])
    with f_col2:
        dept_filter = st.selectbox("Filtrer par département", ["Tous", "Front Desk", "Housekeeping", "Maintenance", "F&B"])
    with f_col3:
        search_query = st.text_input("🔍 Rechercher un mot-clé", placeholder="ex: ascenseur, petit-déjeuner...")

    filtered_df = reviews_df.copy()
    if sentiment_filter != "Tous":
        filtered_df = filtered_df[filtered_df["Sentiment"] == sentiment_filter]
    if dept_filter != "Tous":
        filtered_df = filtered_df[filtered_df["Department"] == dept_filter]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Original Text"].str.contains(search_query, case=False)
            | filtered_df["Auto-Translated English Text"].str.contains(search_query, case=False)
        ]

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    if filtered_df.empty:
        st.info("Aucun avis ne correspond aux filtres sélectionnés.")
    else:
        for _, r in filtered_df.iterrows():
            sentiment_color = "#10b981" if r["Sentiment"] == "Positive" else ("#f59e0b" if r["Sentiment"] == "Neutral" else "#ef4444")
            st.markdown(
                f"""
                <div style="background-color: #ffffff; border-radius: 10px; padding: 16px 20px; border: 1px solid #e2e8f0; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <strong>{r['Platform']}</strong> &nbsp;|&nbsp; {r['Original Language']} &nbsp;|&nbsp; <span style="color: #64748b;">{r['Date']}</span>
                        </div>
                        <div>
                            <span style="background-color: {sentiment_color}22; color: {sentiment_color}; font-weight: 700; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem;">
                                {r['Sentiment']}
                            </span>
                        </div>
                    </div>
                    <div style="font-size: 0.95rem; color: #1e293b; margin-bottom: 6px;">
                        <em>"{r['Original Text']}"</em>
                    </div>
                    <div style="font-size: 0.9rem; color: #475569; background-color: #f8fafc; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
                        🇬🇧 <strong>TRADUCTION AUTO:</strong> "{r['Auto-Translated English Text']}"
                    </div>
                    <div>
                        <span class="badge badge-dept">🏢 {r['Department']}</span>
                        <span style="font-size: 0.8rem; background-color: #f1f5f9; color: #334155; padding: 3px 8px; border-radius: 6px;">
                            🏷️ Aspect: {r['Extracted Aspect']}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )