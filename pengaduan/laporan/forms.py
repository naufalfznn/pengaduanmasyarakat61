from django import forms
from .models import Masyarakat, Pengaduan, Petugas, Tanggapan
import hashlib

# ✅ Form Registrasi Masyarakat
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = Masyarakat
        fields = ['nik', 'nama', 'username', 'password', 'telp']

    def save(self, commit=True):
        masyarakat = super().save(commit=False)
        masyarakat.password = hashlib.sha256(self.cleaned_data['password'].encode()).hexdigest()  # Hash password
        if commit:
            masyarakat.save()
        return masyarakat

# ✅ Form Login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=25, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

# ✅ Form Pengaduan
class PengaduanForm(forms.ModelForm):
    class Meta:
        model = Pengaduan
        fields = ['kategori', 'lokasi', 'isi_laporan', 'foto']
        widgets = {
            'isi_laporan': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tuliskan laporan Anda'}),
            'lokasi': forms.TextInput(attrs={'placeholder': 'Masukkan lokasi'}),
        }

# ✅ Form Pembuatan Petugas (Admin bisa buat petugas)
class PetugasForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = Petugas
        fields = ['nama_petugas', 'username', 'password', 'telp']

    def save(self, commit=True):
        petugas = super().save(commit=False)
        petugas.password = hashlib.sha256(self.cleaned_data['password'].encode()).hexdigest()  # Hash password
        if commit:
            petugas.save()
        return petugas

# ✅ Form untuk Memberikan Tanggapan
class TanggapanForm(forms.ModelForm):
    class Meta:
        model = Tanggapan
        fields = ['tanggapan']
        widgets = {
            'tanggapan': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Masukkan tanggapan'}),
        }
