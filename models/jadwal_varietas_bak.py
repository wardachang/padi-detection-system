from extensions import db

class JadwalVarietas(db.Model):
    __tablename__ = "jadwal_varietas"

    id = db.Column(db.Integer, primary_key=True)
    nama_varietas = db.Column(db.String(100), unique=True, nullable=False)

    hari_tanam = db.Column(db.Integer, nullable=False)
    hari_pemupukan_1 = db.Column(db.Integer, nullable=False)
    hari_pemupukan_2 = db.Column(db.Integer, nullable=False)
    hari_panen = db.Column(db.Integer, nullable=False)