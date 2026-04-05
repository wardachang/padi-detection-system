import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import func, or_
from models.user import User
from models.riwayat_deteksi import RiwayatDeteksi
from extensions import db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

auth = Blueprint("auth", __name__)


# =======================
# HELPER
# =======================
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# =======================
# ROOT
# =======================
@auth.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        return redirect(url_for("deteksi"))
    return redirect(url_for("auth.login"))


# =======================
# LOGIN
# =======================
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        return redirect(url_for("deteksi"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email dan password wajib diisi.", "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email atau password salah.", "error")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Akun Anda tidak aktif.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Email atau password salah.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Login berhasil.", "success")

        if user.role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        return redirect(url_for("deteksi"))

    return render_template("login.html")


# =======================
# REGISTER
# =======================
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        return redirect(url_for("deteksi"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not fullname or not email or not password or not confirm_password:
            flash("Semua field wajib diisi.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Konfirmasi password tidak sama.", "error")
            return redirect(url_for("auth.register"))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email sudah terdaftar.", "error")
            return redirect(url_for("auth.register"))

        user_baru = User(
            fullname=fullname,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )

        db.session.add(user_baru)
        db.session.commit()

        flash("Pendaftaran berhasil. Silakan login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# =======================
# USER DASHBOARD
# =======================
@auth.route("/dashboard")
@login_required
def dashboard():
    histories = RiwayatDeteksi.query.filter_by(user_id=current_user.id) \
        .order_by(RiwayatDeteksi.created_at.desc()) \
        .all()

    total_deteksi = len(histories)
    total_sehat = len([h for h in histories if h.hasil == "Healthy Rice Leaf"])
    total_penyakit = total_deteksi - total_sehat

    return render_template(
        "beranda_user.html",
        active="beranda_user",
        histories=histories[:5],
        total_deteksi=total_deteksi,
        total_sehat=total_sehat,
        total_penyakit=total_penyakit
    )


# =======================
# USER JADWAL
# =======================
@auth.route("/jadwal_user")
@login_required
def jadwal_user():
    return render_template("jadwal_user.html", active="jadwal_user")


# =======================
# USER RIWAYAT
# =======================
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


# =======================
# ADMIN DASHBOARD
# =======================
@auth.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))

    total_pengguna = User.query.filter_by(role="user").count()
    total_deteksi = RiwayatDeteksi.query.count()
    penyakit_terdeteksi = RiwayatDeteksi.query.filter(
        RiwayatDeteksi.hasil != "Healthy Rice Leaf"
    ).count()

    aktivitas_terbaru = db.session.query(RiwayatDeteksi, User) \
        .join(User, RiwayatDeteksi.user_id == User.id) \
        .order_by(RiwayatDeteksi.created_at.desc()) \
        .limit(10) \
        .all()

    return render_template(
        "beranda_admin.html",
        active="beranda_admin",
        total_pengguna=total_pengguna,
        total_deteksi=total_deteksi,
        penyakit_terdeteksi=penyakit_terdeteksi,
        aktivitas_terbaru=aktivitas_terbaru
    )


# =======================
# ADMIN KELOLA AKUN
# =======================
@auth.route("/admin/users")
@login_required
def users():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    query = User.query.filter(User.role == "user")

    if q:
        query = query.filter(
            or_(
                User.fullname.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                User.phone.ilike(f"%{q}%")
            )
        )

    if status == "active":
        query = query.filter(User.is_active.is_(True))
    elif status == "inactive":
        query = query.filter(User.is_active.is_(False))

    users_pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=10, error_out=False)

    user_ids = [user.id for user in users_pagination.items]

    riwayat_count_map = {}
    if user_ids:
        riwayat_counts = (
            db.session.query(
                RiwayatDeteksi.user_id,
                func.count(RiwayatDeteksi.user_id)
            )
            .filter(RiwayatDeteksi.user_id.in_(user_ids))
            .group_by(RiwayatDeteksi.user_id)
            .all()
        )
        riwayat_count_map = {user_id: count for user_id, count in riwayat_counts}

    total_user = User.query.filter_by(role="user").count()
    total_active = User.query.filter_by(role="user", is_active=True).count()
    total_inactive = User.query.filter_by(role="user", is_active=False).count()

    return render_template(
        "kelola_akun.html",
        active="users_admin",
        users=users_pagination,
        q=q,
        status=status,
        total_user=total_user,
        total_active=total_active,
        total_inactive=total_inactive,
        riwayat_count_map=riwayat_count_map
    )


@auth.route("/admin/users/update/<int:user_id>", methods=["POST"])
@login_required
def update_user_admin(user_id):
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))

    user = User.query.filter_by(id=user_id, role="user").first()

    if not user:
        flash("User tidak ditemukan.", "error")
        return redirect(url_for("auth.users"))

    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    q = request.form.get("q", "").strip()
    status = request.form.get("status", "").strip()
    page = request.form.get("page", 1, type=int)

    if not fullname or not email:
        flash("Nama lengkap dan email wajib diisi.", "error")
        return redirect(url_for("auth.users", q=q, status=status, page=page))

    existing_email = User.query.filter(
        User.email == email,
        User.id != user.id
    ).first()

    if existing_email:
        flash("Email sudah digunakan akun lain.", "error")
        return redirect(url_for("auth.users", q=q, status=status, page=page))

    if phone:
        existing_phone = User.query.filter(
            User.phone == phone,
            User.id != user.id
        ).first()

        if existing_phone:
            flash("Nomor telepon sudah digunakan akun lain.", "error")
            return redirect(url_for("auth.users", q=q, status=status, page=page))

    if password or confirm_password:
        if password != confirm_password:
            flash("Konfirmasi password tidak sama.", "error")
            return redirect(url_for("auth.users", q=q, status=status, page=page))

        user.password = generate_password_hash(password)

    user.fullname = fullname
    user.email = email
    user.phone = phone if phone else None

    db.session.commit()
    flash(f"Data user {user.fullname} berhasil diperbarui.", "success")
    return redirect(url_for("auth.users", q=q, status=status, page=page))


@auth.route("/admin/users/toggle-status/<int:user_id>", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))

    user = User.query.filter_by(id=user_id, role="user").first()

    if not user:
        flash("User tidak ditemukan.", "error")
        return redirect(url_for("auth.users"))

    user.is_active = not user.is_active
    db.session.commit()

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    if user.is_active:
        flash(f"Akun {user.fullname} berhasil diaktifkan.", "success")
    else:
        flash(f"Akun {user.fullname} berhasil dinonaktifkan.", "success")

    return redirect(url_for("auth.users", q=q, status=status, page=page))


@auth.route("/admin/users/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user_admin(user_id):
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))

    user = User.query.filter_by(id=user_id, role="user").first()

    if not user:
        flash("User tidak ditemukan.", "error")
        return redirect(url_for("auth.users"))

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    riwayat_user = RiwayatDeteksi.query.filter_by(user_id=user.id).all()
    for item in riwayat_user:
        db.session.delete(item)

    if user.profile_image:
        image_path = os.path.join(current_app.root_path, user.profile_image.lstrip("/"))
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass

    db.session.delete(user)
    db.session.commit()

    flash("Akun user berhasil dihapus.", "success")
    return redirect(url_for("auth.users", q=q, status=status, page=page))


@auth.route("/admin/penyakit")
@login_required
def penyakit():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))
    return render_template("data_penyakit.html", active="penyakit_admin")


@auth.route("/admin/varietas")
@login_required
def varietas():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))
    return render_template("varietas_padi.html", active="varietas_admin")


# =======================
# USER PROFILE
# =======================
@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile_user():
    if current_user.role != "user":
        flash("Akses ditolak.", "error")
        return redirect(url_for("auth.admin_dashboard"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        profile_image = request.files.get("profile_image")

        if not fullname or not email:
            flash("Nama lengkap dan email wajib diisi.", "error")
            return redirect(url_for("auth.profile_user"))

        existing_email = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_email:
            flash("Email sudah digunakan akun lain.", "error")
            return redirect(url_for("auth.profile_user"))

        if phone:
            existing_phone = User.query.filter(
                User.phone == phone,
                User.id != current_user.id
            ).first()

            if existing_phone:
                flash("Nomor telepon sudah digunakan akun lain.", "error")
                return redirect(url_for("auth.profile_user"))

        current_user.fullname = fullname
        current_user.email = email
        current_user.phone = phone if phone else None

        if password or confirm_password:
            if password != confirm_password:
                flash("Konfirmasi password tidak sama.", "error")
                return redirect(url_for("auth.profile_user"))

            current_user.password = generate_password_hash(password)

        if profile_image and profile_image.filename != "":
            if not allowed_file(profile_image.filename):
                flash("Format foto harus PNG, JPG, JPEG, atau WEBP.", "error")
                return redirect(url_for("auth.profile_user"))

            filename = secure_filename(profile_image.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"

            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "profile")
            os.makedirs(upload_folder, exist_ok=True)

            save_path = os.path.join(upload_folder, unique_filename)
            profile_image.save(save_path)

            if current_user.profile_image:
                old_path = os.path.join(current_app.root_path, current_user.profile_image.lstrip("/"))
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass

            current_user.profile_image = f"/static/uploads/profile/{unique_filename}"

        db.session.commit()
        flash("Profil berhasil diperbarui.", "success")
        return redirect(url_for("auth.profile_user"))

    return render_template("profil_user.html", active="profile_user")


@auth.route("/profile/delete", methods=["POST"])
@login_required
def delete_profile_user():
    if current_user.role != "user":
        flash("Akses ditolak.", "error")
        return redirect(url_for("auth.admin_dashboard"))

    user = User.query.get(current_user.id)

    if not user:
        flash("Akun tidak ditemukan.", "error")
        return redirect(url_for("auth.login"))

    riwayat_user = RiwayatDeteksi.query.filter_by(user_id=user.id).all()
    for item in riwayat_user:
        db.session.delete(item)

    if user.profile_image:
        image_path = os.path.join(current_app.root_path, user.profile_image.lstrip("/"))
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass

    logout_user()

    db.session.delete(user)
    db.session.commit()

    flash("Akun berhasil dihapus.", "success")
    return redirect(url_for("auth.login"))


# =======================
# ADMIN PROFILE
# =======================
@auth.route("/admin/profile", methods=["GET", "POST"])
@login_required
def profile_admin():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("deteksi"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        profile_image = request.files.get("profile_image")

        if not fullname or not email:
            flash("Nama lengkap dan email wajib diisi.", "error")
            return redirect(url_for("auth.profile_admin"))

        existing_email = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_email:
            flash("Email sudah digunakan akun lain.", "error")
            return redirect(url_for("auth.profile_admin"))

        if phone:
            existing_phone = User.query.filter(
                User.phone == phone,
                User.id != current_user.id
            ).first()

            if existing_phone:
                flash("Nomor telepon sudah digunakan akun lain.", "error")
                return redirect(url_for("auth.profile_admin"))

        current_user.fullname = fullname
        current_user.email = email
        current_user.phone = phone if phone else None

        if password or confirm_password:
            if password != confirm_password:
                flash("Konfirmasi password tidak sama.", "error")
                return redirect(url_for("auth.profile_admin"))

            current_user.password = generate_password_hash(password)

        if profile_image and profile_image.filename != "":
            if not allowed_file(profile_image.filename):
                flash("Format foto harus PNG, JPG, JPEG, atau WEBP.", "error")
                return redirect(url_for("auth.profile_admin"))

            filename = secure_filename(profile_image.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"

            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "profile")
            os.makedirs(upload_folder, exist_ok=True)

            save_path = os.path.join(upload_folder, unique_filename)
            profile_image.save(save_path)

            if current_user.profile_image:
                old_path = os.path.join(current_app.root_path, current_user.profile_image.lstrip("/"))
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass

            current_user.profile_image = f"/static/uploads/profile/{unique_filename}"

        db.session.commit()
        flash("Profil admin berhasil diperbarui.", "success")
        return redirect(url_for("auth.profile_admin"))

    return render_template("profil_admin.html", active="profile_admin")


# =======================
# LOGOUT
# =======================
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Berhasil logout.", "success")
    return redirect(url_for("auth.login"))