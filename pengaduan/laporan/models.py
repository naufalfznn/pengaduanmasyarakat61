from django.db import models
from django.contrib.auth.hashers import make_password

class Masyarakat(models.Model):
    nik = models.CharField(max_length=16, primary_key=True)
    nama = models.CharField(max_length=35)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=64)  # Menggunakan SHA-256
    telp = models.CharField(max_length=13)

    class Meta:
        managed = False  # Tidak akan dibuat oleh Django, hanya digunakan untuk query
        db_table = 'masyarakat'

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)  # Hashing password sebelum menyimpan
        super().save(*args, **kwargs)

    def _str_(self):
        return self.nama


class Administrator(models.Model):
    id_admin = models.AutoField(primary_key=True)
    nama_admin = models.CharField(max_length=35)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=64)  # Menggunakan SHA-256
    telp = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = 'administrator'

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def _str_(self):
        return self.nama_admin


class Petugas(models.Model):
    id_petugas = models.AutoField(primary_key=True)
    nama_petugas = models.CharField(max_length=100)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=64)  # Menggunakan SHA-256
    telp = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = 'petugas'

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def _str_(self):
        return self.nama_petugas


class Pengaduan(models.Model):
    STATUS_CHOICES = [
        ('tunggu', 'Belum diproses'),
        ('proses', 'Sedang diproses'),
        ('selesai', 'Selesai'),
    ]

    KATEGORI_CHOICES = [
        ('infrastruktur', 'Infrastruktur'),
        ('lingkungan', 'Lingkungan'),
        ('kriminal', 'Kriminal'),
        ('pelayanan', 'Pelayanan Publik'),
        ('lainnya', 'Lainnya')
    ]

    id_pengaduan = models.AutoField(primary_key=True)
    tgl_pengaduan = models.DateField(auto_now_add=True)
    nik = models.ForeignKey(Masyarakat, on_delete=models.CASCADE, db_column='nik', related_name="pengaduan_masyarakat")  
    isi_laporan = models.TextField()
    foto = models.ImageField(upload_to='pengaduan_foto/', blank=True, null=True)  
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='lainnya')
    lokasi = models.CharField(max_length=255, default="Tidak diketahui") 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='tunggu')

    class Meta:
        managed = False
        db_table = 'pengaduan'

    def _str_(self):
        return f"{self.nik.nama} - {self.kategori} - {self.status}"


class Tanggapan(models.Model):
    id_tanggapan = models.AutoField(primary_key=True)
    id_pengaduan = models.ForeignKey(Pengaduan, on_delete=models.CASCADE, db_column='id_pengaduan', related_name="tanggapan_pengaduan")
    tgl_tanggapan = models.DateTimeField(auto_now_add=True)
    tanggapan = models.TextField()
    id_petugas = models.ForeignKey(Petugas, on_delete=models.CASCADE, db_column='id_petugas', null=True, blank=True, related_name="tanggapan_petugas")
    id_admin = models.ForeignKey(Administrator, on_delete=models.CASCADE, db_column='id_admin', null=True, blank=True, related_name="tanggapan_admin")

    class Meta:
        managed = False
        db_table = 'tanggapan'

    def _str_(self):
        return f"Tanggapan untuk {self.id_pengaduan.id_pengaduan} pada {self.tgl_tanggapan}"