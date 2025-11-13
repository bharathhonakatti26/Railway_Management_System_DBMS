USE railway_system;

-- ========================================
-- INSERT STATIONS (5 stations)
-- ========================================
INSERT INTO station VALUES
('S001', 'Mumbai Central', 'Mumbai', 'Maharashtra'),
('S002', 'Delhi Junction', 'Delhi', 'Delhi'),
('S003', 'Bangalore City', 'Bangalore', 'Karnataka'),
('S004', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
('S005', 'Kolkata Howrah', 'Kolkata', 'West Bengal');

-- ========================================
-- INSERT ROUTES
-- ========================================
INSERT INTO route VALUES
('R001', 'Mumbai-Delhi Route'),
('R002', 'Mumbai-Bangalore Route'),
('R003', 'Delhi-Kolkata Route'),
('R004', 'Bangalore-Chennai Route'),
('R005', 'Chennai-Kolkata Route'),
('R006', 'Mumbai-Chennai Route'),
('R007', 'Delhi-Bangalore Route');

-- ========================================
-- INSERT ROUTE_STATION (Station stops for each route)
-- ========================================
-- Route R001: Mumbai -> Delhi
INSERT INTO route_station VALUES
('R001', 'S001', 1, '00:00:00', '06:00:00'),
('R001', 'S002', 2, '22:00:00', '22:30:00');

-- Route R002: Mumbai -> Bangalore
INSERT INTO route_station VALUES
('R002', 'S001', 1, '00:00:00', '08:00:00'),
('R002', 'S003', 2, '22:00:00', '22:30:00');

-- Route R003: Delhi -> Kolkata
INSERT INTO route_station VALUES
('R003', 'S002', 1, '00:00:00', '10:00:00'),
('R003', 'S005', 2, '20:00:00', '20:30:00');

-- Route R004: Bangalore -> Chennai
INSERT INTO route_station VALUES
('R004', 'S003', 1, '00:00:00', '07:00:00'),
('R004', 'S004', 2, '13:00:00', '13:30:00');

-- Route R005: Chennai -> Kolkata
INSERT INTO route_station VALUES
('R005', 'S004', 1, '00:00:00', '09:00:00'),
('R005', 'S005', 2, '21:00:00', '21:30:00');

-- Route R006: Mumbai -> Chennai
INSERT INTO route_station VALUES
('R006', 'S001', 1, '00:00:00', '11:00:00'),
('R006', 'S004', 2, '23:00:00', '23:30:00');

-- Route R007: Delhi -> Bangalore
INSERT INTO route_station VALUES
('R007', 'S002', 1, '00:00:00', '12:00:00'),
('R007', 'S003', 2, '20:00:00', '20:30:00');

-- ========================================
-- INSERT TRAINS (Multiple trains between stations)
-- ========================================
INSERT INTO train VALUES
('T001', 'Rajdhani Express', 'rajdhani', 1.80, 'R001'),
('T002', 'Mumbai Delhi Superfast', 'superfast', 1.50, 'R001'),
('T003', 'Udyan Express', 'express', 1.20, 'R002'),
('T004', 'Bangalore Express', 'express', 1.20, 'R002'),
('T005', 'Rajdhani Express', 'rajdhani', 1.80, 'R003'),
('T006', 'Poorva Express', 'express', 1.20, 'R003'),
('T007', 'Shatabdi Express', 'shatabdi', 1.70, 'R004'),
('T008', 'Chennai Mail', 'passenger', 1.00, 'R004'),
('T009', 'Coromandel Express', 'superfast', 1.50, 'R005'),
('T010', 'Howrah Mail', 'express', 1.20, 'R005'),
('T011', 'Chennai Express', 'superfast', 1.50, 'R006'),
('T012', 'Mumbai Chennai Mail', 'passenger', 1.00, 'R006'),
('T013', 'Karnataka Express', 'superfast', 1.50, 'R007'),
('T014', 'Bangalore Rajdhani', 'rajdhani', 1.80, 'R007');

-- ========================================
-- INSERT SCHEDULES
-- ========================================
INSERT INTO schedule VALUES
('SCH001', 'T001', '06:00:00', '22:00:00', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'),
('SCH002', 'T002', '08:00:00', '23:30:00', 'Mon,Wed,Fri,Sun'),
('SCH003', 'T003', '08:00:00', '22:00:00', 'Tue,Thu,Sat'),
('SCH004', 'T004', '09:00:00', '23:00:00', 'Mon,Wed,Fri'),
('SCH005', 'T005', '10:00:00', '20:00:00', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'),
('SCH006', 'T006', '11:00:00', '21:30:00', 'Tue,Thu,Sat'),
('SCH007', 'T007', '07:00:00', '13:00:00', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'),
('SCH008', 'T008', '08:00:00', '14:00:00', 'Mon,Wed,Fri,Sun'),
('SCH009', 'T009', '09:00:00', '21:00:00', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'),
('SCH010', 'T010', '10:00:00', '22:00:00', 'Tue,Thu,Sat'),
('SCH011', 'T011', '11:00:00', '23:00:00', 'Mon,Wed,Fri,Sun'),
('SCH012', 'T012', '12:00:00', '00:00:00', 'Tue,Thu,Sat'),
('SCH013', 'T013', '12:00:00', '20:00:00', 'Mon,Wed,Fri,Sun'),
('SCH014', 'T014', '13:00:00', '21:00:00', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun');

-- ========================================
-- INSERT CLASSES (Different classes for each train)
-- ========================================
-- Train T001 - Rajdhani Express
INSERT INTO class VALUES
('C001', '1AC', 'ac', 2, 3.00, 'T001'),
('C002', '2AC', 'ac', 4, 2.00, 'T001'),
('C003', '3AC', 'ac', 8, 1.50, 'T001');

-- Train T002 - Mumbai Delhi Superfast
INSERT INTO class VALUES
('C004', '2AC', 'ac', 3, 2.00, 'T002'),
('C005', '3AC', 'ac', 6, 1.50, 'T002'),
('C006', 'Sleeper', 'sleeper', 10, 1.00, 'T002');

-- Train T003 - Udyan Express
INSERT INTO class VALUES
('C007', '3AC', 'ac', 4, 1.50, 'T003'),
('C008', 'Sleeper', 'sleeper', 12, 1.00, 'T003');

-- Train T004 - Bangalore Express
INSERT INTO class VALUES
('C009', '2AC', 'ac', 3, 2.00, 'T004'),
('C010', 'Sleeper', 'sleeper', 10, 1.00, 'T004');

-- Train T005 - Rajdhani Express
INSERT INTO class VALUES
('C011', '1AC', 'ac', 2, 3.00, 'T005'),
('C012', '2AC', 'ac', 4, 2.00, 'T005'),
('C013', '3AC', 'ac', 8, 1.50, 'T005');

-- Train T006 - Poorva Express
INSERT INTO class VALUES
('C014', 'Sleeper', 'sleeper', 14, 1.00, 'T006'),
('C015', 'General', 'general', 8, 0.80, 'T006');

-- Train T007 - Shatabdi Express
INSERT INTO class VALUES
('C016', 'AC Chair', 'ac', 10, 1.80, 'T007'),
('C017', 'Executive Chair', 'ac', 4, 2.50, 'T007');

-- Train T008 - Chennai Mail
INSERT INTO class VALUES
('C018', 'Sleeper', 'sleeper', 12, 1.00, 'T008'),
('C019', 'General', 'general', 10, 0.80, 'T008');

-- Train T009 - Coromandel Express
INSERT INTO class VALUES
('C020', '2AC', 'ac', 4, 2.00, 'T009'),
('C021', '3AC', 'ac', 7, 1.50, 'T009'),
('C022', 'Sleeper', 'sleeper', 12, 1.00, 'T009');

-- Train T010 - Howrah Mail
INSERT INTO class VALUES
('C023', '3AC', 'ac', 5, 1.50, 'T010'),
('C024', 'Sleeper', 'sleeper', 14, 1.00, 'T010');

-- Train T011 - Chennai Express
INSERT INTO class VALUES
('C025', '2AC', 'ac', 4, 2.00, 'T011'),
('C026', '3AC', 'ac', 8, 1.50, 'T011'),
('C027', 'Sleeper', 'sleeper', 10, 1.00, 'T011');

-- Train T012 - Mumbai Chennai Mail
INSERT INTO class VALUES
('C028', 'Sleeper', 'sleeper', 16, 1.00, 'T012'),
('C029', 'General', 'general', 12, 0.80, 'T012');

-- Train T013 - Karnataka Express
INSERT INTO class VALUES
('C030', '2AC', 'ac', 3, 2.00, 'T013'),
('C031', '3AC', 'ac', 6, 1.50, 'T013'),
('C032', 'Sleeper', 'sleeper', 11, 1.00, 'T013');

-- Train T014 - Bangalore Rajdhani
INSERT INTO class VALUES
('C033', '1AC', 'ac', 2, 3.00, 'T014'),
('C034', '2AC', 'ac', 4, 2.00, 'T014'),
('C035', '3AC', 'ac', 7, 1.50, 'T014');

-- ========================================
-- INSERT BERTHS (Sample berths for each class)
-- ========================================
-- Class C001 (1AC) - 2 coaches, 18 berths per coach
INSERT INTO berth VALUES
('B001', 'C001', 1, 1, 'available'),
('B002', 'C001', 1, 2, 'available'),
('B003', 'C001', 1, 3, 'available'),
('B004', 'C001', 1, 4, 'available'),
('B005', 'C001', 2, 1, 'available'),
('B006', 'C001', 2, 2, 'available');

-- Class C002 (2AC) - 4 coaches, 54 berths per coach
INSERT INTO berth VALUES
('B007', 'C002', 1, 1, 'available'),
('B008', 'C002', 1, 2, 'available'),
('B009', 'C002', 2, 1, 'available'),
('B010', 'C002', 2, 2, 'available');

-- Class C006 (Sleeper) - 10 coaches, 72 berths per coach
INSERT INTO berth VALUES
('B011', 'C006', 1, 1, 'available'),
('B012', 'C006', 1, 2, 'available'),
('B013', 'C006', 2, 1, 'available'),
('B014', 'C006', 2, 2, 'available');

-- ========================================
-- INSERT SEAT AVAILABILITY (Next 30 days)
-- ========================================
-- Train T001 classes for next 7 days
INSERT INTO seat_availability VALUES
('T001', 'C001', '2025-11-14', 36),
('T001', 'C001', '2025-11-15', 36),
('T001', 'C001', '2025-11-16', 36),
('T001', 'C002', '2025-11-14', 216),
('T001', 'C002', '2025-11-15', 216),
('T001', 'C002', '2025-11-16', 216),
('T001', 'C003', '2025-11-14', 432),
('T001', 'C003', '2025-11-15', 432),
('T001', 'C003', '2025-11-16', 432);

-- Train T002 classes
INSERT INTO seat_availability VALUES
('T002', 'C004', '2025-11-14', 162),
('T002', 'C004', '2025-11-15', 162),
('T002', 'C005', '2025-11-14', 324),
('T002', 'C005', '2025-11-15', 324),
('T002', 'C006', '2025-11-14', 720),
('T002', 'C006', '2025-11-15', 720);

-- Train T003 classes
INSERT INTO seat_availability VALUES
('T003', 'C007', '2025-11-14', 216),
('T003', 'C007', '2025-11-15', 216),
('T003', 'C008', '2025-11-14', 864),
('T003', 'C008', '2025-11-15', 864);

-- Train T004 classes
INSERT INTO seat_availability VALUES
('T004', 'C009', '2025-11-14', 162),
('T004', 'C009', '2025-11-15', 162),
('T004', 'C010', '2025-11-14', 720),
('T004', 'C010', '2025-11-15', 720);

-- Train T005 classes
INSERT INTO seat_availability VALUES
('T005', 'C011', '2025-11-14', 36),
('T005', 'C011', '2025-11-15', 36),
('T005', 'C012', '2025-11-14', 216),
('T005', 'C012', '2025-11-15', 216),
('T005', 'C013', '2025-11-14', 432),
('T005', 'C013', '2025-11-15', 432);

-- Train T007 classes
INSERT INTO seat_availability VALUES
('T007', 'C016', '2025-11-14', 500),
('T007', 'C016', '2025-11-15', 500),
('T007', 'C017', '2025-11-14', 200),
('T007', 'C017', '2025-11-15', 200);

-- Train T009 classes
INSERT INTO seat_availability VALUES
('T009', 'C020', '2025-11-14', 216),
('T009', 'C020', '2025-11-15', 216),
('T009', 'C021', '2025-11-14', 378),
('T009', 'C021', '2025-11-15', 378),
('T009', 'C022', '2025-11-14', 864),
('T009', 'C022', '2025-11-15', 864);

-- Train T011 classes
INSERT INTO seat_availability VALUES
('T011', 'C025', '2025-11-14', 216),
('T011', 'C025', '2025-11-15', 216),
('T011', 'C026', '2025-11-14', 432),
('T011', 'C026', '2025-11-15', 432),
('T011', 'C027', '2025-11-14', 720),
('T011', 'C027', '2025-11-15', 720);

-- Train T013 classes
INSERT INTO seat_availability VALUES
('T013', 'C030', '2025-11-14', 162),
('T013', 'C030', '2025-11-15', 162),
('T013', 'C031', '2025-11-14', 324),
('T013', 'C031', '2025-11-15', 324),
('T013', 'C032', '2025-11-14', 792),
('T013', 'C032', '2025-11-15', 792);

-- Train T014 classes
INSERT INTO seat_availability VALUES
('T014', 'C033', '2025-11-14', 36),
('T014', 'C033', '2025-11-15', 36),
('T014', 'C034', '2025-11-14', 216),
('T014', 'C034', '2025-11-15', 216),
('T014', 'C035', '2025-11-14', 378),
('T014', 'C035', '2025-11-15', 378);

-- ========================================
-- INSERT CONNECTED (Station-Train mapping)
-- ========================================
INSERT INTO connected VALUES
('S001', 'T001'),
('S002', 'T001'),
('S001', 'T002'),
('S002', 'T002'),
('S001', 'T003'),
('S003', 'T003'),
('S001', 'T004'),
('S003', 'T004'),
('S002', 'T005'),
('S005', 'T005'),
('S002', 'T006'),
('S005', 'T006'),
('S003', 'T007'),
('S004', 'T007'),
('S003', 'T008'),
('S004', 'T008'),
('S004', 'T009'),
('S005', 'T009'),
('S004', 'T010'),
('S005', 'T010'),
('S001', 'T011'),
('S004', 'T011'),
('S001', 'T012'),
('S004', 'T012'),
('S002', 'T013'),
('S003', 'T013'),
('S002', 'T014'),
('S003', 'T014');

-- ========================================
-- INSERT TRAIN STATUS (Sample current status)
-- ========================================
INSERT INTO train_status VALUES
('T001', '2025-11-13', 'S001', 0, 'on_time'),
('T002', '2025-11-13', 'S001', 15, 'delayed'),
('T003', '2025-11-13', 'S001', 0, 'on_time'),
('T005', '2025-11-13', 'S002', 0, 'on_time'),
('T007', '2025-11-13', 'S003', 0, 'on_time'),
('T009', '2025-11-13', 'S004', 30, 'delayed');

