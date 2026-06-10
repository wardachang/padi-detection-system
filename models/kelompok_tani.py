from extensions import db


user_kelompok_tani = db.Table(
    "user_kelompok_tani",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("kelompok_tani_id", db.Integer, db.ForeignKey("kelompok_tani.id"), primary_key=True),
)


class KelompokTani(db.Model):
    __tablename__ = "kelompok_tani"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    anggota = db.relationship(
        "User",
        secondary=user_kelompok_tani,
        back_populates="kelompok_tani_list"
    )

    jadwal_tanam_items = db.relationship(
        "JadwalTanam",
        back_populates="kelompok_tani"
    )

    def __repr__(self):
        return f"<KelompokTani {self.nama}>"