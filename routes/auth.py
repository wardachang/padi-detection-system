from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from models.riwayat_deteksi import RiwayatDeteksi
from extensions import db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        return redirect(url_for("deteksi"))
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            if user.role == "admin":
                return redirect(url_for("auth.admin_dashboard"))
            elif user.role == "user":
                return redirect(url_for("deteksi"))
            else:
                flash("Role tidak dikenali")
                return redirect(url_for("auth.login"))

        flash("Email atau password salah")

    return render_template("login.html")


@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("beranda_user.html", active="beranda_user")


@auth.route("/jadwal_user")
@login_required
def jadwal_user():
    return render_template("jadwal_user.html", active="jadwal_user")


@auth.route("/riwayat_user")
@login_required
def riwayat_user():
    histories = RiwayatDeteksi.query.filter_by(user_id=current_user.id) \
        .order_by(RiwayatDeteksi.created_at.desc()) \
        .all()

    return render_template(
        "riwayat_user.html",
        histories=histories,
        active="riwayat_user"
    )


@auth.route("/riwayat_user/hapus/<int:id>", methods=["POST"])
@login_required
def hapus_riwayat(id):
    riwayat = RiwayatDeteksi.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()

    if not riwayat:
        flash("Data riwayat tidak ditemukan atau bukan milik Anda.", "error")
        return redirect(url_for("auth.riwayat_user"))

    db.session.delete(riwayat)
    db.session.commit()
    flash("Riwayat berhasil dihapus.", "success")
    return redirect(url_for("auth.riwayat_user"))


@auth.route("/riwayat_user/hapus_semua", methods=["POST"])
@login_required
def hapus_semua_riwayat():
    semua_riwayat = RiwayatDeteksi.query.filter_by(user_id=current_user.id).all()

    if not semua_riwayat:
        flash("Tidak ada riwayat yang bisa dihapus.", "error")
        return redirect(url_for("auth.riwayat_user"))

    for item in semua_riwayat:
        db.session.delete(item)

    db.session.commit()
    flash("Semua riwayat berhasil dihapus.", "success")
    return redirect(url_for("auth.riwayat_user"))


@auth.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("beranda_admin.html")


@auth.route("/admin/users")
@login_required
def users():
    return render_template("kelola_akun.html")


@auth.route("/admin/penyakit")
@login_required
def penyakit():
    return render_template("data_penyakit.html")


@auth.route("/admin/varietas")
@login_required
def varietas():
    return render_template("varietas_padi.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))