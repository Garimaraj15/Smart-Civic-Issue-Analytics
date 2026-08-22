-- =============================================================================
-- SMART CIVIC ISSUE ANALYTICS - ENTERPRISE STAR SCHEMA & REPORTING VIEWS
-- Target Engines: MySQL 8.0+ / PostgreSQL / SQLite (ANSI Standard)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Dimension Tables
-- -----------------------------------------------------------------------------

-- Dimension: Geography / Ward
CREATE TABLE IF NOT EXISTS dim_geography (
    geography_key INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(50) NOT NULL,
    ward VARCHAR(50) NOT NULL,
    area VARCHAR(100) NOT NULL,
    avg_latitude DECIMAL(10,6),
    avg_longitude DECIMAL(10,6),
    UNIQUE KEY uq_geo (district, ward, area)
);

-- Dimension: Department & Category
CREATE TABLE IF NOT EXISTS dim_department (
    department_key INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    head_officer VARCHAR(100),
    sla_target_days INT DEFAULT 3
);

-- Dimension: Officer
CREATE TABLE IF NOT EXISTS dim_officer (
    officer_key INT AUTO_INCREMENT PRIMARY KEY,
    officer_name VARCHAR(100) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    active_status VARCHAR(20) DEFAULT 'Active'
);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_name VARCHAR(20),
    month_name VARCHAR(20),
    month_number INT,
    quarter VARCHAR(10),
    year INT,
    is_weekend TINYINT
);

-- -----------------------------------------------------------------------------
-- 2. Fact Table: Civic Complaints
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_complaints (
    complaint_key INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(30) NOT NULL UNIQUE,
    complaint_date DATE NOT NULL,
    resolution_date DATE,
    district VARCHAR(50),
    ward VARCHAR(50),
    area VARCHAR(100),
    issue_type VARCHAR(100),
    department VARCHAR(100),
    priority VARCHAR(20),
    status VARCHAR(30),
    assigned_officer VARCHAR(100),
    citizen_rating INT,
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    remarks VARCHAR(255),
    resolution_time_days INT,
    complaint_severity_score INT,
    resolution_category VARCHAR(30),
    sla_status VARCHAR(30),
    sla_breached_flag TINYINT,
    complaint_age_days INT,
    
    -- Indexes for High-Velocity Analytics
    INDEX idx_complaint_date (complaint_date),
    INDEX idx_dept_status (department, status),
    INDEX idx_sla (sla_status),
    INDEX idx_district_ward (district, ward)
);

-- -----------------------------------------------------------------------------
-- 3. Enterprise Reporting Views
-- -----------------------------------------------------------------------------

-- View 1: Executive KPI Summary View
CREATE OR REPLACE VIEW vw_executive_kpi_summary AS
SELECT
    COUNT(*) AS total_complaints,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
    ROUND(SUM(CASE WHEN status = 'Resolved' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS resolution_rate_pct,
    ROUND(AVG(CASE WHEN status = 'Resolved' THEN resolution_time_days END), 2) AS avg_turnaround_days,
    ROUND(SUM(CASE WHEN sla_status = 'Within SLA' THEN 1.0 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN sla_status IN ('Within SLA', 'SLA Breached') THEN 1 ELSE 0 END), 0) * 100, 2) AS sla_compliance_pct,
    ROUND(AVG(citizen_rating), 2) AS avg_citizen_satisfaction
FROM fact_complaints;

-- View 2: Department Operational Performance View
CREATE OR REPLACE VIEW vw_department_performance AS
SELECT
    department,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
    ROUND(AVG(resolution_time_days), 2) AS avg_resolution_days,
    SUM(CASE WHEN sla_status = 'SLA Breached' THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(AVG(citizen_rating), 2) AS avg_rating
FROM fact_complaints
GROUP BY department;

-- View 3: Ward Risk Matrix View
CREATE OR REPLACE VIEW vw_ward_risk_matrix AS
SELECT
    district,
    ward,
    COUNT(*) AS incident_volume,
    SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) AS high_priority_count,
    ROUND(AVG(citizen_rating), 2) AS avg_rating,
    ROUND(SUM(CASE WHEN sla_status = 'SLA Breached' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS breach_rate_pct
FROM fact_complaints
GROUP BY district, ward;
