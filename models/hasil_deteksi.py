from extensions import db
from datetime import datetime

class HasilDeteksi(db.Model):
    __tablename__ = "hasil_deteksi"

    id_hasil = db.Column(db.Integer, primary_key=True)
    id_deteksi = db.Column(db.Integer, db.ForeignKey("detail_jadwal_pengelolaan.id_deteksi"))
    id_penyakit = db.Column(db.Integer, db.ForeignKey("penyakit.id_penyakit"))
    tingkat_keyakinan = db.Column(db.Float)
    ringkasan = db.Column(db.Text)
    snapshot_rekomendasi = db.Column(db.Text)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)