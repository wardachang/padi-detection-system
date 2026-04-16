from utils.disease_info import disease_info
from flask import Flask, render_template, request
from config import Config
from extensions import db, login_manager
from routes.auth import auth

from models.user import User
from models.riwayat_deteksi import RiwayatDeteksi
from models import *

from flask_migrate import Migrate
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

import numpy as np
import os
import uuid
import click
from flask.cli import with_appcontext


# =======================
# INIT APP
# =======================
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Silakan login terlebih dahulu."

app.register_blueprint(auth)
migrate = Migrate(app, db)


# =======================
# LOAD MODEL CNN
# =======================
model_padi = load_model("model/baru_model_resnet_rice_leaf.h5", compile=False)

class_names = [
    "Bacterialblight",  # 0
    "Blast",            # 1
    "Brownspot",        # 2
    "healthy"           # 3
]

class_names_display = {
    "Bacterialblight": "Bacterial Leaf Blight",
    "Blast": "Leaf Blast",
    "Brownspot": "Brown Spot",
    "healthy": "Healthy Rice Leaf"
}

# =======================
# PREPROCESS IMAGE
# =======================
def prepare_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    return img_array

# =======================
# PREDICT IMAGE (FINAL TANPA FILTER)
# =======================
def predict_disease(img_path):
    img = prepare_image(img_path)

    pred = model_padi.predict(img, verbose=0)[0]

    idx = int(np.argmax(pred))
    prediction_raw = class_names[idx]
    prediction = class_names_display[prediction_raw]
    confidence = float(pred[idx]) * 100

    return prediction, confidence, pred

# =======================
# LOGIN MANAGER
# =======================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =======================
# SEED DATABASE
# =======================
@click.command("seed")
@with_appcontext
def seed():
    users = [
        User(
            fullname="Admin",
            email="admin@mail.com",
            password=generate_password_hash("123"),
            role="admin"
        ),
        User(
            fullname="User 1",
            email="user1@mail.com",
            password=generate_password_hash("123"),
            role="user"
        ),
        User(
            fullname="User 2",
            email="user2@mail.com",
            password=generate_password_hash("123"),
            role="user"
        ),
    ]

    db.session.add_all(users)
    db.session.commit()
    print("Database seeded")


app.cli.add_command(seed)


# =======================
# ROUTE DETEKSI
# =======================
@app.route("/deteksi", methods=["GET", "POST"])
@login_required
def deteksi():
    prediction = None
    confidence = None
    desc = None
    solution = []
    img_path = None
    error = None

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            error = "Silakan pilih gambar terlebih dahulu."
        else:
            allowed_ext = {"png", "jpg", "jpeg"}
            filename = secure_filename(file.filename)
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

            if ext not in allowed_ext:
                error = "Format file harus JPG, JPEG, atau PNG."
            else:
                upload_folder = os.path.join("static", "uploads")
                os.makedirs(upload_folder, exist_ok=True)

                unique_name = f"{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join(upload_folder, unique_name)
                file.save(file_path)

                img_path = f"/static/uploads/{unique_name}"

                try:
                    prediction, confidence, raw_pred = predict_disease(file_path)

                    if prediction == "Bukan Padi":
                            desc = "Gambar yang Anda upload bukan daun padi."
                            solution = ["Silakan upload gambar daun padi yang jelas."]
                    else:
                            info = disease_info.get(prediction)
                            if info:
                                desc = info.get("desc")
                                solution = info.get("solution", [])
                            else:
                                desc = "Informasi penyakit belum tersedia."
                                solution = []
                                
                    # =======================
                    # SIMPAN KE DATABASE
                    # =======================
                    history = RiwayatDeteksi(
                        user_id=current_user.id,
                        image_path=img_path,
                        hasil=prediction,
                        confidence=confidence,
                        deskripsi=desc
                    )
                    db.session.add(history)
                    db.session.commit()

                except Exception as e:
                    error = f"Terjadi kesalahan saat prediksi: {str(e)}"

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=round(confidence, 2) if confidence is not None else None,
        desc=desc,
        solution=solution,
        img_path=img_path,
        error=error,
        active="deteksi"
    )


if __name__ == "__main__":
    app.run(debug=True)