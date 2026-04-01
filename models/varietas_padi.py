from extensions import db
from datetime import datetime

class VarietasPadi(db.Model):
    __tablename__ = "varietas_padi"

    id_varietas = db.Column(db.Integer, primary_key=True)
    kode_varietas = db.Column(db.String(50), unique=True)
    nama_varietas = db.Column(db.String(100))
    jenis_varietas = db.Column(db.String(50))
    umur_panen_hari = db.Column(db.Integer)
    deskripsi = db.Column(db.Text)
    karakterisik = db.Column(db.Text)
    dibuat_oleh = db.Column(db.Integer, db.ForeignKey("users.id"))
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)
    diperbarui_pada = db.Column(db.DateTime, onupdate=datetime.utcnow)