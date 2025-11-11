-- Safe Insert Script for Railway System
-- This script will insert sample data only if it doesn't already exist
-- Run this with: mysql -u root -p < insert_sample_data_safe.sql

USE railway_system;

-- Insert Sample Stations (if not exists)
INSERT IGNORE INTO station (station_id, station_name, city, state) VALUES
('S001', 'Mumbai Central', 'Mumbai', 'Maharashtra'),
('S002', 'Delhi Junction', 'Delhi', 'Delhi'),
('S003', 'Bangalore City', 'Bangalore', 'Karnataka'),
('S004', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
('S005', 'Kolkata Howrah', 'Kolkata', 'West Bengal'),
('S006', 'Pune Junction', 'Pune', 'Maharashtra'),
('S007', 'Hyderabad Deccan', 'Hyderabad', 'Telangana'),
('S008', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat');

-- Insert Sample Routes (if not exists)
INSERT IGNORE INTO route (route_id, route_name) VALUES
('R001', 'Mumbai-Bangalore Express Route'),
('R002', 'Delhi-Chennai Superfast Route'),
('R003', 'Mumbai-Delhi Rajdhani Route'),
('R004', 'Bangalore-Kolkata Route');

-- Insert Route Stations (if not exists)
INSERT IGNORE INTO route_station (route_id, station_id, stop_no, arrival_time, departure_time) VALUES
-- Route R001: Mumbai to Bangalore
('R001', 'S001', 1, '00:00:00', '06:00:00'),
('R001', 'S006', 2, '08:30:00', '08:45:00'),
('R001', 'S003', 3, '18:00:00', '18:30:00'),

-- Route R002: Delhi to Chennai
('R002', 'S002', 1, '00:00:00', '07:00:00'),
('R002', 'S007', 2, '15:30:00', '16:00:00'),
('R002', 'S003', 3, '22:00:00', '22:30:00'),
('R002', 'S004', 4, '05:00:00', '05:30:00'),

-- Route R003: Mumbai to Delhi
('R003', 'S001', 1, '00:00:00', '16:00:00'),
('R003', 'S008', 2, '22:00:00', '22:30:00'),
('R003', 'S002', 3, '08:00:00', '08:30:00'),

-- Route R004: Bangalore to Kolkata
('R004', 'S003', 1, '00:00:00', '10:00:00'),
('R004', 'S007', 2, '18:00:00', '18:30:00'),
('R004', 'S005', 3, '14:00:00', '14:30:00');

-- Insert Sample Trains (if not exists)
INSERT IGNORE INTO train (train_no, train_name, type, base_fare_multiplier, route_id) VALUES
('T001', 'Shatabdi Express', 'shatabdi', 1.8, 'R001'),
('T002', 'Rajdhani Express', 'rajdhani', 2.0, 'R003'),
('T003', 'Duronto Express', 'duronto', 1.7, 'R002'),
('T004', 'Superfast Express', 'superfast', 1.4, 'R004'),
('T005', 'Passenger Train', 'passenger', 1.0, 'R001');

-- Insert Sample Classes (if not exists)
INSERT IGNORE INTO class (class_id, class_name, coach_type, no_of_coaches, c_multiplier, train_no) VALUES
-- For Shatabdi Express
('CL001', 'AC First Class', 'ac', 2, 2.5, 'T001'),
('CL002', 'AC Chair Car', 'ac', 8, 1.5, 'T001'),

-- For Rajdhani Express
('CL003', 'AC 2 Tier', 'ac', 10, 1.8, 'T002'),
('CL004', 'AC 3 Tier', 'ac', 12, 1.3, 'T002'),

-- For Duronto Express
('CL005', 'AC 2 Tier', 'ac', 8, 1.7, 'T003'),
('CL006', 'Sleeper Class', 'sleeper', 15, 1.0, 'T003'),

-- For Superfast Express
('CL007', 'AC 3 Tier', 'ac', 10, 1.3, 'T004'),
('CL008', 'Sleeper Class', 'sleeper', 18, 1.0, 'T004'),

-- For Passenger Train
('CL009', 'General', 'general', 20, 0.8, 'T005');

-- Insert Sample Berths (if not exists)
INSERT IGNORE INTO berth (berth_id, class_id, coach_no, berth_no, status) VALUES
-- AC First Class berths
('B001', 'CL001', 1, 1, 'available'),
('B002', 'CL001', 1, 2, 'available'),
('B003', 'CL001', 1, 3, 'available'),
('B004', 'CL001', 1, 4, 'available'),

-- AC Chair Car berths
('B005', 'CL002', 1, 1, 'available'),
('B006', 'CL002', 1, 2, 'available'),
('B007', 'CL002', 1, 3, 'available'),

-- Sleeper berths
('B008', 'CL006', 1, 1, 'available'),
('B009', 'CL006', 1, 2, 'available'),
('B010', 'CL006', 1, 3, 'available');

-- Insert Seat Availability for next 7 days (if not exists)
INSERT IGNORE INTO seat_availability (train_no, class_id, travel_date, available_seats) VALUES
-- For next 7 days
('T001', 'CL001', CURDATE() + INTERVAL 1 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 1 DAY, 120),
('T002', 'CL003', CURDATE() + INTERVAL 1 DAY, 80),
('T002', 'CL004', CURDATE() + INTERVAL 1 DAY, 150),
('T003', 'CL005', CURDATE() + INTERVAL 1 DAY, 70),
('T003', 'CL006', CURDATE() + INTERVAL 1 DAY, 200),

('T001', 'CL001', CURDATE() + INTERVAL 2 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 2 DAY, 120),
('T002', 'CL003', CURDATE() + INTERVAL 2 DAY, 80),
('T002', 'CL004', CURDATE() + INTERVAL 2 DAY, 150),

('T001', 'CL001', CURDATE() + INTERVAL 3 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 3 DAY, 120),

('T001', 'CL001', CURDATE() + INTERVAL 4 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 4 DAY, 120),

('T001', 'CL001', CURDATE() + INTERVAL 5 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 5 DAY, 120),

('T001', 'CL001', CURDATE() + INTERVAL 6 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 6 DAY, 120),

('T001', 'CL001', CURDATE() + INTERVAL 7 DAY, 50),
('T001', 'CL002', CURDATE() + INTERVAL 7 DAY, 120);

-- Insert Sample Schedule (if not exists)
INSERT IGNORE INTO schedule (schedule_id, train_no, start_time, end_time, running_days) VALUES
('SCH001', 'T001', '06:00:00', '18:30:00', 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday'),
('SCH002', 'T002', '16:00:00', '08:30:00', 'Monday,Wednesday,Friday,Sunday'),
('SCH003', 'T003', '07:00:00', '05:30:00', 'Tuesday,Thursday,Saturday'),
('SCH004', 'T004', '10:00:00', '14:30:00', 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday'),
('SCH005', 'T005', '06:00:00', '18:30:00', 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday');

-- Insert Sample Train Status (if not exists)
INSERT IGNORE INTO train_status (train_no, status_date, current_station, delay_minutes, status) VALUES
('T001', CURDATE(), 'S001', 0, 'on_time'),
('T002', CURDATE(), 'S008', 15, 'delayed'),
('T003', CURDATE(), 'S002', 0, 'on_time'),
('T004', CURDATE(), 'S003', 5, 'delayed');

-- Insert Connected stations (if not exists)
INSERT IGNORE INTO connected (station_id, train_no) VALUES
('S001', 'T001'),
('S006', 'T001'),
('S003', 'T001'),
('S001', 'T002'),
('S008', 'T002'),
('S002', 'T002'),
('S002', 'T003'),
('S007', 'T003'),
('S003', 'T003'),
('S004', 'T003');

-- Sample User (for testing) - Password is 'password123'
INSERT IGNORE INTO user (user_id, name, email, password, dob, gender, city, state, pin_code, role) VALUES
('U001', 'Test User', 'test@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', '1995-05-15', 'male', 'Mumbai', 'Maharashtra', '400001', 'passenger');

INSERT IGNORE INTO user_mobile (user_id, mobile_no) VALUES
('U001', '9876543210');

COMMIT;

-- Show summary
SELECT 'Data inserted successfully!' AS Status;
SELECT 'Stations:', COUNT(*) AS Count FROM station;
SELECT 'Routes:', COUNT(*) AS Count FROM route;
SELECT 'Trains:', COUNT(*) AS Count FROM train;
SELECT 'Classes:', COUNT(*) AS Count FROM class;
SELECT 'Users:', COUNT(*) AS Count FROM user;
SELECT 'Seat Availability:', COUNT(*) AS Count FROM seat_availability;
