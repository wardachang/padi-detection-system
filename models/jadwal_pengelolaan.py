from extensions import db
from datetime import datetime

class JadwalPengelolaan(db.Model):
    __tablename__ = "jadwal_pengelolaan"

    id_jadwal = db.Column(db.Integer, primary_key=True)
    id_varietas = db.Column(db.Integer, db.ForeignKey("varietas_padi.id_varietas"))
    nama_jadwal = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    aktif = db.Column(db.Boolean, default=True)
    dibuat_oleh = db.Column(db.Integer, db.ForeignKey("users.id"))
    diperbarui_pada = db.Column(db.DateTime, onupdate=datetime.utcnow)