
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE IF NOT EXISTS roles (
  role_id INT AUTO_INCREMENT PRIMARY KEY,
  role_name VARCHAR(50) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  fullname VARCHAR(150),
  role_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sites (
  site_id INT AUTO_INCREMENT PRIMARY KEY,
  site_code VARCHAR(50) UNIQUE,
  site_name VARCHAR(150) NOT NULL,
  address VARCHAR(255),
  latitude DOUBLE,
  longitude DOUBLE,
  contractor_id INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS contractors (
  contractor_id INT AUTO_INCREMENT PRIMARY KEY,
  contractor_name VARCHAR(150) NOT NULL,
  phone VARCHAR(30)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS reports (
  report_id INT AUTO_INCREMENT PRIMARY KEY,
  site_id INT NOT NULL,
  contractor_id INT,
  engineer_id INT NOT NULL,
  title VARCHAR(255),
  description TEXT,
  date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  gps_lat DOUBLE,
  gps_lon DOUBLE,
  FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE,
  FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id) ON DELETE SET NULL,
  FOREIGN KEY (engineer_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workers (
  worker_id INT AUTO_INCREMENT PRIMARY KEY,
  report_id INT,
  worker_name VARCHAR(150),
  job_title VARCHAR(150),
  task_details VARCHAR(255),
  notes TEXT,
  FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS report_images (
  image_id INT AUTO_INCREMENT PRIMARY KEY,
  report_id INT,
  image_path VARCHAR(255),
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS gps_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  report_id INT,
  user_id INT,
  lat DOUBLE,
  lon DOUBLE,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- permissions per role table
CREATE TABLE IF NOT EXISTS roles_permissions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  role_id INT NOT NULL,
  permission VARCHAR(100) NOT NULL,
  FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
  UNIQUE KEY(role_id, permission)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- per-user per-site permissions (as before)
CREATE TABLE IF NOT EXISTS user_sites (
  user_id INT NOT NULL,
  site_id INT NOT NULL,
  PRIMARY KEY(user_id, site_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS report_permissions (
  user_id INT NOT NULL,
  site_id INT NOT NULL,
  can_view TINYINT(1) DEFAULT 0,
  can_add TINYINT(1) DEFAULT 0,
  can_edit TINYINT(1) DEFAULT 0,
  can_delete TINYINT(1) DEFAULT 0,
  PRIMARY KEY(user_id, site_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS audit_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  action VARCHAR(200),
  object_type VARCHAR(50),
  object_id VARCHAR(100),
  details TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS=1;
