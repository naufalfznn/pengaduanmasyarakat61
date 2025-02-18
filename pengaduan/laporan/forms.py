from django import forms
from .models import Masyarakat, Pengaduan, Petugas, Tanggapan
import hashlib

# Form Registrasi Masyarakat
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

# Form Login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=25, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

# Form Pengaduan
class PengaduanForm(forms.ModelForm):
    kategori_lainnya = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'id': 'kategori_lainnya', 'style': 'display:none;', 'placeholder': 'Masukkan kategori lainnya'})
    )

    class Meta:
        model = Pengaduan
        fields = ['kategori', 'kategori_lainnya', 'isi_laporan', 'foto', 'lokasi']
        widgets = {
            'kategori': forms.Select(attrs={'id': 'kategori'}),
        }

    def __init__(self, *args, **kwargs):
        super(PengaduanForm, self).__init__(*args, **kwargs)

        # Pastikan kategori default adalah "Infrastruktur"
        if 'infrastruktur' in dict(self.fields['kategori'].choices).keys():
            self.fields['kategori'].initial = 'infrastruktur'

    def clean(self):
        cleaned_data = super().clean()
        kategori = cleaned_data.get('kategori')
        kategori_lainnya = cleaned_data.get('kategori_lainnya')

        # Validasi: Jika "Lainnya" dipilih, kategori_lainnya harus diisi
        if kategori == 'lainnya' and not kategori_lainnya:
            self.add_error('kategori_lainnya', "Silakan isi kategori lainnya.")

        return cleaned_data
    
# Form Pembuatan Petugas (Admin bisa buat petugas)
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

# Form untuk Memberikan Tanggapan
class TanggapanForm(forms.ModelForm):
    class Meta:
        model = Tanggapan
        fields = ['tanggapan']
        widgets = {
            'tanggapan': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Masukkan tanggapan'}),
        }

class ProfilMasyarakatForm(forms.ModelForm):
    class Meta:
        model = Masyarakat
        fields = ['nama', 'username', 'telp', 'foto_profil']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'telp': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfilPetugasForm(forms.ModelForm):
    class Meta:
        model = Petugas
        fields = ['nama_petugas', 'username', 'telp', 'foto_profil']
        widgets = {
            'nama_petugas': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'telp': forms.TextInput(attrs={'class': 'form-control'}),
        }