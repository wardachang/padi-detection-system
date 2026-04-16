import os
import uuid

import calendar
from models.varietas_padi import VarietasPadi
from models.jadwal_tanam import JadwalTanam
from models.varietas_padi import VarietasPadi
from datetime import datetime, date, timedelta
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
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


# =======================
# LOGIN
# =======================
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        return redirect(url_for("auth.dashboard"))

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
        return redirect(url_for("auth.dashboard"))

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

def get_countdown_jadwal(jadwal):
    today = date.today()

    if not jadwal:
        return None

    tahapan = [
        ("Semai", jadwal.tanggal_semai),
        ("Penyemaian", jadwal.tanggal_penyemaian),
        ("Penanaman", jadwal.tanggal_penanaman),
        ("Pemupukan 1", jadwal.tanggal_pemupukan_1),
        ("Pemupukan 2", jadwal.tanggal_pemupukan_2),
        ("Panen", jadwal.tanggal_panen),
    ]

    for nama, tgl in tahapan:
        if tgl and tgl >= today:
            selisih = (tgl - today).days

            if selisih == 0:
                return f"Hari ini {nama}"
            elif selisih == 1:
                return f"Besok {nama}"
            else:
                return f"{selisih} hari menuju {nama}"

    return "Semua tahapan selesai"

@auth.route("/dashboard")
@login_required
def dashboard():
    # =========================
    # RIWAYAT DETEKSI
    # =========================
    histories = RiwayatDeteksi.query.filter_by(user_id=current_user.id) \
        .order_by(RiwayatDeteksi.created_at.desc()) \
        .all()

    total_deteksi = len(histories)
    total_sehat = len([h for h in histories if h.hasil == "Healthy Rice Leaf"])
    total_penyakit = total_deteksi - total_sehat

    # =========================
    # JADWAL TANAM
    # =========================
    jadwal = JadwalTanam.query.filter_by(user_id=current_user.id) \
        .order_by(JadwalTanam.created_at.desc()) \
        .first()

    # =========================
    # COUNTDOWN
    # =========================
    countdown = None
    if jadwal:
        countdown = get_countdown_jadwal(jadwal)

    # =========================
    # PROGRESS BAR (🔥 INI YANG BARU)
    # =========================
    progress_percent = 0

    if jadwal:
        total_hari = (jadwal.tanggal_panen - jadwal.tanggal_semai).days
        hari_berjalan = (date.today() - jadwal.tanggal_semai).days

        if total_hari > 0:
            progress_percent = max(0, min(100, int((hari_berjalan / total_hari) * 100)))

    # =========================
    # RENDER
    # =========================
    return render_template(
        "beranda_user.html",
        active="beranda_user",
        histories=histories[:5],
        total_deteksi=total_deteksi,
        total_sehat=total_sehat,
        total_penyakit=total_penyakit,
        jadwal=jadwal,
        countdown=countdown,
        progress_percent=progress_percent   # 🔥 WAJIB ADA
    )

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


@auth.route('/admin/varietas')
@login_required
def varietas():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("auth.dashboard"))

    varietas_list = VarietasPadi.query.order_by(VarietasPadi.nama.asc()).all()

    return render_template(
        "varietas_padi.html",
        varietas_list=varietas_list,
        active="varietas_admin"
    )
    
@auth.route('/admin/varietas/tambah', methods=['GET', 'POST'])
@login_required
def tambah_varietas():
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("auth.dashboard"))

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        hari_penyemaian = request.form.get('hari_penyemaian', type=int)
        hari_penanaman = request.form.get('hari_penanaman', type=int)
        hari_pemupukan_1 = request.form.get('hari_pemupukan_1', '').strip()
        hari_pemupukan_2 = request.form.get('hari_pemupukan_2', '').strip()
        hari_panen = request.form.get('hari_panen', type=int)

        if not nama or hari_penyemaian is None or hari_penanaman is None or hari_panen is None:
            flash("Nama, hari penyemaian, hari penanaman, dan hari panen wajib diisi.", "error")
            return redirect(url_for('auth.tambah_varietas'))

        cek = VarietasPadi.query.filter_by(nama=nama).first()
        if cek:
            flash("Varietas sudah ada.", "error")
            return redirect(url_for('auth.tambah_varietas'))

        data = VarietasPadi(
            nama=nama,
            hari_penyemaian=hari_penyemaian,
            hari_penanaman=hari_penanaman,
            hari_pemupukan_1=int(hari_pemupukan_1) if hari_pemupukan_1 else None,
            hari_pemupukan_2=int(hari_pemupukan_2) if hari_pemupukan_2 else None,
            hari_panen=hari_panen
        )

        db.session.add(data)
        db.session.commit()

        flash("Varietas berhasil ditambahkan.", "success")
        return redirect(url_for('auth.varietas'))

    return render_template(
        'form_varietas.html',
        title='Tambah Varietas',
        form_action=url_for('auth.tambah_varietas'),
        varietas=None,
        active='varietas_admin'
    )
    
@auth.route('/admin/varietas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_varietas(id):
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("auth.dashboard"))

    varietas = VarietasPadi.query.get_or_404(id)

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        hari_penyemaian = request.form.get('hari_penyemaian', type=int)
        hari_penanaman = request.form.get('hari_penanaman', type=int)
        hari_pemupukan_1 = request.form.get('hari_pemupukan_1', '').strip()
        hari_pemupukan_2 = request.form.get('hari_pemupukan_2', '').strip()
        hari_panen = request.form.get('hari_panen', type=int)

        if not nama or hari_penyemaian is None or hari_penanaman is None or hari_panen is None:
            flash("Nama, hari penyemaian, hari penanaman, dan hari panen wajib diisi.", "error")
            return redirect(url_for('auth.edit_varietas', id=id))

        cek = VarietasPadi.query.filter(
            VarietasPadi.nama == nama,
            VarietasPadi.id != id
        ).first()
        if cek:
            flash("Nama varietas sudah dipakai.", "error")
            return redirect(url_for('auth.edit_varietas', id=id))

        varietas.nama = nama
        varietas.hari_penyemaian = hari_penyemaian
        varietas.hari_penanaman = hari_penanaman
        varietas.hari_pemupukan_1 = int(hari_pemupukan_1) if hari_pemupukan_1 else None
        varietas.hari_pemupukan_2 = int(hari_pemupukan_2) if hari_pemupukan_2 else None
        varietas.hari_panen = hari_panen

        db.session.commit()

        flash("Varietas berhasil diperbarui.", "success")
        return redirect(url_for('auth.varietas'))

    return render_template(
        'form_varietas.html',
        title='Edit Varietas',
        form_action=url_for('auth.edit_varietas', id=id),
        varietas=varietas,
        active='varietas_admin'
    )

#delete
@auth.route('/admin/varietas/delete/<int:id>', methods=['POST'])
@login_required
def delete_varietas(id):
    if current_user.role != "admin":
        flash("Akses ditolak.", "error")
        return redirect(url_for("auth.dashboard"))

    varietas = VarietasPadi.query.get_or_404(id)

    dipakai = JadwalTanam.query.filter_by(varietas_id=id).first()
    if dipakai:
        flash("Varietas tidak bisa dihapus karena sudah dipakai user.", "error")
        return redirect(url_for('auth.varietas'))

    db.session.delete(varietas)
    db.session.commit()

    flash("Varietas berhasil dihapus.", "success")
    return redirect(url_for('auth.varietas'))

#jadwal tanam user
@auth.route("/jadwal_user", methods=["GET", "POST"])
@login_required
def jadwal_user():
    varietas_list = VarietasPadi.query.order_by(VarietasPadi.nama.asc()).all()
    today = date.today()

    jadwal = JadwalTanam.query.filter_by(user_id=current_user.id) \
        .order_by(JadwalTanam.created_at.desc()) \
        .first()

    if request.method == "POST":
        varietas_id = request.form.get("varietas_id", type=int)
        tanggal_semai_str = request.form.get("tanggal_semai")

        if not varietas_id or not tanggal_semai_str:
            flash("Varietas padi dan tanggal semai wajib diisi.", "error")
            return redirect(url_for("auth.jadwal_user"))

        varietas = VarietasPadi.query.get(varietas_id)
        if not varietas:
            flash("Varietas tidak ditemukan.", "error")
            return redirect(url_for("auth.jadwal_user"))

        try:
            tanggal_semai = datetime.strptime(tanggal_semai_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Format tanggal semai tidak valid.", "error")
            return redirect(url_for("auth.jadwal_user"))

        tanggal_penyemaian = tanggal_semai + timedelta(days=varietas.hari_penyemaian)
        tanggal_penanaman = tanggal_semai + timedelta(days=varietas.hari_penanaman)
        tanggal_pemupukan_1 = (
            tanggal_semai + timedelta(days=varietas.hari_pemupukan_1)
            if varietas.hari_pemupukan_1 is not None else None
        )
        tanggal_pemupukan_2 = (
            tanggal_semai + timedelta(days=varietas.hari_pemupukan_2)
            if varietas.hari_pemupukan_2 is not None else None
        )
        tanggal_panen = tanggal_semai + timedelta(days=varietas.hari_panen)

        jadwal_lama = JadwalTanam.query.filter_by(user_id=current_user.id).first()
        if jadwal_lama:
            db.session.delete(jadwal_lama)
            db.session.flush()

        jadwal_baru = JadwalTanam(
            user_id=current_user.id,
            varietas_id=varietas.id,
            tanggal_semai=tanggal_semai,
            tanggal_penyemaian=tanggal_penyemaian,
            tanggal_penanaman=tanggal_penanaman,
            tanggal_pemupukan_1=tanggal_pemupukan_1,
            tanggal_pemupukan_2=tanggal_pemupukan_2,
            tanggal_panen=tanggal_panen
        )

        db.session.add(jadwal_baru)
        db.session.commit()

        flash("Jadwal tanam berhasil dibuat.", "success")
        return redirect(url_for("auth.jadwal_user"))

    selected_varietas = jadwal.varietas if jadwal else None

    steps = []
    total_durasi = 0
    waktu_berjalan = 0
    sisa_waktu = 0
    progress_percent = 0
    calendar_days = []
    current_month_label = today.strftime("%B %Y")

    if jadwal:
        total_durasi = (jadwal.tanggal_panen - jadwal.tanggal_semai).days
        waktu_berjalan = max(0, min((today - jadwal.tanggal_semai).days, total_durasi))
        sisa_waktu = max(0, (jadwal.tanggal_panen - today).days)

        if total_durasi > 0:
            progress_percent = min(100, max(0, (waktu_berjalan / total_durasi) * 100))

        step_candidates = [
            {"label": "Semai", "icon": "fa-seedling", "date": jadwal.tanggal_semai},
            {"label": "Penyemaian", "icon": "fa-droplet", "date": jadwal.tanggal_penyemaian},
            {"label": "Penanaman", "icon": "fa-hand-holding-droplet", "date": jadwal.tanggal_penanaman},
            {"label": "Pemupukan 1", "icon": "fa-flask", "date": jadwal.tanggal_pemupukan_1},
            {"label": "Pemupukan 2", "icon": "fa-flask", "date": jadwal.tanggal_pemupukan_2},
            {"label": "Panen", "icon": "fa-wheat-awn", "date": jadwal.tanggal_panen},
        ]

        steps = [
            {
                "label": step["label"],
                "icon": step["icon"],
                "date": step["date"],
                "done": step["date"] is not None and today >= step["date"],
            }
            for step in step_candidates if step["date"] is not None
        ]

        active_month = jadwal.tanggal_semai.month
        active_year = jadwal.tanggal_semai.year
        current_month_label = jadwal.tanggal_semai.strftime("%B %Y")

        important_dates = set()
        for step in steps:
            if step["date"] and step["date"].month == active_month and step["date"].year == active_year:
                important_dates.add(step["date"])

        cal = calendar.Calendar(firstweekday=6)
        for day in cal.itermonthdates(active_year, active_month):
            calendar_days.append({
                "day": day.day,
                "in_month": day.month == active_month,
                "is_today": day == today,
                "is_event": day in important_dates
            })

    return render_template(
        "jadwal_user.html",
        active="jadwal_user",
        varietas_list=varietas_list,
        jadwal=jadwal,
        selected_varietas=selected_varietas,
        steps=steps,
        total_durasi=total_durasi,
        waktu_berjalan=waktu_berjalan,
        sisa_waktu=sisa_waktu,
        progress_percent=progress_percent,
        calendar_days=calendar_days,
        current_month_label=current_month_label,
        today=today
    )

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