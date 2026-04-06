from extensions import db

class VarietasPadi(db.Model):
    __tablename__ = "varietas_padi"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    hari_penyemaian = db.Column(db.Integer, nullable=False, default=0)
    hari_penanaman = db.Column(db.Integer, nullable=False)
    hari_pemupukan_1 = db.Column(db.Integer, nullable=True)
    hari_pemupukan_2 = db.Column(db.Integer, nullable=True)
    hari_panen = db.Column(db.Integer, nullable=False)