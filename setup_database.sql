-- Script untuk setup database MySQL EduConnect
-- Jalankan script ini di MySQL untuk membuat database yang diperlukan

-- Buat database untuk setiap service
CREATE DATABASE IF NOT EXISTS educonnect_user CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS educonnect_course CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS educonnect_enrollment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS educonnect_progress CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS educonnect_review CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Buat user untuk aplikasi (opsional, bisa menggunakan root)
-- CREATE USER IF NOT EXISTS 'educonnect'@'localhost' IDENTIFIED BY 'your_password_here';
-- GRANT ALL PRIVILEGES ON educonnect_user.* TO 'educonnect'@'localhost';
-- GRANT ALL PRIVILEGES ON educonnect_course.* TO 'educonnect'@'localhost';
-- GRANT ALL PRIVILEGES ON educonnect_enrollment.* TO 'educonnect'@'localhost';
-- GRANT ALL PRIVILEGES ON educonnect_progress.* TO 'educonnect'@'localhost';
-- GRANT ALL PRIVILEGES ON educonnect_review.* TO 'educonnect'@'localhost';
-- FLUSH PRIVILEGES;

-- Tampilkan database yang telah dibuat
SHOW DATABASES LIKE 'educonnect_%';

