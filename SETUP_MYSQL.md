# Setup MySQL Database untuk EduConnect

## 📋 Prerequisites

- MySQL Server terinstall (versi 5.7 atau lebih tinggi)
- MySQL client atau command line access
- Python dengan pip

## 🗄️ Setup Database

### 1. Login ke MySQL

```bash
mysql -u root -p
```

### 2. Jalankan Script Setup

```bash
mysql -u root -p < setup_database.sql
```

Atau copy-paste isi file `setup_database.sql` ke MySQL client.

### 3. Verifikasi Database

Setelah script dijalankan, verifikasi database telah dibuat:

```sql
SHOW DATABASES LIKE 'educonnect_%';
```

Anda harus melihat 5 database:
- `educonnect_user`
- `educonnect_course`
- `educonnect_enrollment`
- `educonnect_progress`
- `educonnect_review`

## ⚙️ Konfigurasi Environment

### 1. Copy file .env.example

```bash
cp .env.example .env
```

### 2. Edit file .env

Edit file `.env` dan sesuaikan dengan konfigurasi MySQL Anda:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Menjalankan Aplikasi

### 1. Pastikan MySQL Running

```bash
# Windows
net start MySQL

# Linux/Mac
sudo systemctl start mysql
# atau
sudo service mysql start
```

### 2. Jalankan Services

```bash
python run_services.py
```

Services akan otomatis membuat tabel di database saat pertama kali dijalankan.

### 3. Jalankan Frontend

```bash
python serve_frontend.py
```

## 🔍 Troubleshooting

### Error: "Access denied for user"

**Solusi:**
- Pastikan username dan password di `.env` benar
- Pastikan user memiliki privilege untuk membuat database dan tabel
- Jika menggunakan root, pastikan password sudah di-set

### Error: "Can't connect to MySQL server"

**Solusi:**
- Pastikan MySQL server sedang running
- Cek host dan port di `.env` (default: localhost:3306)
- Cek firewall jika menggunakan remote MySQL

### Error: "Unknown database"

**Solusi:**
- Jalankan script `setup_database.sql` terlebih dahulu
- Atau buat database secara manual:
  ```sql
  CREATE DATABASE educonnect_user;
  CREATE DATABASE educonnect_course;
  CREATE DATABASE educonnect_enrollment;
  CREATE DATABASE educonnect_progress;
  CREATE DATABASE educonnect_review;
  ```

### Error: "Table doesn't exist"

**Solusi:**
- Tabel akan dibuat otomatis saat service pertama kali dijalankan
- Pastikan user memiliki privilege CREATE TABLE
- Cek error log di terminal untuk detail error

## 📝 Catatan

- **Password Encryption**: Password user dienkripsi menggunakan `werkzeug.security.generate_password_hash()`
- **Database Separation**: Setiap service menggunakan database terpisah untuk isolasi data
- **Connection Pooling**: Menggunakan SQLAlchemy connection pooling untuk performa optimal
- **Charset**: Database menggunakan utf8mb4 untuk support emoji dan karakter unicode

## 🔐 Security Best Practices

1. **Jangan commit file .env** ke repository
2. **Gunakan user khusus** untuk aplikasi (bukan root)
3. **Set password yang kuat** untuk MySQL user
4. **Backup database** secara berkala
5. **Gunakan SSL** untuk koneksi production

## 📊 Database Schema

Tabel akan dibuat otomatis oleh SQLAlchemy saat service pertama kali dijalankan. Schema dapat dilihat di file `app.py` masing-masing service di bagian `Models`.

