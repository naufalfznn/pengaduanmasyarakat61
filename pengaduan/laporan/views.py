from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Administrator, Petugas, Masyarakat, Pengaduan, Tanggapan
from .forms import RegisterForm, LoginForm, PengaduanForm, PetugasForm, TanggapanForm
from django.contrib import messages
import hashlib
import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponse
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from django.db.models import Count
import matplotlib
matplotlib.use('Agg') 
from collections import Counter
from django.db.models.functions import TruncDate
from django.utils import timezone



def homepage(request):
    role = "public"  # Default untuk yang belum login

    if request.user.is_authenticated:
        username = request.user.username

        # Cek apakah user adalah masyarakat
        if Masyarakat.objects.filter(username=username).exists():
            role = "masyarakat"
        # Cek apakah user adalah petugas
        elif Petugas.objects.filter(username=username).exists():
            role = "petugas"
        # Cek apakah user adalah admin
        elif Administrator.objects.filter(username=username).exists():
            role = "admin"

    return render(request, 'homepage.html', {'role': role})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            masyarakat = form.save(commit=False)
            masyarakat.password = hashlib.sha256(masyarakat.password.encode()).hexdigest()
            masyarakat.save()
            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = hashlib.sha256(form.cleaned_data['password'].encode()).hexdigest()

            # Cek di tabel administrator
            admin = Administrator.objects.filter(username=username, password=password).first()
            if admin:
                request.session['user_id'] = admin.id_admin
                request.session['username'] = admin.username
                request.session['user_role'] = 'admin'
                messages.success(request, "Login berhasil sebagai Administrator.")
                return redirect('dashboard_admin')

            # Cek di tabel petugas
            petugas = Petugas.objects.filter(username=username, password=password).first()
            if petugas:
                request.session['user_id'] = petugas.id_petugas
                request.session['username'] = petugas.username
                request.session['user_role'] = 'petugas'
                messages.success(request, "Login berhasil sebagai Petugas.")
                return redirect('dashboard_petugas')

            # Cek di tabel masyarakat
            masyarakat = Masyarakat.objects.filter(username=username, password=password).first()
            if masyarakat:
                request.session['user_id'] = masyarakat.nik
                request.session['username'] = masyarakat.username
                request.session['user_role'] = 'masyarakat'
                messages.success(request, "Login berhasil sebagai Masyarakat.")
                return redirect('dashboard_masyarakat')

            messages.error(request, "Username atau password salah!")
    
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Anda telah logout.")
    return redirect('homepage')

def dashboard_admin(request):
    if request.session.get('user_role') == 'admin':
        # Ambil semua pengaduan
        pengaduan_list = Pengaduan.objects.all()

        # Ambil data pengaduan per hari
        pengaduan_per_hari = Pengaduan.objects.values('tgl_pengaduan').annotate(count=Count('id_pengaduan')).order_by('tgl_pengaduan')

        # Menyiapkan data untuk grafik
        tanggal_pengaduan = [str(item['tgl_pengaduan']) for item in pengaduan_per_hari]
        jumlah_per_hari = [item['count'] for item in pengaduan_per_hari]

        # Ambil total jumlah masyarakat dan petugas
        total_masyarakat = Masyarakat.objects.count()
        total_petugas = Petugas.objects.count()

        role = request.session.get('user_role', 'public')  # Ambil role dari session

        # Kirim data ke template
        return render(request, 'dashboard/admin_dashboard.html', {
            'pengaduan_list': pengaduan_list,
            'role': role,
            'total_masyarakat': total_masyarakat,
            'total_petugas': total_petugas,
            'tanggal_pengaduan': tanggal_pengaduan,
            'jumlah_per_hari': jumlah_per_hari
        })
    
    messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
    return redirect('login')

def dashboard_petugas(request):
    if request.session.get('user_role') == 'petugas':
        pengaduan_list = Pengaduan.objects.all()
        role = request.session.get('user_role', 'public')  # Ambil role dari session
        return render(request, 'dashboard/petugas_dashboard.html', {
            'pengaduan_list': pengaduan_list,
            'role': role
        })
    
    messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
    return redirect('login')

def dashboard_masyarakat(request):
    if 'user_role' in request.session and request.session['user_role'] == 'masyarakat':
        pengaduan_list = Pengaduan.objects.filter(nik=request.session['user_id'])
        role = request.session.get('user_role', 'public')  # Ambil role dari session
        return render(request, 'dashboard/masyarakat_dashboard.html', {
            'pengaduan_list': pengaduan_list,
            'role': role  # Kirim ke template
        })
    messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
    return redirect('login')

def buat_pengaduan(request):
    if 'user_role' not in request.session or request.session['user_role'] != 'masyarakat':
        messages.error(request, "Anda harus login sebagai masyarakat untuk membuat pengaduan.")
        return redirect('login')

    if request.method == 'POST':
        form = PengaduanForm(request.POST, request.FILES)
        if form.is_valid():
            pengaduan = form.save(commit=False)
            pengaduan.nik = Masyarakat.objects.get(nik=request.session['user_id'])
            pengaduan.tgl_pengaduan = timezone.now()
            pengaduan.status = 'tunggu'
            pengaduan.save()
            messages.success(request, "Pengaduan berhasil dikirim!")
            return redirect('dashboard_masyarakat')
    else:
        form = PengaduanForm()

    return render(request, 'pengaduan/buat_pengaduan.html', {'form': form})

def detail_pengaduan(request, id_pengaduan):
    pengaduan = get_object_or_404(Pengaduan, id_pengaduan=id_pengaduan)
    return render(request, 'pengaduan/detail_pengaduan.html', {'pengaduan': pengaduan})

def ubah_status_pengaduan(request, id_pengaduan):
    if 'user_role' not in request.session or request.session['user_role'] not in ['admin', 'petugas']:
        return HttpResponseForbidden("Anda tidak memiliki akses untuk mengubah status.")

    pengaduan = get_object_or_404(Pengaduan, id_pengaduan=id_pengaduan)

    if request.method == "POST":
        status_baru = request.POST.get("status")

        if status_baru in ["tunggu", "proses", "selesai"]:  # ✅ Hanya nilai valid
            pengaduan.status = status_baru
            pengaduan.save()
            messages.success(request, "Status pengaduan berhasil diperbarui.")
        else:
            messages.error(request, "Status tidak valid.")  # ❌ Jika ada error input

    return redirect('detail_pengaduan', id_pengaduan=id_pengaduan)

def daftar_pengaduan_adminpetugas(request):
    if 'user_role' not in request.session or request.session['user_role'] not in ['admin', 'petugas']:
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('login')

    pengaduan_list = Pengaduan.objects.all()  # Admin & Petugas bisa melihat semua pengaduan
    return render(request, 'pengaduan/daftar_pengaduan.html', {'pengaduan': pengaduan_list})

def daftar_pengaduan_masyarakat(request):
    if 'user_role' not in request.session or request.session['user_role'] != 'masyarakat':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('login')

    pengaduan_list = Pengaduan.objects.filter(nik=request.session['user_id'])  # Masyarakat hanya bisa melihat pengaduan mereka sendiri
    return render(request, 'pengaduan/daftar_pengaduan.html', {'pengaduan': pengaduan_list})

def daftar_pengaduan(request):
    if 'user_role' not in request.session:
        messages.error(request, "Silakan login terlebih dahulu.")
        return redirect('login')

    user_role = request.session['user_role']
    user_id = request.session['user_id']

    if user_role == 'masyarakat':
        pengaduan_list = Pengaduan.objects.filter(nik=user_id)  
    else:  
        pengaduan_list = Pengaduan.objects.all()

    return render(request, 'pengaduan/daftar_pengaduan.html', {'pengaduan_list': pengaduan_list})

def buat_petugas(request):
    if 'user_role' not in request.session or request.session['user_role'] != 'admin':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('dashboard_admin')

    if request.method == "POST":
        form = PetugasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Akun Petugas berhasil dibuat!")
            return redirect('dashboard_admin')
    else:
        form = PetugasForm()

    return render(request, 'admin/buat_petugas.html', {'form': form})



def beri_tanggapan(request, id_pengaduan):
    if 'user_role' not in request.session or request.session['user_role'] not in ['admin', 'petugas']:
        messages.error(request, "Anda harus login sebagai Admin atau Petugas untuk memberikan tanggapan.")
        return redirect('login')

    pengaduan = get_object_or_404(Pengaduan, id_pengaduan=id_pengaduan)
    user_id = request.session['user_id']
    user_role = request.session['user_role']

    admin = None
    petugas = None

    if user_role == 'admin':
        admin = Administrator.objects.filter(id_admin=user_id).first()
        if not admin:
            messages.error(request, "Akun Admin tidak ditemukan.")
            return redirect('dashboard_admin')

    elif user_role == 'petugas':
        petugas = Petugas.objects.filter(id_petugas=user_id).first()
        if not petugas:
            messages.error(request, "Akun Petugas tidak ditemukan.")
            return redirect('dashboard_petugas')

    if request.method == 'POST':
        form = TanggapanForm(request.POST)
        if form.is_valid():
            tanggapan = form.save(commit=False)
            tanggapan.id_pengaduan = pengaduan
            tanggapan.tgl_tanggapan = datetime.date.today()
            tanggapan.id_petugas = petugas 
            tanggapan.id_admin = admin  
            tanggapan.save()
            messages.success(request, "Tanggapan berhasil dikirim!")
            return redirect('detail_pengaduan', id_pengaduan=id_pengaduan)

    else:
        form = TanggapanForm()

    return render(request, 'pengaduan/beri_tanggapan.html', {'form': form, 'pengaduan': pengaduan})

def export_pengaduan_pdf(request):
    if 'user_role' not in request.session or request.session['user_role'] != 'admin':
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('login')

    pengaduan_list = Pengaduan.objects.all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, "Laporan Pengaduan Masyarakat")
    y = 730

    for pengaduan in pengaduan_list:
        pdf.drawString(100, y, f"{pengaduan.tgl_pengaduan} - {pengaduan.kategori} - {pengaduan.status}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_pengaduan.pdf"'
    return response

def export_pengaduan_excel(request):
    if 'user_role' not in request.session or request.session['user_role'] != 'admin':
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('login')

    pengaduan_list = Pengaduan.objects.all().values('tgl_pengaduan', 'nik__nama', 'kategori', 'status')

    df = pd.DataFrame(list(pengaduan_list))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="laporan_pengaduan.xlsx"'
    df.to_excel(response, index=False)
    return response

def kelola_akun(request):
    if 'user_role' not in request.session or request.session['user_role'] != 'admin':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('login')

    masyarakat_list = Masyarakat.objects.all()
    petugas_list = Petugas.objects.all()
    jumlah_masyarakat = Masyarakat.objects.count()
    jumlah_petugas = Petugas.objects.count()

    # 📊 Grafik Pengaduan per Hari
    # TruncDate digunakan untuk mengelompokkan pengaduan berdasarkan tanggal
    pengaduan_per_hari = Pengaduan.objects.annotate(date=TruncDate('tanggal_pengaduan')) \
                                          .values('date') \
                                          .annotate(count=Count('date')) \
                                          .order_by('date')

    # Menyusun data untuk grafik
    dates = [item['date'] for item in pengaduan_per_hari]
    counts = [item['count'] for item in pengaduan_per_hari]

    # Membuat grafik garis
    fig, ax = plt.subplots()
    ax.plot(dates, counts, marker='o', color='b', label='Pengaduan per Hari')
    ax.set_xlabel('Tanggal')
    ax.set_ylabel('Jumlah Pengaduan')
    ax.set_title('Grafik Pengaduan per Hari')
    ax.grid(True)
    ax.legend()

    # Menyimpan grafik ke dalam buffer sebagai PNG
    buffer = BytesIO()
    plt.xticks(rotation=45)  # Agar tanggal tidak saling bertumpuk
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'admin/kelola_akun.html', {
        'masyarakat_list': masyarakat_list,
        'petugas_list': petugas_list,
        'jumlah_masyarakat': jumlah_masyarakat,
        'jumlah_petugas': jumlah_petugas,
        'grafik_pengaduan': image_base64
    })

def ubah_status_akun(request, role, user_id):
    if 'user_role' not in request.session or request.session['user_role'] != 'admin':
        messages.error(request, "Anda tidak memiliki akses.")
        return redirect('login')

    if role == "masyarakat":
        user = get_object_or_404(Masyarakat, nik=user_id)
    elif role == "petugas":
        user = get_object_or_404(Petugas, id_petugas=user_id)
    else:
        messages.error(request, "Role tidak valid.")
        return redirect('kelola_akun')

    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"Akun {role} {user.username} telah {'diaktifkan' if user.is_active else 'dinonaktifkan'}.")

    return redirect('kelola_akun')