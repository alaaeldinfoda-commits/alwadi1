-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 02, 2025 at 01:51 AM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.4.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `enterprise_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `assigned_engineers`
--

CREATE TABLE `assigned_engineers` (
  `id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `audit_log`
--

CREATE TABLE `audit_log` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `object_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `object_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `details` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `audit_log`
--

INSERT INTO `audit_log` (`id`, `user_id`, `action`, `object_type`, `object_id`, `details`, `timestamp`) VALUES
(1, 2, 'login', 'user', '2', 'User logged in', '2025-11-30 01:06:30'),


-- --------------------------------------------------------

--
-- Table structure for table `contractors`
--

CREATE TABLE `contractors` (
  `contractor_id` int(11) NOT NULL,
  `contractor_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `contractors`
--

INSERT INTO `contractors` (`contractor_id`, `contractor_name`, `phone`) VALUES
(1, 'كريم', '0101112233'),
(2, 'ابو ياسين', '0105557866'),
(3, 'عمر احمد', '0103334499'),
(4, 'صبرى', '0101112233'),
(7, 'مقاول الشرق', '01000111222');

-- --------------------------------------------------------

--
-- Table structure for table `gps_logs`
--

CREATE TABLE `gps_logs` (
  `id` int(11) NOT NULL,
  `report_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `lat` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lon` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `permissions`
--

CREATE TABLE `permissions` (
  `id` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `report_id` int(11) NOT NULL,
  `site_id` int(11) DEFAULT NULL,
  `contractor_id` int(11) DEFAULT NULL,
  `engineer_id` int(11) DEFAULT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gps_lat` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gps_lon` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_created` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `reports`
--

INSERT INTO `reports` (`report_id`, `site_id`, `contractor_id`, `engineer_id`, `title`, `description`, `gps_lat`, `gps_lon`, `date_created`) VALUES
(1, 1, 1, 21, 'نجارة الأسقف', 'بدء تنفيذ أعمال النجارة للأسقف في المنطقة A.', '30.10', '31.22', '2025-11-30 00:57:40'),
(2, 2, 2, 22, 'نجارة الأسقف', 'بدء تنفيذ أعمال النجارة للأسقف في المنطقة A.', '30.10', '31.22', '2025-11-30 00:57:40'),
(3, 3, 2, 23, 'نجارة الأسقف', 'بدء تنفيذ أعمال النجارة للأسقف في المنطقة A.', '30.10', '31.22', '2025-11-30 00:57:40'),
(4, 4, 3, 24, 'توريد حديد', 'تم توريد الحديد للموقع وتم استلامه بعد الفحص.', '30.10', '31.22', '2025-11-30 00:57:40'),
(5, 1, 4, 21, 'توريد حديد', 'تم توريد الحديد للموقع وتم استلامه بعد الفحص.', '30.10', '31.22', '2025-11-30 00:57:40'),
(10, 1, 3, 21, 'dasd', 'dsadsada', '29.9946', '31.1678', '2025-12-01 23:01:49'),
(11, 3, 1, 23, 'ereee', 'eerdcxvgf', '29.9946', '31.1678', '2025-12-01 23:12:52'),
(12, 1, 3, 16, '32423', '3242', '29.9946', '31.1678', '2025-12-02 00:41:25'),
(13, 3, 2, 16, 'dsadas', 'dsadas', '29.9946', '31.1678', '2025-12-02 00:41:58');

-- --------------------------------------------------------

--
-- Table structure for table `report_images`
--

CREATE TABLE `report_images` (
  `image_id` int(11) NOT NULL,
  `report_id` int(11) DEFAULT NULL,
  `image_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `report_permissions`
--

CREATE TABLE `report_permissions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `site_id` int(11) DEFAULT NULL,
  `can_view` tinyint(4) DEFAULT 0,
  `can_add` tinyint(4) DEFAULT 0,
  `can_edit` tinyint(4) DEFAULT 0,
  `can_delete` tinyint(4) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `report_permissions`
--

INSERT INTO `report_permissions` (`id`, `user_id`, `site_id`, `can_view`, `can_add`, `can_edit`, `can_delete`) VALUES
(21, 1, 1, 0, 0, 0, 0),
(26, 21, 1, 0, 1, 0, 0),
(28, 23, 3, 0, 1, 0, 0),
(29, 24, 4, 1, 1, 0, 0),
(34, 19, 1, 1, 0, 0, 0),
(35, 19, 2, 1, 0, 0, 0),
(36, 25, 1, 1, 0, 0, 0),
(37, 22, 1, 0, 0, 0, 0),
(38, 22, 2, 0, 0, 0, 0),
(39, 20, 1, 1, 0, 0, 0),
(40, 20, 2, 1, 0, 0, 0),
(41, 20, 3, 1, 0, 0, 0),
(42, 20, 4, 1, 0, 0, 0),
(43, 25, 2, 0, 0, 0, 0),
(44, 26, 1, 1, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`role_id`, `role_name`) VALUES
(1, 'Admin'),
(3, 'Contractor Manager'),
(2, 'Engineer'),
(10, 'Manager'),
(27, 'view_only aa'),
(4, 'Viewer');

-- --------------------------------------------------------

--
-- Table structure for table `roles_permissions`
--

CREATE TABLE `roles_permissions` (
  `id` int(11) NOT NULL,
  `role_id` int(11) DEFAULT NULL,
  `perm_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `roles_permissions`
--

INSERT INTO `roles_permissions` (`id`, `role_id`, `perm_name`) VALUES
(1, 1, 'manage_users'),
(2, 1, 'manage_sites'),
(3, 3, 'manage_sites'),
(5, 1, 'manage_contractors'),
(6, 3, 'manage_contractors'),
(8, 1, 'manage_reports'),
(9, 2, 'manage_reports'),
(10, 10, 'manage_reports');

-- --------------------------------------------------------

--
-- Table structure for table `sites`
--

CREATE TABLE `sites` (
  `site_id` int(11) NOT NULL,
  `site_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `site_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `latitude` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `longitude` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contractor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sites`
--

INSERT INTO `sites` (`site_id`, `site_code`, `site_name`, `address`, `latitude`, `longitude`, `contractor_id`) VALUES
(1, 'SIT-1012', 'انتماء', 'التجمع', '30.0444', '31.2357', 1),
(2, 'SIT-1001', 'العلمين', 'العلمين', '', '', NULL),
(3, 'SIT-001', 'كوبرى القبة', 'التجمع', '30.0444', '31.2357', 1),
(4, 'SIT-002', 'بورسعيد', 'بورسعيد', '29.98', '31.2', 1),
(6, 'SIT-1002', 'موقع العاصمة الجديدة 2', 'العاصمة', '30.2', '31.2', 1),
(7, 'SIT-1003', 'موقع التجمع الخامس', 'القاهرة', '30.5', '31.3', NULL),
(8, 'SIT-1004', 'موقع 6 أكتوبر', 'الجيزة', '29.9', '31.0', 2),
(10, 'SIT-1006', 'موقع زايد الجديدة', 'الجيزة', '30.0', '30.9', NULL),
(11, 'SIT-1007', 'موقع بنها', 'القليوبية', '30.5', '31.2', 4),
(16, '3123', '31231', '3123', '31231', '3123', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fullname` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`, `fullname`, `role_id`) VALUES
(1, 'admin', 'scrypt:32768:8:1$CN3RKEcOZpAQB87k$d9056517549d2ed6d718d89e0a0779b1caeef44cc5f2a43e105c10b5fc67a8bc07c659c7b3bdddbcae4bf7b7ce6a1737ee81189d449e7eca6f3d819458f9f75a', 'System Administrator', 1),
(16, 'alaa', 'scrypt:32768:8:1$aw1AZAzihgpyYyi5$c12ced34c4f500f7d3d4401fdbb2f69283bd308ee01a4b79c6d4b456a80a27ad8c557402abca7310f06bf6ce9417006f95309d66f553069aa00aceeec7c161d7', 'alaa eldin', 1),
(18, 'manager', 'scrypt:32768:8:1$6ZMQLRryvouQDVvB$f0a679a03aa3e44deb87ae5dc1b8af490c697bec240ad0ccf7fe7b574a56863ffad2c7f73d73af0ec8c1db05044e1377be42ab9ebf6c9e96100fe092e92c9bd2', 'ashraf mohamed', 10),
(19, 'emam', 'scrypt:32768:8:1$eB4vUxfpQEwtUWg9$d1d3305b563b7b31965d597a5b06df04ace03869b064e01a2bc6bfec6e465151b4495ae487a714e968ebd540452a29ad4c34d2676d9c8d6565cd71e09e0da5d0', 'emam selim', 10),
(20, 'ibrahim', 'scrypt:32768:8:1$zT1Dxdae5ms9IAk3$9f7fb9393d07fe93c03600d52dd1eaeececc1580e06332e268ab68b8ce061110d50964198e8d3f48ecff94e76b65ac537c13ae86aa4bf97614fbbefd9ee5d347', 'ibrahim', 2),
(21, 'amir', 'scrypt:32768:8:1$y7XH0dowl1MHa11T$4534c2bb59c8e16ee3fcef37918e13210ad4cdcb9db855e6b950730b6449017fb306c47544c0e09de647ea9c7b44673f54956660f8ca7cf962ec3cab2864013e', 'amir', 2),
(22, 'nabil', 'scrypt:32768:8:1$ZC2JrWkOpLjosFYn$18cb995e793448fd91d2b8816490651260a9c5087a7a77fcaf9759e33dc23710b0cf6fbc990a3f752e33dab527a6fae21fed0609f93a4c2c641cfbbbaf5067dc', 'nabil', 2),
(23, 'mahmoud', 'scrypt:32768:8:1$8NzDl1lWIci1mSwi$0b305400e1aeba14d0cabc15e75463d7f760cae3179ef2a98da5407c928ced78745a97561a53eb7a0ec4d94cc139524a2dc4eed6468b230ae2a7ac5e56cc2445', 'mahmoud', 2),
(24, 'hossam', 'scrypt:32768:8:1$xklql0ojp3sSs9vr$46088c8621df609d71d4b58b846c669ae717a208b065b21c46073423d95d24409e2eb1db3301bb994b6cddba12c6fe03a9445030fb5e5ab8536018e3253577b1', 'hossam', 2),
(25, 'mohamed rabie', 'scrypt:32768:8:1$v6Vb6CH6Ot0MOB31$c84b368b9c5f5c897cde0af8e79e38190eb13f5437e3512778a0d6908dc0b6dfc697c07ddc7adf8dbdde927188b28020a14baf53edceb119a1a99ed4b12a8b63', 'mohamed rabie', 3),
(26, 'magda', 'scrypt:32768:8:1$6aP2b6ybt0jXj8n1$aa9ccce2d17379aa6e0840be5b2009b9ce9ce9ab29a444a10cc3308efe9f8ce539b67182c5c450b87e7fc79c8f0bf6b3a21642b2648cd3f241f3b36283a3d69b', 'magda', 4);

-- --------------------------------------------------------

--
-- Table structure for table `user_roles`
--

CREATE TABLE `user_roles` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `user_roles`
--

INSERT INTO `user_roles` (`user_id`, `role_id`) VALUES
(25, 3),
(26, 4);

-- --------------------------------------------------------

--
-- Table structure for table `user_sites`
--

CREATE TABLE `user_sites` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `site_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `user_sites`
--

INSERT INTO `user_sites` (`id`, `user_id`, `site_id`) VALUES
(33, 19, 1),
(34, 19, 2),
(29, 20, 1),
(30, 20, 2),
(31, 20, 3),
(32, 20, 4),
(24, 21, 1),
(27, 22, 2),
(25, 24, 4),
(35, 25, 2),
(36, 26, 1);

-- --------------------------------------------------------

--
-- Table structure for table `workers`
--

CREATE TABLE `workers` (
  `worker_id` int(11) NOT NULL,
  `report_id` int(11) DEFAULT NULL,
  `worker_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `job_title` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `task_details` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `workers`
--

INSERT INTO `workers` (`worker_id`, `report_id`, `worker_name`, `job_title`, `task_details`, `notes`) VALUES
(1, 1, 'عامل 1', 'نجار', 'عمل الشدات الخشبية', NULL),
(2, 1, 'عامل 2', 'حداد', 'تجهيز حديد التسليح', NULL),
(3, 2, 'عامل 1', 'نجار', 'عمل الشدات الخشبية', NULL),
(4, 2, 'عامل 2', 'حداد', 'تجهيز حديد التسليح', NULL),
(5, 3, 'عامل 1', 'نجار', 'عمل الشدات الخشبية', NULL),
(6, 3, 'عامل 2', 'حداد', 'تجهيز حديد التسليح', NULL),
(7, 4, 'عامل 1', 'نجار', 'عمل الشدات الخشبية', NULL),
(8, 4, 'عامل 2', 'حداد', 'تجهيز حديد التسليح', NULL),
(9, 5, 'عامل 1', 'نجار', 'عمل الشدات الخشبية', NULL),
(10, 5, 'عامل 2', 'حداد', 'تجهيز حديد التسليح', NULL),
(11, 5, 'محمد على', 'صنايعى', 'تركيب كاميرا', ''),
(16, 10, 'aaa', 'صنايعى', 'تركيب كاميرا', ''),
(17, 10, 'aaaa', 'صنايعى', 'تركيب كاميرا', ''),
(18, 11, 'sssds', 'صنايعى', 'تركيب كاميرا', ''),
(19, 11, 'dcvfdf', 'صنايعى', 'تركيب كاميرا', ''),
(20, 11, 'ddd', 'صنايعى', 'تركيب كاميرا', ''),
(21, 12, '4234', '3244', '4234', ''),
(22, 13, 'dsad', 'dsadas', 'dsa', ''),
(23, 13, 'dsadsa', 'dsadsa', 'dasdas', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `assigned_engineers`
--
ALTER TABLE `assigned_engineers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `site_id` (`site_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `audit_log`
--
ALTER TABLE `audit_log`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `contractors`
--
ALTER TABLE `contractors`
  ADD PRIMARY KEY (`contractor_id`);

--
-- Indexes for table `gps_logs`
--
ALTER TABLE `gps_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_gps_report_id` (`report_id`);

--
-- Indexes for table `permissions`
--
ALTER TABLE `permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`report_id`),
  ADD KEY `contractor_id` (`contractor_id`),
  ADD KEY `idx_reports_site_id` (`site_id`),
  ADD KEY `idx_reports_engineer_id` (`engineer_id`);

--
-- Indexes for table `report_images`
--
ALTER TABLE `report_images`
  ADD PRIMARY KEY (`image_id`),
  ADD KEY `idx_images_report_id` (`report_id`);

--
-- Indexes for table `report_permissions`
--
ALTER TABLE `report_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_perm` (`user_id`,`site_id`),
  ADD KEY `site_id` (`site_id`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `role_name` (`role_name`);

--
-- Indexes for table `roles_permissions`
--
ALTER TABLE `roles_permissions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `role_id` (`role_id`);

--
-- Indexes for table `sites`
--
ALTER TABLE `sites`
  ADD PRIMARY KEY (`site_id`),
  ADD KEY `contractor_id` (`contractor_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `role_id` (`role_id`);

--
-- Indexes for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD PRIMARY KEY (`user_id`,`role_id`),
  ADD KEY `role_id` (`role_id`);

--
-- Indexes for table `user_sites`
--
ALTER TABLE `user_sites`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_user_site` (`user_id`,`site_id`),
  ADD KEY `site_id` (`site_id`);

--
-- Indexes for table `workers`
--
ALTER TABLE `workers`
  ADD PRIMARY KEY (`worker_id`),
  ADD KEY `report_id` (`report_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `assigned_engineers`
--
ALTER TABLE `assigned_engineers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `audit_log`
--
ALTER TABLE `audit_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=147;

--
-- AUTO_INCREMENT for table `contractors`
--
ALTER TABLE `contractors`
  MODIFY `contractor_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `gps_logs`
--
ALTER TABLE `gps_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `permissions`
--
ALTER TABLE `permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `report_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `report_images`
--
ALTER TABLE `report_images`
  MODIFY `image_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `report_permissions`
--
ALTER TABLE `report_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `roles_permissions`
--
ALTER TABLE `roles_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `sites`
--
ALTER TABLE `sites`
  MODIFY `site_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `user_sites`
--
ALTER TABLE `user_sites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `workers`
--
ALTER TABLE `workers`
  MODIFY `worker_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `assigned_engineers`
--
ALTER TABLE `assigned_engineers`
  ADD CONSTRAINT `assigned_engineers_ibfk_1` FOREIGN KEY (`site_id`) REFERENCES `sites` (`site_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `assigned_engineers_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`site_id`) REFERENCES `sites` (`site_id`),
  ADD CONSTRAINT `reports_ibfk_2` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`contractor_id`),
  ADD CONSTRAINT `reports_ibfk_3` FOREIGN KEY (`engineer_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `report_images`
--
ALTER TABLE `report_images`
  ADD CONSTRAINT `report_images_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`report_id`);

--
-- Constraints for table `report_permissions`
--
ALTER TABLE `report_permissions`
  ADD CONSTRAINT `report_permissions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `report_permissions_ibfk_2` FOREIGN KEY (`site_id`) REFERENCES `sites` (`site_id`);

--
-- Constraints for table `roles_permissions`
--
ALTER TABLE `roles_permissions`
  ADD CONSTRAINT `roles_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);

--
-- Constraints for table `sites`
--
ALTER TABLE `sites`
  ADD CONSTRAINT `sites_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`contractor_id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);

--
-- Constraints for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_sites`
--
ALTER TABLE `user_sites`
  ADD CONSTRAINT `user_sites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `user_sites_ibfk_2` FOREIGN KEY (`site_id`) REFERENCES `sites` (`site_id`);

--
-- Constraints for table `workers`
--
ALTER TABLE `workers`
  ADD CONSTRAINT `workers_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`report_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
