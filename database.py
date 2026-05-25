"""
database.py — Gestion SQLite pour KineAssist
=============================================
Tables :
  - kines     : comptes kinésithérapeutes
  - patients  : comptes patients (liés à un kiné)
  - invitations : tokens d'invitation envoyés par email
"""

import sqlite3
import hashlib
import hmac
import secrets
import os
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("kineassist.db")


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS kines (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        email       TEXT    UNIQUE NOT NULL,
        nom         TEXT    NOT NULL,
        password_hash TEXT  NOT NULL,
        created_at  TEXT    DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS patients (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        email       TEXT    UNIQUE NOT NULL,
        nom         TEXT    NOT NULL,
        age         INTEGER DEFAULT 0,
        pathologie  TEXT    DEFAULT '',
        exercice    TEXT    DEFAULT 'Flexion du genou',
        semaine     INTEGER DEFAULT 1,
        objectif_semaine INTEGER DEFAULT 8,
        password_hash TEXT  DEFAULT NULL,
        activated   INTEGER DEFAULT 0,
        kine_id     INTEGER NOT NULL,
        notes       TEXT    DEFAULT '',
        alerte      INTEGER DEFAULT 0,
        created_at  TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY (kine_id) REFERENCES kines(id)
    );

    CREATE TABLE IF NOT EXISTS invitations (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        token       TEXT    UNIQUE NOT NULL,
        patient_id  INTEGER NOT NULL,
        email       TEXT    NOT NULL,
        expires_at  TEXT    NOT NULL,
        used        INTEGER DEFAULT 0,
        created_at  TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    );

    CREATE TABLE IF NOT EXISTS sessions_kine (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id  INTEGER NOT NULL,
        date        TEXT    NOT NULL,
        exercice    TEXT    DEFAULT '',
        reps        INTEGER DEFAULT 0,
        score_mean  REAL    DEFAULT 0,
        score_best  REAL    DEFAULT 0,
        trend       TEXT    DEFAULT 'stable',
        semaine     INTEGER DEFAULT 1,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    );
    """)


    # Migration: add protocol column if missing
    try:
        c.execute("ALTER TABLE patients ADD COLUMN protocol TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass

    # Migration: add profile columns if missing
    for col, default in [
        ("photo_b64",    "TEXT DEFAULT ''"),
        ("poids",        "REAL DEFAULT 0"),
        ("taille",       "INTEGER DEFAULT 0"),
        ("telephone",    "TEXT DEFAULT ''"),
        ("antecedents",  "TEXT DEFAULT ''"),
        ("genre",        "TEXT DEFAULT ''"),
    ]:
        try:
            c.execute(f"ALTER TABLE patients ADD COLUMN {col} {default}")
            conn.commit()
        except Exception:
            pass

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _check_pwd(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(_hash(plain), hashed)


# ─────────────────────────────────────────────────────────────────────────────
# AUTH — Kinés
# ─────────────────────────────────────────────────────────────────────────────

def register_kine(email: str, nom: str, password: str) -> tuple[bool, str]:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO kines (email, nom, password_hash) VALUES (?, ?, ?)",
            (email.lower().strip(), nom.strip(), _hash(password))
        )
        conn.commit()
        return True, "ok"
    except sqlite3.IntegrityError:
        return False, "Un compte kiné existe déjà avec cet email."
    finally:
        conn.close()


def login_kine(email: str, password: str):
    """Retourne le dict kiné ou None."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM kines WHERE email = ?", (email.lower().strip(),)
    ).fetchone()
    conn.close()
    if row and _check_pwd(password, row["password_hash"]):
        return dict(row)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# AUTH — Patients
# ─────────────────────────────────────────────────────────────────────────────

def login_patient(email: str, password: str):
    """Retourne le dict patient ou None."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM patients WHERE email = ? AND activated = 1",
        (email.lower().strip(),)
    ).fetchone()
    conn.close()
    if row and row["password_hash"] and _check_pwd(password, row["password_hash"]):
        return dict(row)
    return None


def activate_patient(token: str, password: str) -> tuple[bool, str]:
    """Active le compte patient via token d'invitation."""
    conn = get_conn()
    try:
        inv = conn.execute(
            "SELECT * FROM invitations WHERE token = ? AND used = 0",
            (token,)
        ).fetchone()
        if not inv:
            return False, "Lien invalide ou déjà utilisé."
        if datetime.fromisoformat(inv["expires_at"]) < datetime.now():
            return False, "Lien expiré. Demandez un nouvel email à votre kiné."

        conn.execute(
            "UPDATE patients SET password_hash = ?, activated = 1 WHERE id = ?",
            (_hash(password), inv["patient_id"])
        )
        conn.execute(
            "UPDATE invitations SET used = 1 WHERE token = ?", (token,)
        )
        conn.commit()
        return True, "ok"
    finally:
        conn.close()


def get_patient_by_token(token: str):
    """Retourne le patient lié au token, ou None."""
    conn = get_conn()
    row = conn.execute("""
        SELECT p.* FROM patients p
        JOIN invitations i ON i.patient_id = p.id
        WHERE i.token = ? AND i.used = 0
    """, (token,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─────────────────────────────────────────────────────────────────────────────
# CRUD — Patients (côté kiné)
# ─────────────────────────────────────────────────────────────────────────────

def get_patients_by_kine(kine_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM patients WHERE kine_id = ? ORDER BY created_at DESC",
        (kine_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_patient(kine_id: int, email: str, nom: str,
                   age: int = 0, pathologie: str = "",
                   exercice: str = "Flexion du genou",
                   semaine: int = 1, objectif_semaine: int = 8) -> tuple[bool, str, int]:
    """
    Crée un patient (sans mot de passe — envoi invitation par email).
    Retourne (success, message, patient_id).
    """
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO patients
               (email, nom, age, pathologie, exercice, semaine, objectif_semaine, kine_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (email.lower().strip(), nom.strip(), age, pathologie, exercice,
             semaine, objectif_semaine, kine_id)
        )
        conn.commit()
        return True, "ok", cur.lastrowid
    except sqlite3.IntegrityError:
        return False, "Un patient avec cet email existe déjà.", -1
    finally:
        conn.close()


def update_patient(patient_id: int, nom: str, age: int, pathologie: str,
                   exercice: str, semaine: int, objectif_semaine: int,
                   notes: str, alerte: bool):
    conn = get_conn()
    conn.execute("""
        UPDATE patients SET
            nom=?, age=?, pathologie=?, exercice=?,
            semaine=?, objectif_semaine=?, notes=?, alerte=?
        WHERE id=?
    """, (nom, age, pathologie, exercice, semaine, objectif_semaine,
          notes, int(alerte), patient_id))
    conn.commit()
    conn.close()


def delete_patient(patient_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM invitations WHERE patient_id = ?", (patient_id,))
    conn.execute("DELETE FROM sessions_kine WHERE patient_id = ?", (patient_id,))
    conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Invitations
# ─────────────────────────────────────────────────────────────────────────────

def create_invitation(patient_id: int, email: str) -> str:
    """Crée un token d'invitation valable 72h. Retourne le token."""
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(hours=72)).isoformat()
    conn = get_conn()
    # Invalider les anciens tokens
    conn.execute(
        "UPDATE invitations SET used = 1 WHERE patient_id = ? AND used = 0",
        (patient_id,)
    )
    conn.execute(
        "INSERT INTO invitations (token, patient_id, email, expires_at) VALUES (?, ?, ?, ?)",
        (token, patient_id, email, expires)
    )
    conn.commit()
    conn.close()
    return token


# ─────────────────────────────────────────────────────────────────────────────
# Sessions
# ─────────────────────────────────────────────────────────────────────────────

def add_session(patient_id: int, exercice: str, reps: int,
                score_mean: float, score_best: float,
                trend: str, semaine: int):
    conn = get_conn()
    conn.execute("""
        INSERT INTO sessions_kine
        (patient_id, date, exercice, reps, score_mean, score_best, trend, semaine)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, datetime.now().strftime("%d/%m/%Y"),
          exercice, reps, score_mean, score_best, trend, semaine))
    conn.commit()
    conn.close()


def get_sessions(patient_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sessions_kine WHERE patient_id = ? ORDER BY date ASC",
        (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Init automatique
init_db()

def update_patient_protocol(patient_id: int, protocol: str):
    """Met à jour le protocole assigné au patient par le kiné."""
    conn = get_conn()
    conn.execute(
        "UPDATE patients SET protocol=? WHERE id=?",
        (protocol, patient_id)
    )
    conn.commit()
    conn.close()


def update_patient_profile(patient_id: int, poids: float, taille: int,
                           telephone: str, antecedents: str, genre: str,
                           photo_b64: str = ""):
    """Met à jour les informations de profil du patient."""
    conn = get_conn()
    if photo_b64:
        conn.execute(
            """UPDATE patients SET poids=?, taille=?, telephone=?,
               antecedents=?, genre=?, photo_b64=? WHERE id=?""",
            (poids, taille, telephone, antecedents, genre, photo_b64, patient_id)
        )
    else:
        conn.execute(
            """UPDATE patients SET poids=?, taille=?, telephone=?,
               antecedents=?, genre=? WHERE id=?""",
            (poids, taille, telephone, antecedents, genre, patient_id)
        )
    conn.commit()
    conn.close()


def get_patient_by_id(patient_id: int) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}