from extensions import db
from datetime import datetime


class RiwayatDeteksi(db.Model):
    __tablename__ = "riwayat_deteksi"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    image_path = db.Column(db.String(255), nullable=False)
    hasil = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("riwayat_deteksi", lazy=True))