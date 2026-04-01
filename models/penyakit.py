from extensions import db
from datetime import datetime

class Penyakit(db.Model):
    __tablename__ = "penyakit"

    id_penyakit = db.Column(db.Integer, primary_key=True)
    kode_penyakit = db.Column(db.String(50), unique=True)
    nama_penyakit = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)
    penyebab = db.Column(db.Text)
    tingkat_keparahan = db.Column(db.String(50))
    dibuat_oleh = db.Column(db.Integer, db.ForeignKey("users.id"))
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)
    diperbarui_pada = db.Column(db.DateTime, onupdate=datetime.utcnow)