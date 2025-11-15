# EduConnect - Online Learning Platform

EduConnect adalah platform pembelajaran online yang dibangun menggunakan arsitektur microservices dengan 5 layanan terpisah, masing-masing memiliki database sendiri.

## Arsitektur

Aplikasi ini menggunakan arsitektur microservices dengan API Gateway sebagai single entry point:

### API Gateway (Port: 5000)
- Single entry point untuk semua request dari frontend
- Routing request ke service terkait
- Centralized authentication handling
- Health check untuk semua services

### Microservices (5 Services)

1. User & Authentication Service (Port: 5001)
   - Manajemen pengguna
   - Registrasi dan autentikasi
   - JWT token management

2. Course Management Service (Port: 5002)
   - Manajemen kursus
   - CRUD operations untuk kursus
   - Kategorisasi dan filtering

3. Enrollment Service (Port: 5003)
   - Pendaftaran kursus
   - Manajemen enrollment
   - Tracking status enrollment

4. Learning Progress Service (Port: 5004)
   - Tracking progress pembelajaran
   - Completion percentage
   - Time spent tracking
   - Modules dan Tasks management

5. Review & Rating Service (Port: 5005)
   - Ulasan dan rating kursus
   - Statistik rating
   - Review management

## Fitur

- Registrasi dan Login pengguna
- Browse dan filter kursus
- Enroll ke kursus
- Tracking progress pembelajaran
- Modules pembelajaran dengan toggle view
- Tasks dan submissions
- Review dan rating kursus
- UI modern dengan animasi smooth
- Responsive design
- Real-time updates

### Ringkas:

1. **Setup MySQL Database (PILIH SALAH SATU):**
```bash
# buka termiinal di vsc dan run ini pertama kali
python setup_database.py

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Jalankan Services (Terminal 1):**
```bash
python run_services.py
```

4. **Jalankan Frontend (Terminal 2):**
```bash
python serve_frontend.py
```

5. **Akses di Browser:**
   - Browser akan terbuka otomatis di `http://localhost:8000`
   - Login dengan: `admin` / `admin123`
   - Atau langsung sign up saja


## Struktur Project

```
EduConnect/
├── services/
│   ├── user_service/
│   │   ├── app.py
│   │   └── user_service.db (auto-generated)
│   ├── course_service/
│   │   ├── app.py
│   │   └── course_service.db (auto-generated)
│   ├── enrollment_service/
│   │   ├── app.py
│   │   └── enrollment_service.db (auto-generated)
│   ├── progress_service/
│   │   ├── app.py
│   │   └── progress_service.db (auto-generated)
│   └── review_service/
│       ├── app.py
│       └── review_service.db (auto-generated)
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── api_gateway/
│   └── app.py
├── run_services.py
├── serve_frontend.py
├── requirements.txt
├── start.bat (Windows)
├── start.sh (Linux/Mac)
└── README.md
```

## Database

Setiap service menggunakan MySQL database terpisah untuk isolasi data:
- `educonnect_user` - User Service (menyimpan data user, password terenkripsi)
- `educonnect_course` - Course Service (menyimpan data kursus)
- `educonnect_enrollment` - Enrollment Service (menyimpan data enrollment user)
- `educonnect_progress` - Progress Service (menyimpan data progress pembelajaran user, modules, tasks)
- `educonnect_review` - Review Service (menyimpan data review dan rating)

## Fitur UI

- Modern dan responsive design
- Smooth animations
- Interactive course cards
- Progress tracking visualization
- Modules dengan toggle view (Modules/Tasks)
- Review and rating system
- Modal dialogs
- Toast notifications
- Loading indicators

## Authentication & Security

- **JWT Authentication**: Menggunakan JSON Web Tokens untuk autentikasi
- **Password Encryption**: Password dienkripsi menggunakan `werkzeug.security` (bcrypt-based)
- **API Gateway**: Semua request melalui API Gateway sebagai single entry point
- **Token Storage**: Token disimpan di localStorage browser
- **Token Expiry**: Token berlaku selama 24 jam

### User Default untuk Testing

Setelah service pertama kali dijalankan, akan dibuat user default:

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Student User:**
- Username: `student`
- Password: `student123`

**Cara Login:**
1. Buka website di `http://localhost:8000`
2. Klik tombol "Login" di navbar
3. Masukkan username dan password
4. Klik "Login"

Atau bisa juga membuat user baru dengan klik "Sign Up". 
## Catatan

- **API Gateway**: Semua request dari frontend hanya melalui API Gateway (port 5000)
- **Database MySQL**: Setiap service menggunakan database MySQL terpisah
- **Port Services**: 
  - API Gateway: 5000
  - User Service: 5001
  - Course Service: 5002
  - Enrollment Service: 5003
  - Progress Service: 5004
  - Review Service: 5005
- **Sample Data**: Sample data kursus, modules, dan tasks akan dibuat otomatis saat service pertama kali dijalankan
- **Frontend**: Menggunakan vanilla JavaScript (tidak memerlukan build process)
- **Security**: Password user terenkripsi, JWT untuk authentication
- **Pastikan**: MySQL running dan semua services berjalan sebelum mengakses frontend

## API Endpoints

**Semua endpoint diakses melalui API Gateway (http://localhost:5000)**

### Authentication
- `POST /api/auth/register` - Registrasi pengguna baru
- `POST /api/auth/login` - Login pengguna

### User Service (Port: 5001, via Gateway)
- `GET /api/users/me` - Get current user (requires auth)
- `GET /api/users/<id>` - Get user by ID (requires auth)
- `GET /api/users` - Get all users (requires auth)
- `PUT /api/users/<id>` - Update user (requires auth)
- `DELETE /api/users/<id>` - Delete user (requires auth)

### Course Service (Port: 5002, via Gateway)
- `GET /api/courses` - Get all courses
- `GET /api/courses/<id>` - Get course by ID
- `POST /api/courses` - Create new course
- `PUT /api/courses/<id>` - Update course
- `DELETE /api/courses/<id>` - Delete course

### Enrollment Service (Port: 5003, via Gateway)
- `GET /api/enrollments` - Get enrollments (with filters)
- `POST /api/enrollments` - Create enrollment
- `PUT /api/enrollments/<id>` - Update enrollment
- `DELETE /api/enrollments/<id>` - Delete enrollment

### Progress Service (Port: 5004, via Gateway)
- `GET /api/progress` - Get progress records
- `POST /api/progress` - Create progress record
- `PUT /api/progress/<id>` - Update progress
- `GET /api/progress/user/<user_id>/course/<course_id>` - Get user course progress
- `GET /api/modules?course_id=<id>` - Get modules for course
- `GET /api/modules/<id>` - Get module by ID
- `GET /api/tasks?course_id=<id>` - Get tasks for course
- `GET /api/tasks/user/<user_id>/course/<course_id>` - Get user tasks with status
- `POST /api/submissions` - Submit task
- `GET /api/submissions/user/<user_id>/task/<task_id>` - Get user submission

### Review Service (Port: 5005, via Gateway)
- `GET /api/reviews` - Get reviews (with filters)
- `POST /api/reviews` - Create review
- `PUT /api/reviews/<id>` - Update review
- `DELETE /api/reviews/<id>` - Delete review
- `GET /api/reviews/course/<course_id>/stats` - Get course review statistics

## Anggota
1. Darvesh Gladwin Musyaffa: Perancangan Arsitektur Microservice, Membantu Pembuatan Website, Pembuatan Update dan Delete pada Profile
   Bertanggung jawab pada pada Service Courses, Pembuatan UI Design, Bux Fixing
2. Muhammad Luthfi Tukhfattur Romadhoni: Perancangan Arsitektur Microservice, Pembuatan Website, Bug Fixing, Pembuatan Sign Up dan Login
   Pembuatan Tasks and Modules pada Courses; My Courses; dan Proggress, Bertanggung jawab pada pada Service Proggress, Pembuatan UI Design
   



## Kontributor

Dibuat untuk keperluan pembelajaran EAI (Enterprise Application Integration). 

Dari Kelompok 2

Made with ❤
