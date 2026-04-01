from extensions import db
from datetime import datetime

class DetailJadwalPengelolaan(db.Model):
    __tablename__ = "detail_jadwal_pengelolaan"

    id_deteksi = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    waktu_deteksi = db.Column(db.DateTime, default=datetime.utcnow)
    jenis_input = db.Column(db.String(50), nullable=False)
    url_gambar = db.Column(db.String(255))
    teks_input = db.Column(db.Text)
    versi_model = db.Column(db.String(50))
    status_deteksi = db.Column(db.String(50))
    catatan = db.Column(db.Text)