-- Optional: the app creates these automatically. Use this file only if you want to
-- import the tables yourself in phpMyAdmin (Import tab).
CREATE DATABASE IF NOT EXISTS skillgap_db;
USE skillgap_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    overall_percent INT NOT NULL,
    taken_on DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS skill_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    result_id INT NOT NULL,
    skill VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    total INT NOT NULL,
    level_name VARCHAR(20) NOT NULL,
    required_name VARCHAR(20) NOT NULL,
    gap INT NOT NULL,
    priority VARCHAR(20) NOT NULL,
    FOREIGN KEY (result_id) REFERENCES results(id)
);
