from django.urls import path
from .views import (
    homepage, register, login_view, logout_view,
    dashboard_admin, dashboard_petugas, dashboard_masyarakat,
    buat_pengaduan, daftar_pengaduan, detail_pengaduan, ubah_status_pengaduan,
    buat_petugas, beri_tanggapan, export_pengaduan_pdf,
    kelola_akun, ubah_status_akun, profil_masyarakat, profil_petugas
)

urlpatterns = [
    path('', homepage, name='homepage'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/petugas/', dashboard_petugas, name='dashboard_petugas'),
    path('dashboard/masyarakat/', dashboard_masyarakat, name='dashboard_masyarakat'),

    # Pengaduan
    path('pengaduan/buat/', buat_pengaduan, name='buat_pengaduan'),
    path('pengaduan/', daftar_pengaduan, name='daftar_pengaduan'),
    path('pengaduan/<int:id_pengaduan>/', detail_pengaduan, name='detail_pengaduan'),
    path('pengaduan/<int:id_pengaduan>/ubah_status/', ubah_status_pengaduan, name='ubah_status_pengaduan'),

    # Buat Petugas
    path('buat_petugas/', buat_petugas, name='buat_petugas'),

    path('pengaduan/<int:id_pengaduan>/tanggapan/', beri_tanggapan, name='beri_tanggapan'),

    path('laporan/pdf/', export_pengaduan_pdf, name='export_pengaduan_pdf'),

    path('kelola_akun/', kelola_akun, name='kelola_akun'),
    path('ubah_status_akun/<str:role>/<str:user_id>/', ubah_status_akun, name='ubah_status_akun'),

    path('profil/masyarakat/', profil_masyarakat, name='profil_masyarakat'),
    path('profil/petugas/', profil_petugas, name='profil_petugas'),

]
