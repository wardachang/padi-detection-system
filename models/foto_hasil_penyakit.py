from extensions import db
from datetime import datetime

class FotoHasilPenyakit(db.Model):
    __tablename__ = "foto_hasil_penyakit"

    id_foto = db.Column(db.Integer, primary_key=True)
    id_penyakit = db.Column(db.Integer, db.ForeignKey("penyakit.id_penyakit"))
    url_foto = db.Column(db.String(255), nullable=False)
    keterangan = db.Column(db.String(255))
    foto_utama = db.Column(db.Boolean, default=False)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)