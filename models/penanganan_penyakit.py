from extensions import db
from datetime import datetime

class PenangananPenyakit(db.Model):
    __tablename__ = "penanganan_penyakit"

    id_penanganan = db.Column(db.Integer, primary_key=True)
    id_penyakit = db.Column(db.Integer, db.ForeignKey("penyakit.id_penyakit"))
    jenis_penanganan = db.Column(db.String(50))
    judul_penanganan = db.Column(db.String(100))
    dosis = db.Column(db.String(100))
    cara_aplikasi = db.Column(db.Text)
    catatan = db.Column(db.Text)
    urutan = db.Column(db.Integer)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)