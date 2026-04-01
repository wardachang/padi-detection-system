from extensions import db
from datetime import datetime

class RumusVarietas(db.Model):
    __tablename__ = "rumus_varietas"

    id_rumus = db.Column(db.Integer, primary_key=True)
    id_varietas = db.Column(db.Integer, db.ForeignKey("varietas_padi.id_varietas"))
    nama_rumus = db.Column(db.String(100))
    tipe_rumus = db.Column(db.String(50))
    konfigurasi_rumus = db.Column(db.Text)
    catatan = db.Column(db.Text)
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)