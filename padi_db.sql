-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 23, 2026 at 07:07 AM
-- Server version: 8.0.30
-- PHP Version: 8.3.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `padi_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `detail_jadwal_pengelolaan`
--

CREATE TABLE `detail_jadwal_pengelolaan` (
  `id_deteksi` int NOT NULL,
  `id_user` int NOT NULL,
  `waktu_deteksi` datetime DEFAULT NULL,
  `jenis_input` varchar(50) NOT NULL,
  `url_gambar` varchar(255) DEFAULT NULL,
  `teks_input` text,
  `versi_model` varchar(50) DEFAULT NULL,
  `status_deteksi` varchar(50) DEFAULT NULL,
  `catatan` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `foto_hasil_penyakit`
--

CREATE TABLE `foto_hasil_penyakit` (
  `id_foto` int NOT NULL,
  `id_penyakit` int DEFAULT NULL,
  `url_foto` varchar(255) NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `foto_utama` tinyint(1) DEFAULT NULL,
  `dibuat_pada` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hasil_deteksi`
--

CREATE TABLE `hasil_deteksi` (
  `id_hasil` int NOT NULL,
  `id_deteksi` int DEFAULT NULL,
  `id_penyakit` int DEFAULT NULL,
  `tingkat_keyakinan` float DEFAULT NULL,
  `ringkasan` text,
  `snapshot_rekomendasi` text,
  `dibuat_pada` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `jadwal_tanam`
--

CREATE TABLE `jadwal_tanam` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `varietas_id` int NOT NULL,
  `tanggal_semai` date NOT NULL,
  `tanggal_penyemaian` date NOT NULL,
  `tanggal_penanaman` date NOT NULL,
  `tanggal_pemupukan_1` date DEFAULT NULL,
  `tanggal_pemupukan_2` date DEFAULT NULL,
  `tanggal_panen` date NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `jadwal_tanam`
--

INSERT INTO `jadwal_tanam` (`id`, `user_id`, `varietas_id`, `tanggal_semai`, `tanggal_penyemaian`, `tanggal_penanaman`, `tanggal_pemupukan_1`, `tanggal_pemupukan_2`, `tanggal_panen`, `created_at`) VALUES
(9, 4, 2, '2026-03-27', '2026-03-27', '2026-04-13', '2026-05-02', '2026-05-12', '2026-06-05', '2026-04-20 14:08:26');

-- --------------------------------------------------------

--
-- Table structure for table `penanganan_penyakit`
--

CREATE TABLE `penanganan_penyakit` (
  `id_penanganan` int NOT NULL,
  `id_penyakit` int DEFAULT NULL,
  `jenis_penanganan` varchar(50) DEFAULT NULL,
  `judul_penanganan` varchar(100) DEFAULT NULL,
  `dosis` varchar(100) DEFAULT NULL,
  `cara_aplikasi` text,
  `catatan` text,
  `urutan` int DEFAULT NULL,
  `dibuat_pada` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `penyakit`
--

CREATE TABLE `penyakit` (
  `id_penyakit` int NOT NULL,
  `kode_penyakit` varchar(50) DEFAULT NULL,
  `nama_penyakit` varchar(100) NOT NULL,
  `deskripsi` text,
  `penyebab` text,
  `tingkat_keparahan` varchar(50) DEFAULT NULL,
  `dibuat_oleh` int DEFAULT NULL,
  `dibuat_pada` datetime DEFAULT NULL,
  `diperbarui_pada` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `riwayat_deteksi`
--

CREATE TABLE `riwayat_deteksi` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `hasil` varchar(100) NOT NULL,
  `confidence` float NOT NULL,
  `deskripsi` text,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `riwayat_deteksi`
--

INSERT INTO `riwayat_deteksi` (`id`, `user_id`, `image_path`, `hasil`, `confidence`, `deskripsi`, `created_at`) VALUES
(7, 1, '/static/uploads/47e5c52a42104a7c9180fa80f9ee383d.jpg', 'Leaf Blast', 98.7704, 'Leaf Blast ditandai dengan bercak berbentuk belah ketupat dengan bagian tengah abu-abu dan tepi kecokelatan. Penyakit ini dapat menyebar cepat pada lingkungan lembap.', '2026-04-02 16:59:29'),
(8, 2, '/static/uploads/307c37f0bb704e9a993de3abb855fa78.jpg', 'Leaf Blast', 98.7704, 'Leaf Blast ditandai dengan bercak berbentuk belah ketupat dengan bagian tengah abu-abu dan tepi kecokelatan. Penyakit ini dapat menyebar cepat pada lingkungan lembap.', '2026-04-02 17:02:01'),
(9, 2, '/static/uploads/7acbe2d80468469688e87e2cb3a410e7.jpg', 'Brown Spot', 86.5484, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-04-02 17:02:47'),
(10, 2, '/static/uploads/2e42dd1846dc47fe9bd46155ffa6c069.jpg', 'Brown Spot', 90.3821, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-04-02 17:03:11'),
(19, 1, '/static/uploads/bdfb3aab034c44279adeb7af88c4ae34.jpg', 'Bacterial Leaf Blight', 81.759, 'Penyakit hawar daun bakteri ditandai dengan bercak memanjang berwarna kuning pucat hingga cokelat pada tepi daun. Pada kondisi berat, daun dapat mengering dan hasil panen menurun.', '2026-04-10 06:21:44'),
(63, 4, '/static/uploads/8a08ae0c4794481f823f0f7e66525f65.jpg', 'Brown Spot', 100, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-07 08:48:42'),
(64, 4, '/static/uploads/777085731c5c434fafd2517bfa77329e.jpg', 'Bacterial Leaf Blight', 99.4593, 'Penyakit hawar daun bakteri ditandai dengan bercak memanjang berwarna kuning pucat hingga cokelat pada tepi daun. Pada kondisi berat, daun dapat mengering dan hasil panen menurun.', '2026-05-20 11:11:16'),
(65, 4, '/static/uploads/e5fb02f8b23d4a7da409ab279427ec95.jpg', 'Brown Spot', 99.9843, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 11:12:46'),
(66, 4, '/static/uploads/3e8f4a29277747909ede009a39cbe94f.jpg', 'Leaf scald', 99.9968, 'Leaf scald ditandai dengan bercak memanjang berwarna pucat keabu-abuan yang berkembang dari ujung atau tepi daun. Pada kondisi berat, daun dapat tampak terbakar.', '2026-05-20 11:19:12'),
(67, 4, '/static/uploads/d2efdd163a9e4e30b3fba6fbfcc4bdbb.jpg', 'Leaf scald', 100, 'Leaf scald ditandai dengan bercak memanjang berwarna pucat keabu-abuan yang berkembang dari ujung atau tepi daun. Pada kondisi berat, daun dapat tampak terbakar.', '2026-05-20 11:59:25'),
(68, 4, '/static/uploads/aec940008d89450f9dbc9b220f00581a.jpg', 'Brown Spot', 99.98, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 11:59:47'),
(69, 4, '/static/uploads/82f46dfe7f304c02bea341c5da185480.jpg', 'Brown Spot', 99.98, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 12:02:26'),
(70, 4, '/static/uploads/d71738dd413849ccb7b7c99e280a2b16.jpg', 'Bacterial Leaf Blight', 99.46, 'Penyakit hawar daun bakteri ditandai dengan bercak memanjang berwarna kuning pucat hingga cokelat pada tepi daun. Pada kondisi berat, daun dapat mengering dan hasil panen menurun.', '2026-05-20 12:03:29'),
(71, 4, '/static/uploads/0066dfedcd8842279423524e180b46d8.jpg', 'Bacterial Leaf Blight', 99.46, 'Penyakit hawar daun bakteri ditandai dengan bercak memanjang berwarna kuning pucat hingga cokelat pada tepi daun. Pada kondisi berat, daun dapat mengering dan hasil panen menurun.', '2026-05-20 12:06:38'),
(72, 4, '/static/uploads/09e73c7fb41e4d0a86eecd87767bd804.jpg', 'Bacterial Leaf Blight', 99.46, 'Penyakit hawar daun bakteri ditandai dengan bercak memanjang berwarna kuning pucat hingga cokelat pada tepi daun. Pada kondisi berat, daun dapat mengering dan hasil panen menurun.', '2026-05-20 12:07:42'),
(73, 4, '/static/uploads/33d739eeb1174e85a728109c610e0246.jpg', 'Bacterial Leaf Blight', 99.46, 'Penyakit hawar daun bakteri ditandai dengan bercak memanjang berwarna kuning pucat hingga cokelat pada tepi daun. Pada kondisi berat, daun dapat mengering dan hasil panen menurun.', '2026-05-20 12:07:48'),
(74, 4, '/static/uploads/fac47057107f445ab976b081192c8780.jpg', 'Sheath Blight', 100, 'Sheath Blight menyerang pelepah daun dengan bercak oval kehijauan hingga cokelat. Penyakit ini berkembang cepat pada kondisi lembap dan tanaman yang terlalu rapat.', '2026-05-20 12:08:37'),
(75, 4, '/static/uploads/9fd3c27ce7404983980817ed0ca7d3be.jpg', 'Brown Spot', 99.98, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 12:08:51'),
(76, 4, '/static/uploads/5985be7772d34cbcb886c29825e4ed11.jpg', 'Brown Spot', 99.98, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 12:15:03'),
(77, 4, '/static/uploads/0bfb24cb5c5545f3be08c311c32d1fc5.jpg', 'Brown Spot', 99.98, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 12:15:25'),
(78, 4, '/static/uploads/4384ba0e0f1a432f9d538eb7905d51eb.jpg', 'Brown Spot', 99.98, 'Brown Spot ditandai dengan bercak cokelat kecil berbentuk oval pada daun. Serangan berat dapat mengganggu fotosintesis dan menurunkan pertumbuhan tanaman.', '2026-05-20 12:25:00'),
(79, 4, '/static/uploads/697edb5d65af47488dd93f487103b28d.jpg', 'Leaf scald', 100, 'Leaf scald ditandai dengan bercak memanjang berwarna pucat keabu-abuan yang berkembang dari ujung atau tepi daun. Pada kondisi berat, daun dapat tampak terbakar.', '2026-05-20 12:27:16'),
(80, 4, '/static/uploads/42e3408442ec4786993927aa9fd03e31.jpg', 'Leaf scald', 99.92, 'Leaf scald ditandai dengan bercak memanjang berwarna pucat keabu-abuan yang berkembang dari ujung atau tepi daun. Pada kondisi berat, daun dapat tampak terbakar.', '2026-05-20 12:29:28'),
(81, 4, '/static/uploads/8b811349c61d4b15b0480d0afa635dae.jpg', 'Bukan Padi', 100, 'Gambar yang Anda upload bukan daun padi.', '2026-05-20 12:31:38'),
(82, 4, '/static/uploads/7906f7613e3b4330ad61f98564ef391e.jpg', 'Bukan Padi', 100, 'Gambar yang Anda upload bukan daun padi.', '2026-05-20 12:31:59'),
(83, 4, '/static/uploads/62d0abc911404702991c0c0d7a2063b2.jpg', 'Bukan Padi', 100, 'Gambar yang Anda upload bukan daun padi.', '2026-05-20 12:38:09'),
(84, 4, '/static/uploads/4a07f2a170c44d228807e8a6f9490c99.jpg', 'Bukan Padi', 100, 'Gambar yang Anda upload bukan daun padi.', '2026-05-20 12:39:45');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `fullname` varchar(50) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('user','admin') NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `profile_image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fullname`, `email`, `phone`, `password`, `role`, `is_active`, `profile_image`) VALUES
(1, 'Admin', 'admin@mail.com', NULL, 'scrypt:32768:8:1$yf1Z8wjuyJxs8tck$7b6d509f086160791406c733562f52d5f88ab352102bb931c7c2d4805aff2a97ef7e9cf2003a74e7a24018cc6c3595c964946b1fdee196ebda3adc1b25297774', 'admin', 1, '/static/uploads/profile/af5f17d0c9a34859a0b81b646cbeb0aa.jpg'),
(2, 'User 1', 'user1@mail.com', NULL, 'scrypt:32768:8:1$0h9leeFoHuuhW2Pf$37ed6201737dfe1ed21c54c28a8a166182092fedd1f1264b5221bb2647405e9a0aa18d44cfdfe1d49ddab23db563a84d8d59dfdf0d55b009ed6aa2611f939ae5', 'user', 1, NULL),
(3, 'User 2', 'user2@mail.com', NULL, 'scrypt:32768:8:1$emU4ddMLms1LMiiq$0b1128cf508fac08ca786bd815baae7cbc2a4f743b66a4413354ca341b23cbc71ba017ad59641369fc76fc536351b783346ba13eaf6bd361f1ba60efce8ef86c', 'user', 0, NULL),
(4, 'lalala', 'lala@sistem.com', '085791409080', 'scrypt:32768:8:1$Fbsw73Z2gzrjKFHR$2e771aa8d5a4c5912cd50cbe367c66534c53ebd3cf9f4b5d29a4de2c9bc47f88b943fadeeccb8936d9c80d1a843dac6c0327e727e34b2d7b62442477682054b9', 'user', 1, '/static/uploads/profile/6a3ba6bba5934459838a5fef5a86fefc.png');

-- --------------------------------------------------------

--
-- Table structure for table `varietas_padi`
--

CREATE TABLE `varietas_padi` (
  `id` int NOT NULL,
  `nama` varchar(100) NOT NULL,
  `hari_penyemaian` int DEFAULT '0',
  `hari_penanaman` int NOT NULL,
  `hari_pemupukan_1` int DEFAULT NULL,
  `hari_pemupukan_2` int DEFAULT NULL,
  `hari_panen` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `varietas_padi`
--

INSERT INTO `varietas_padi` (`id`, `nama`, `hari_penyemaian`, `hari_penanaman`, `hari_pemupukan_1`, `hari_pemupukan_2`, `hari_panen`) VALUES
(1, 'inpari', 0, 15, 30, 40, 67),
(2, 'a', 0, 17, 36, 46, 70);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `detail_jadwal_pengelolaan`
--
ALTER TABLE `detail_jadwal_pengelolaan`
  ADD PRIMARY KEY (`id_deteksi`),
  ADD KEY `id_user` (`id_user`);

--
-- Indexes for table `foto_hasil_penyakit`
--
ALTER TABLE `foto_hasil_penyakit`
  ADD PRIMARY KEY (`id_foto`),
  ADD KEY `id_penyakit` (`id_penyakit`);

--
-- Indexes for table `hasil_deteksi`
--
ALTER TABLE `hasil_deteksi`
  ADD PRIMARY KEY (`id_hasil`),
  ADD KEY `id_deteksi` (`id_deteksi`),
  ADD KEY `id_penyakit` (`id_penyakit`);

--
-- Indexes for table `jadwal_tanam`
--
ALTER TABLE `jadwal_tanam`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_jadwal_user` (`user_id`),
  ADD KEY `fk_jadwal_varietas` (`varietas_id`);

--
-- Indexes for table `penanganan_penyakit`
--
ALTER TABLE `penanganan_penyakit`
  ADD PRIMARY KEY (`id_penanganan`),
  ADD KEY `id_penyakit` (`id_penyakit`);

--
-- Indexes for table `penyakit`
--
ALTER TABLE `penyakit`
  ADD PRIMARY KEY (`id_penyakit`),
  ADD UNIQUE KEY `kode_penyakit` (`kode_penyakit`),
  ADD KEY `dibuat_oleh` (`dibuat_oleh`);

--
-- Indexes for table `riwayat_deteksi`
--
ALTER TABLE `riwayat_deteksi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- Indexes for table `varietas_padi`
--
ALTER TABLE `varietas_padi`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `detail_jadwal_pengelolaan`
--
ALTER TABLE `detail_jadwal_pengelolaan`
  MODIFY `id_deteksi` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `foto_hasil_penyakit`
--
ALTER TABLE `foto_hasil_penyakit`
  MODIFY `id_foto` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hasil_deteksi`
--
ALTER TABLE `hasil_deteksi`
  MODIFY `id_hasil` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `jadwal_tanam`
--
ALTER TABLE `jadwal_tanam`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `penanganan_penyakit`
--
ALTER TABLE `penanganan_penyakit`
  MODIFY `id_penanganan` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `penyakit`
--
ALTER TABLE `penyakit`
  MODIFY `id_penyakit` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `riwayat_deteksi`
--
ALTER TABLE `riwayat_deteksi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `varietas_padi`
--
ALTER TABLE `varietas_padi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `detail_jadwal_pengelolaan`
--
ALTER TABLE `detail_jadwal_pengelolaan`
  ADD CONSTRAINT `detail_jadwal_pengelolaan_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id`);

--
-- Constraints for table `foto_hasil_penyakit`
--
ALTER TABLE `foto_hasil_penyakit`
  ADD CONSTRAINT `foto_hasil_penyakit_ibfk_1` FOREIGN KEY (`id_penyakit`) REFERENCES `penyakit` (`id_penyakit`);

--
-- Constraints for table `hasil_deteksi`
--
ALTER TABLE `hasil_deteksi`
  ADD CONSTRAINT `hasil_deteksi_ibfk_1` FOREIGN KEY (`id_deteksi`) REFERENCES `detail_jadwal_pengelolaan` (`id_deteksi`),
  ADD CONSTRAINT `hasil_deteksi_ibfk_2` FOREIGN KEY (`id_penyakit`) REFERENCES `penyakit` (`id_penyakit`);

--
-- Constraints for table `jadwal_tanam`
--
ALTER TABLE `jadwal_tanam`
  ADD CONSTRAINT `fk_jadwal_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_jadwal_varietas` FOREIGN KEY (`varietas_id`) REFERENCES `varietas_padi` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `penanganan_penyakit`
--
ALTER TABLE `penanganan_penyakit`
  ADD CONSTRAINT `penanganan_penyakit_ibfk_1` FOREIGN KEY (`id_penyakit`) REFERENCES `penyakit` (`id_penyakit`);

--
-- Constraints for table `penyakit`
--
ALTER TABLE `penyakit`
  ADD CONSTRAINT `penyakit_ibfk_1` FOREIGN KEY (`dibuat_oleh`) REFERENCES `users` (`id`);

--
-- Constraints for table `riwayat_deteksi`
--
ALTER TABLE `riwayat_deteksi`
  ADD CONSTRAINT `riwayat_deteksi_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
