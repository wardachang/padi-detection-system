from extensions import db

class JadwalTanam(db.Model):
    __tablename__ = "jadwal_tanam"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    varietas_id = db.Column(db.Integer, db.ForeignKey("varietas_padi.id"), nullable=False)

    tanggal_semai = db.Column(db.Date, nullable=False)
    tanggal_penyemaian = db.Column(db.Date, nullable=False)
    tanggal_penanaman = db.Column(db.Date, nullable=False)
    tanggal_pemupukan_1 = db.Column(db.Date, nullable=True)
    tanggal_pemupukan_2 = db.Column(db.Date, nullable=True)
    tanggal_panen = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref="jadwal_tanam_items")
    varietas = db.relationship("VarietasPadi", backref="jadwal_tanam_items")