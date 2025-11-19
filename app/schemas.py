# app/schemas.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# -----------------------------
#  Types de signalements RATP
# -----------------------------

class ReportKind(str, Enum):
    urine = "urine"
    vomit = "vomit"
    feces = "feces"          # excréments
    blood = "blood"
    syringe = "syringe"
    broken_glass = "broken_glass"


class ReportSignal(str, Enum):
    # Statut du signalement
    to_clean = "to_clean"                      # signalement créé, à traiter
    cleaning_in_progress = "cleaning_in_progress"  # équipe envoyée / en cours
    cleaned = "cleaned"                        # terminé
    false_alarm = "false_alarm"                # faux signalement / erreur


# -----------------------------
#  Modèles pour les API
# -----------------------------

class ReportIn(BaseModel):
    """
    Données reçues quand un utilisateur crée un signalement.
    Photo ou vidéo courte : URL dans photo_url.
    """
    kind: ReportKind
    signal: ReportSignal = ReportSignal.to_clean

    # Position GPS
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    accuracy_m: Optional[float] = None

    # Contexte transport (optionnel mais recommandé)
    mode: Optional[str] = None          # "metro", "rer", "tram", "bus", "train_sncf"
    line_code: Optional[str] = None     # ex: "M8", "RER A", "T2", "Bus 27"
    direction: Optional[str] = None     # ex: "Balard"

    current_stop: Optional[str] = None  # station actuelle ou quittée
    next_stop: Optional[str] = None     # prochaine station (si connue)
    final_stop: Optional[str] = None    # destination finale
    train_state: Optional[str] = None   # "en_gare" | "en_mouvement"

    # Infos complémentaires
    note: Optional[str] = None

    # URL vers le média : photo OU vidéo 5s (Supabase)
    photo_url: Optional[str] = None

    # Pour plus tard si tu ajoutes une auth
    user_id: Optional[str] = None


class ReportOut(BaseModel):
    """
    Représentation d'un signalement retourné par les endpoints (liste, détails…)
    """
    id: str
    kind: ReportKind
    signal: ReportSignal

    lat: float
    lng: float
    created_at: datetime

    # Contexte transport
    mode: Optional[str] = None
    line_code: Optional[str] = None
    direction: Optional[str] = None
    current_stop: Optional[str] = None
    next_stop: Optional[str] = None
    final_stop: Optional[str] = None
    train_state: Optional[str] = None

    note: Optional[str] = None
    photo_url: Optional[str] = None
    user_id: Optional[str] = None


# -----------------------------
#  Modèles admin / utilitaires
# -----------------------------

class AdminSupabaseStatus(BaseModel):
    """
    Utilisé par l'endpoint /admin/supabase_status
    pour vérifier la config Supabase.
    """
    SUPABASE_URL_set: bool
    SUPABASE_SERVICE_ROLE_set: bool
    SUPABASE_BUCKET: Optional[str] = None
