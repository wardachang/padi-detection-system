from datetime import datetime
from extensions import db


class JadwalUser(db.Model):
    __tablename__ = "jadwal_user"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    varietas_id = db.Column(db.Integer, db.ForeignKey("varietas_padi.id"), nullable=False)

    tanggal_semai = db.Column(db.Date, nullable=False)
    tanggal_penyemaian = db.Column(db.Date, nullable=False)
    tanggal_penanaman = db.Column(db.Date, nullable=False)
    tanggal_pemupukan_1 = db.Column(db.Date, nullable=True)
    tanggal_pemupukan_2 = db.Column(db.Date, nullable=True)
    tanggal_panen = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="jadwal_user_items")
    varietas = db.relationship("VarietasPadi", backref="jadwal_user_items")