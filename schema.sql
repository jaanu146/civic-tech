-- Database Schema for Smart Civic Grievance Management System

-- Departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'officer', 'admin')),
    department_id INTEGER REFERENCES departments(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complaints table
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    description TEXT NOT NULL,
    image_path VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    department_id INTEGER REFERENCES departments(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP,
    escalation_level INTEGER DEFAULT 1
);

-- Upvotes table
CREATE TABLE upvotes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    complaint_id INTEGER REFERENCES complaints(id) NOT NULL,
    UNIQUE(user_id, complaint_id)
);

-- Updates table (for status updates by officers)
CREATE TABLE updates (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id) NOT NULL,
    officer_id INTEGER REFERENCES users(id) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_progress', 'resolved')),
    remarks TEXT,
    image_path VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Escalations table
CREATE TABLE escalations (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id) NOT NULL,
    from_level INTEGER NOT NULL,
    to_level INTEGER NOT NULL,
    escalated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default departments
INSERT INTO departments (name) VALUES ('PWD'), ('Municipality'), ('Water Department'), ('Electricity');