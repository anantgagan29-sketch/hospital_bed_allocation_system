"""Data access for the patients table."""
import sqlite3
import uuid


def generate_patient_id() -> str:
    return f"PAT-{uuid.uuid4().hex[:6].upper()}"


def create_patient(db: sqlite3.Connection, name: str, age: int, gender: str,
                    medical_condition: str, contact: str) -> str:
    patient_id = generate_patient_id()
    db.execute(
        """INSERT INTO patients (patient_id, name, age, gender, medical_condition, contact)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (patient_id, name, age, gender, medical_condition, contact),
    )
    db.commit()
    return patient_id


def list_patients(db: sqlite3.Connection):
    return db.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()


def get_patient(db: sqlite3.Connection, patient_id: str):
    return db.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
