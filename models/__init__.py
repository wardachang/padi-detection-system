from .kelompok_tani import KelompokTani, user_kelompok_tani
from .user import User
from .riwayat_deteksi import RiwayatDeteksi
from .penyakit import Penyakit
from .penanganan_penyakit import PenangananPenyakit
from .varietas_padi import VarietasPadi
from .jadwal_tanam import JadwalTanam

# Model ini jangan di-import dulu karena foreign key-nya mengarah ke tabel yang tidak ada:
# from .hasil_deteksi import HasilDeteksi

# Model lama / backup / tidak dipakai
# from .jadwal_pengelolaan_bak import JadwalPengelolaan
# from .jadwal_varietas_bak import JadwalVarietas
# from .jadwal_user_bak import JadwalUser