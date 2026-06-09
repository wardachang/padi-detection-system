from utils.disease_info import disease_info
from flask import Flask, render_template, request, redirect, url_for, flash
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
import gc
import tensorflow as tf
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

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# =======================
# PATH MODEL CNN
# =======================
# Model TIDAK di-load di awal aplikasi.
# Model hanya akan di-load saat user melakukan deteksi.
MODEL_FILTER_PATH = "model/model_resnet_final.h5"
MODEL_PADI_PATH = "model/baru_model.h5"

class_names_filter = ["BUKAN PADI", "PADI"]

class_names = [
    "Bacterial Leaf Blight",  # 0
    "Brown Spot",             # 1
    "Healthy Rice Leaf",      # 2
    "Leaf Blast",             # 3
    "Leaf scald",             # 4
    "Sheath Blight"           # 5
]

# Nama penyakit untuk tampilan UI
# Key tetap memakai nama asli dari model CNN
display_names = {
    "Bacterial Leaf Blight": "Hawar Daun Bakteri",
    "Brown Spot": "Bercak Cokelat",
    "Healthy Rice Leaf": "Daun Padi Sehat",
    "Leaf Blast": "Blas Daun",
    "Leaf scald": "Skald Daun",
    "Sheath Blight": "Hawar Pelepah",
    "Bukan Padi": "Bukan Daun Padi",
    "Tidak Yakin": "Hasil Tidak Yakin"
}


# =======================
# PREPROCESS IMAGE
# =======================

# Untuk model filter padi / bukan padi
def prepare_image_filter(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    return img_array


# Untuk model penyakit padi
def prepare_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    return img_array


def predict_disease(img_path):
    # =======================
    # STEP 1: CEK PADI / BUKAN PADI
    # =======================
    img_filter = prepare_image_filter(img_path)

    model_filter = None

    try:
        print("Loading model filter padi...")
        model_filter = load_model(MODEL_FILTER_PATH, compile=False)

        pred_filter = model_filter.predict(img_filter, verbose=0)[0]

    finally:
        if model_filter is not None:
            del model_filter

        tf.keras.backend.clear_session()
        gc.collect()
        print("Model filter padi sudah dibersihkan dari memori.")

    idx_filter = int(np.argmax(pred_filter))
    filter_label = class_names_filter[idx_filter]
    filter_confidence = float(pred_filter[idx_filter]) * 100

    print("\n=== FILTER PADI / BUKAN PADI ===")
    for name, prob in zip(class_names_filter, pred_filter):
        print(f"{name}: {prob * 100:.2f}%")

    if filter_label == "BUKAN PADI":
        return "Bukan Padi", round(filter_confidence, 2), pred_filter

    # =======================
    # STEP 2: DETEKSI PENYAKIT PADI
    # =======================
    img = prepare_image(img_path)

    model_padi = None

    try:
        print("Loading model penyakit padi...")
        model_padi = load_model(MODEL_PADI_PATH, compile=False)

        pred = model_padi.predict(img, verbose=0)[0]

    finally:
        if model_padi is not None:
            del model_padi

        tf.keras.backend.clear_session()
        gc.collect()
        print("Model penyakit padi sudah dibersihkan dari memori.")

    idx = int(np.argmax(pred))
    prediction = class_names[idx]
    confidence = float(pred[idx]) * 100

    print("\n=== DETEKSI PENYAKIT PADI ===")
    for name, prob in zip(class_names, pred):
        print(f"{name}: {prob * 100:.2f}%")

    # Kalau model kurang yakin
    if confidence < 60:
        return "Tidak Yakin", round(confidence, 2), pred

    return prediction, round(confidence, 2), pred


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
    prediction_indo = None
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

                    # Nama hasil untuk tampilan UI
                    prediction_indo = display_names.get(prediction, prediction)

                    if prediction == "Bukan Padi":
                        desc = "Gambar yang Anda upload bukan daun padi."
                        solution = ["Silakan upload gambar daun padi yang jelas."]

                    elif prediction == "Tidak Yakin":
                        desc = "Model belum cukup yakin terhadap hasil prediksi gambar ini."
                        solution = [
                            "Gunakan gambar daun padi yang lebih jelas.",
                            "Pastikan daun terlihat fokus.",
                            "Gunakan pencahayaan yang cukup.",
                            "Hindari gambar buram atau terlalu jauh."
                        ]

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
        prediction_indo=prediction_indo,
        confidence=round(confidence, 2) if confidence is not None else None,
        desc=desc,
        solution=solution,
        img_path=img_path,
        error=error,
        active="deteksi"
    )

# =======================
# ROUTE DETEKSI ADMIN
# =======================
@app.route("/admin/deteksi", methods=["GET", "POST"])
@login_required
def deteksi_admin():
    if current_user.role != "admin":
        flash("Anda tidak memiliki akses ke halaman admin.", "error")
        return redirect(url_for("deteksi"))

    prediction = None
    prediction_indo = None
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

                    prediction_indo = display_names.get(prediction, prediction)

                    if prediction == "Bukan Padi":
                        desc = "Gambar yang Anda upload bukan daun padi."
                        solution = ["Silakan upload gambar daun padi yang jelas."]

                    elif prediction == "Tidak Yakin":
                        desc = "Model belum cukup yakin terhadap hasil prediksi gambar ini."
                        solution = [
                            "Gunakan gambar daun padi yang lebih jelas.",
                            "Pastikan daun terlihat fokus.",
                            "Gunakan pencahayaan yang cukup.",
                            "Hindari gambar buram atau terlalu jauh."
                        ]

                    else:
                        info = disease_info.get(prediction)

                        if info:
                            desc = info.get("desc")
                            solution = info.get("solution", [])
                        else:
                            desc = "Informasi penyakit belum tersedia."
                            solution = []

                    # Simpan hasil deteksi sebagai riwayat milik admin yang sedang login
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
        "deteksi_admin.html",
        prediction=prediction,
        prediction_indo=prediction_indo,
        confidence=round(confidence, 2) if confidence is not None else None,
        desc=desc,
        solution=solution,
        img_path=img_path,
        error=error,
        active="deteksi_admin"
    )


# =======================
# ROUTE RIWAYAT ADMIN
# =======================
@app.route("/admin/riwayat")
@login_required
def riwayat_admin():
    if current_user.role != "admin":
        flash("Anda tidak memiliki akses ke halaman admin.", "error")
        return redirect(url_for("deteksi"))

    # Hanya menampilkan riwayat deteksi milik admin yang sedang login
    histories = RiwayatDeteksi.query.filter_by(
        user_id=current_user.id
    ).order_by(
        RiwayatDeteksi.id.desc()
    ).all()

    return render_template(
        "riwayat_admin.html",
        histories=histories,
        active="riwayat_admin"
    )


# =======================
# ROUTE HAPUS SATU RIWAYAT ADMIN
# =======================
@app.route("/admin/riwayat/hapus/<int:id>", methods=["POST"])
@login_required
def hapus_riwayat_admin(id):
    if current_user.role != "admin":
        flash("Anda tidak memiliki akses ke halaman admin.", "error")
        return redirect(url_for("deteksi"))

    # Admin hanya boleh menghapus riwayat miliknya sendiri
    riwayat = RiwayatDeteksi.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if riwayat.image_path:
        image_file = riwayat.image_path.lstrip("/")

        if os.path.exists(image_file):
            os.remove(image_file)

    db.session.delete(riwayat)
    db.session.commit()

    flash("Riwayat deteksi admin berhasil dihapus.", "success")
    return redirect(url_for("riwayat_admin"))


# =======================
# ROUTE HAPUS SEMUA RIWAYAT ADMIN
# =======================
@app.route("/admin/riwayat/hapus-semua", methods=["POST"])
@login_required
def hapus_semua_riwayat_admin():
    if current_user.role != "admin":
        flash("Anda tidak memiliki akses ke halaman admin.", "error")
        return redirect(url_for("deteksi"))

    # Hanya menghapus semua riwayat milik admin yang sedang login
    histories = RiwayatDeteksi.query.filter_by(
        user_id=current_user.id
    ).all()

    for item in histories:
        if item.image_path:
            image_file = item.image_path.lstrip("/")

            if os.path.exists(image_file):
                os.remove(image_file)

        db.session.delete(item)

    db.session.commit()

    flash("Semua riwayat deteksi admin berhasil dihapus.", "success")
    return redirect(url_for("riwayat_admin"))
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)