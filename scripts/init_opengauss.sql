-- OpenGauss Database Initialization Script
-- Connect to openGauss as admin user first, then run this script

-- Create database
CREATE DATABASE student_course_db WITH ENCODING 'UTF8' TEMPLATE template0;

-- Create user for application
CREATE USER app_user WITH PASSWORD 'App123456';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE student_course_db TO app_user;

-- Connect to the database
\c student_course_db;

-- Grant schema access
GRANT ALL ON SCHEMA public TO app_user;
