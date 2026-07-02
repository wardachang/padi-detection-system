from extensions import db
from models.penyakit import Penyakit
from models.penanganan_penyakit import PenangananPenyakit
from utils.disease_info import disease_info

def seed_diseases_if_empty():
    try:
        # Check if table has any records
        if Penyakit.query.first() is None:
            print("Penyakit table is empty. Seeding from utils/disease_info.py...")
            
            # Map original ML model class names to standard display names
            display_names = {
                "Bacterial Leaf Blight": "Hawar Daun Bakteri",
                "Brown Spot": "Bercak Cokelat",
                "Healthy Rice Leaf": "Daun Padi Sehat",
                "Leaf Blast": "Blas Daun",
                "Leaf scald": "Skald Daun",
                "Sheath Blight": "Hawar Pelepah",
            }
            
            for key, val in disease_info.items():
                p = Penyakit(
                    kode_penyakit=key,
                    nama_penyakit=display_names.get(key, key),
                    deskripsi=val.get("desc"),
                    tingkat_keparahan="Sedang"
                )
                db.session.add(p)
                db.session.flush() # Populate id_penyakit
                
                # Seed solutions
                for idx, sol in enumerate(val.get("solution", [])):
                    pp = PenangananPenyakit(
                        id_penyakit=p.id_penyakit,
                        jenis_penanganan="Solusi",
                        judul_penanganan=sol,
                        urutan=idx + 1
                    )
                    db.session.add(pp)
            
            db.session.commit()
            print("Penyakit and solutions seeded successfully!")
    except Exception as e:
        db.session.rollback()
        print("Error seeding diseases:", e)
