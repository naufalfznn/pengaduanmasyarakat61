from django.db import models

class Masyarakat(models.Model):
    nik = models.CharField(max_length=16, primary_key=True)
    nama = models.CharField(max_length=35)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=32)
    telp = models.CharField(max_length=13)

    class Meta:
        managed = False 
        db_table = 'masyarakat'

    def __str__(self):
        return self.nama

class Administrator(models.Model):
    id_admin = models.AutoField(primary_key=True)
    nama_admin = models.CharField(max_length=35)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=32)
    telp = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = 'administrator'

    def __str__(self):
        return self.nama_admin

from django.db import models

class Petugas(models.Model):
    id_petugas = models.AutoField(primary_key=True)
    nama_petugas = models.CharField(max_length=100)
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=64)  # Hash password menggunakan SHA-256
    telp = models.CharField(max_length=13)

    class Meta:
        db_table = 'petugas'

    def __str__(self):
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
    nik = models.ForeignKey('Masyarakat', on_delete=models.CASCADE, db_column='nik')  
    isi_laporan = models.TextField()
    foto = models.ImageField(upload_to='pengaduan_foto/', blank=True, null=True)  
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='lainnya')
    lokasi = models.CharField(max_length=255, default="Tidak diketahui") 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='tunggu')

    class Meta:
        db_table = 'pengaduan'

    def __str__(self):
        return f"{self.nik.nama} - {self.kategori} - {self.status}"


class Tanggapan(models.Model):
    id_tanggapan = models.AutoField(primary_key=True)
    id_pengaduan = models.ForeignKey(Pengaduan, on_delete=models.CASCADE, db_column='id_pengaduan')
    tgl_tanggapan = models.DateTimeField(auto_now_add=True)
    tanggapan = models.TextField()
    id_petugas = models.ForeignKey(Petugas, on_delete=models.CASCADE, db_column='id_petugas', null=True, blank=True)
    id_admin = models.ForeignKey(Administrator, on_delete=models.CASCADE, db_column='id_admin', null=True, blank=True)

    class Meta:
        db_table = 'tanggapan'

    def __str__(self):
        return f"Tanggapan oleh {self.id_petugas} untuk pengaduan {self.id_pengaduan}"
