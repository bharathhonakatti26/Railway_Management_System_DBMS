CREATE DATABASE IF NOT EXISTS railway_system;
USE railway_system;

CREATE TABLE user (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    dob DATE,
    gender ENUM('male','female','other'),
    city VARCHAR(50),
    state VARCHAR(50),
    pin_code VARCHAR(10),
    role ENUM('passenger','employee','admin') DEFAULT 'passenger'
);

CREATE TABLE user_mobile (
    user_id VARCHAR(10),
    mobile_no VARCHAR(15) NOT NULL,
    PRIMARY KEY (user_id, mobile_no),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);


CREATE TABLE station (
    station_id VARCHAR(10) PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    state VARCHAR(50)
);

CREATE TABLE route (
    route_id VARCHAR(10) PRIMARY KEY,
    route_name VARCHAR(50)
);

CREATE TABLE route_station (
    route_id VARCHAR(10),
    station_id VARCHAR(10),
    stop_no INT CHECK (stop_no > 0),
    arrival_time TIME,
    departure_time TIME,
    PRIMARY KEY (route_id, station_id),
    FOREIGN KEY (route_id) REFERENCES route(route_id) ON DELETE CASCADE,
    FOREIGN KEY (station_id) REFERENCES station(station_id) ON DELETE CASCADE
);

CREATE TABLE train (
    train_no VARCHAR(10) PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    type ENUM('passenger','express','superfast','shatabdi','rajdhani','duronto','vande_bharat') NOT NULL,
    base_fare_multiplier DECIMAL(5,2) DEFAULT 1.0 CHECK (base_fare_multiplier >= 0),
    route_id VARCHAR(10),
    FOREIGN KEY (route_id) REFERENCES route(route_id)
);

CREATE TABLE schedule (
    schedule_id VARCHAR(10) PRIMARY KEY,
    train_no VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    running_days VARCHAR(50),
    FOREIGN KEY (train_no) REFERENCES train(train_no) ON DELETE CASCADE
);

CREATE TABLE class (
    class_id VARCHAR(10) PRIMARY KEY,
    class_name VARCHAR(50),
    coach_type ENUM('sleeper','ac','general'),
    no_of_coaches INT CHECK (no_of_coaches > 0),
    c_multiplier DECIMAL(5,2) DEFAULT 1.0,
    train_no VARCHAR(10),
    FOREIGN KEY (train_no) REFERENCES train(train_no)
);

CREATE TABLE berth (
    berth_id VARCHAR(10) PRIMARY KEY,
    class_id VARCHAR(10),
    coach_no INT CHECK (coach_no > 0),
    berth_no INT CHECK (berth_no > 0),
    status ENUM('available','booked') DEFAULT 'available',
    FOREIGN KEY (class_id) REFERENCES class(class_id) ON DELETE CASCADE
);

CREATE TABLE seat_availability (
    train_no VARCHAR(10),
    class_id VARCHAR(10),
    travel_date DATE,
    available_seats INT CHECK (available_seats >= 0),
    PRIMARY KEY (train_no, class_id, travel_date),
    FOREIGN KEY (train_no) REFERENCES train(train_no),
    FOREIGN KEY (class_id) REFERENCES class(class_id)
);

CREATE TABLE ticket (
    pnr_no VARCHAR(15) PRIMARY KEY,
    train_no VARCHAR(10),
    user_id VARCHAR(10),
    source_station VARCHAR(10),
    destination_station VARCHAR(10),
    travel_date DATE,
    booking_time DATETIME DEFAULT NOW(),
    total_fare DECIMAL(10,2),
    status ENUM('booked','cancelled','waiting') DEFAULT 'booked',
    FOREIGN KEY (train_no) REFERENCES train(train_no),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (source_station) REFERENCES station(station_id),
    FOREIGN KEY (destination_station) REFERENCES station(station_id)
);

CREATE TABLE passenger (
    passenger_id VARCHAR(10) PRIMARY KEY,
    pnr_no VARCHAR(15),
    passenger_name VARCHAR(100),
    age INT,
    gender ENUM('male','female','other'),
    berth_pref VARCHAR(20),
    FOREIGN KEY (pnr_no) REFERENCES ticket(pnr_no) ON DELETE CASCADE
);

-- ==========================
-- 6. PAYMENT & CANCELLATION
-- ==========================
CREATE TABLE payment (
    transaction_id VARCHAR(10) PRIMARY KEY,
    pnr_no VARCHAR(15),
    user_id VARCHAR(10),
    amount DECIMAL(10,2),
    mode ENUM('credit_card','debit_card','upi','net_banking','wallet'),
    status ENUM('success','failed','pending') DEFAULT 'success',
    transaction_date DATETIME DEFAULT NOW(),
    FOREIGN KEY (pnr_no) REFERENCES ticket(pnr_no),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE cancellation (
    cancel_id VARCHAR(10) PRIMARY KEY,
    pnr_no VARCHAR(15),
    cancel_date DATETIME DEFAULT NOW(),
    refund_amount DECIMAL(10,2),
    reason VARCHAR(100),
    FOREIGN KEY (pnr_no) REFERENCES ticket(pnr_no)
);

CREATE TABLE train_status (
    train_no VARCHAR(10),
    status_date DATE,
    current_station VARCHAR(10),
    delay_minutes INT DEFAULT 0,
    status ENUM('on_time','delayed','cancelled') DEFAULT 'on_time',
    PRIMARY KEY (train_no, status_date),
    FOREIGN KEY (train_no) REFERENCES train(train_no),
    FOREIGN KEY (current_station) REFERENCES station(station_id)
);

CREATE TABLE connected (
    station_id VARCHAR(10),
    train_no VARCHAR(10),
    PRIMARY KEY (station_id, train_no),
    FOREIGN KEY (station_id) REFERENCES station(station_id),
    FOREIGN KEY (train_no) REFERENCES train(train_no)
);

-- ========================================
-- TRIGGERS
-- ========================================

-- Trigger 1: Auto-update seat availability after ticket booking
DELIMITER //
CREATE TRIGGER after_ticket_insert
AFTER INSERT ON ticket
FOR EACH ROW
BEGIN
    DECLARE seat_count INT;
    
    SELECT COUNT(*) INTO seat_count
    FROM passenger
    WHERE pnr_no = NEW.pnr_no;
    
    UPDATE seat_availability
    SET available_seats = available_seats - seat_count
    WHERE train_no = NEW.train_no
    AND travel_date = NEW.travel_date;
END//
DELIMITER ;

-- Trigger 2: Update seat availability on ticket cancellation
DELIMITER //
CREATE TRIGGER after_ticket_cancel
AFTER UPDATE ON ticket
FOR EACH ROW
BEGIN
    DECLARE seat_count INT;
    
    IF NEW.status = 'cancelled' AND OLD.status != 'cancelled' THEN
        SELECT COUNT(*) INTO seat_count
        FROM passenger
        WHERE pnr_no = NEW.pnr_no;
        
        UPDATE seat_availability
        SET available_seats = available_seats + seat_count
        WHERE train_no = NEW.train_no
        AND travel_date = NEW.travel_date;
    END IF;
END//
DELIMITER ;

-- Trigger 3: Update berth status when passenger is assigned
DELIMITER //
CREATE TRIGGER update_berth_status
AFTER INSERT ON passenger
FOR EACH ROW
BEGIN
    UPDATE berth
    SET status = 'booked'
    WHERE berth_id = NEW.berth_pref
    AND status = 'available';
END//
DELIMITER ;

-- Trigger 4: Validate booking date (must be future date)
DELIMITER //
CREATE TRIGGER validate_travel_date
BEFORE INSERT ON ticket
FOR EACH ROW
BEGIN
    IF NEW.travel_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Travel date must be a future date';
    END IF;
END//
DELIMITER ;

-- Trigger 5: Auto-calculate refund amount on cancellation
DELIMITER //
CREATE TRIGGER calculate_refund
BEFORE INSERT ON cancellation
FOR EACH ROW
BEGIN
    DECLARE ticket_fare DECIMAL(10,2);
    DECLARE days_before INT;
    
    SELECT total_fare, DATEDIFF(travel_date, CURDATE())
    INTO ticket_fare, days_before
    FROM ticket
    WHERE pnr_no = NEW.pnr_no;
    
    IF days_before > 7 THEN
        SET NEW.refund_amount = ticket_fare * 0.90; -- 10% cancellation charge
    ELSEIF days_before BETWEEN 2 AND 7 THEN
        SET NEW.refund_amount = ticket_fare * 0.70; -- 30% cancellation charge
    ELSE
        SET NEW.refund_amount = ticket_fare * 0.50; -- 50% cancellation charge
    END IF;
END//
DELIMITER ;

-- ========================================
-- STORED PROCEDURES
-- ========================================

-- Procedure 1: Book a ticket
DELIMITER //
CREATE PROCEDURE book_ticket(
    IN p_pnr VARCHAR(15),
    IN p_train_no VARCHAR(10),
    IN p_user_id VARCHAR(10),
    IN p_source VARCHAR(10),
    IN p_destination VARCHAR(10),
    IN p_travel_date DATE,
    IN p_class_id VARCHAR(10),
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE available INT;
    DECLARE base_fare DECIMAL(10,2);
    DECLARE distance INT;
    DECLARE multiplier DECIMAL(5,2);
    DECLARE class_mult DECIMAL(5,2);
    
    -- Check seat availability
    SELECT available_seats INTO available
    FROM seat_availability
    WHERE train_no = p_train_no
    AND class_id = p_class_id
    AND travel_date = p_travel_date;
    
    IF available > 0 THEN
        -- Calculate fare
        SELECT t.base_fare_multiplier, c.c_multiplier
        INTO multiplier, class_mult
        FROM train t
        JOIN class c ON t.train_no = c.train_no
        WHERE t.train_no = p_train_no AND c.class_id = p_class_id;
        
        SET distance = ABS(
            (SELECT stop_no FROM route_station rs 
             JOIN train t ON rs.route_id = t.route_id 
             WHERE t.train_no = p_train_no AND rs.station_id = p_source) -
            (SELECT stop_no FROM route_station rs 
             JOIN train t ON rs.route_id = t.route_id 
             WHERE t.train_no = p_train_no AND rs.station_id = p_destination)
        );
        
        SET base_fare = distance * 10 * multiplier * class_mult;
        
        -- Insert ticket
        INSERT INTO ticket (pnr_no, train_no, user_id, source_station, destination_station, travel_date, total_fare, status)
        VALUES (p_pnr, p_train_no, p_user_id, p_source, p_destination, p_travel_date, base_fare, 'booked');
        
        SET p_result = 'Ticket booked successfully';
    ELSE
        SET p_result = 'No seats available';
    END IF;
END//
DELIMITER ;

-- Procedure 2: Cancel ticket
DELIMITER //
CREATE PROCEDURE cancel_ticket(
    IN p_pnr VARCHAR(15),
    IN p_cancel_id VARCHAR(10),
    IN p_reason VARCHAR(100),
    OUT p_message VARCHAR(100)
)
BEGIN
    DECLARE ticket_status VARCHAR(20);
    
    SELECT status INTO ticket_status
    FROM ticket
    WHERE pnr_no = p_pnr;
    
    IF ticket_status = 'booked' THEN
        UPDATE ticket SET status = 'cancelled' WHERE pnr_no = p_pnr;
        INSERT INTO cancellation (cancel_id, pnr_no, reason)
        VALUES (p_cancel_id, p_pnr, p_reason);
        SET p_message = 'Ticket cancelled successfully';
    ELSE
        SET p_message = 'Ticket cannot be cancelled';
    END IF;
END//
DELIMITER ;

-- Procedure 3: Search trains between stations
DELIMITER //
CREATE PROCEDURE search_trains(
    IN p_source VARCHAR(10),
    IN p_destination VARCHAR(10),
    IN p_travel_date DATE
)
BEGIN
    SELECT DISTINCT t.train_no, t.train_name, t.type,
           rs1.departure_time AS source_departure,
           rs2.arrival_time AS destination_arrival
    FROM train t
    JOIN route_station rs1 ON t.route_id = rs1.route_id AND rs1.station_id = p_source
    JOIN route_station rs2 ON t.route_id = rs2.route_id AND rs2.station_id = p_destination
    WHERE rs1.stop_no < rs2.stop_no
    ORDER BY rs1.departure_time;
END//
DELIMITER ;

-- Procedure 4: Get passenger booking history
DELIMITER //
CREATE PROCEDURE get_booking_history(IN p_user_id VARCHAR(10))
BEGIN
    SELECT t.pnr_no, t.train_no, tr.train_name, 
           t.source_station, t.destination_station,
           t.travel_date, t.booking_time, t.total_fare, t.status
    FROM ticket t
    JOIN train tr ON t.train_no = tr.train_no
    WHERE t.user_id = p_user_id
    ORDER BY t.booking_time DESC;
END//
DELIMITER ;

-- Procedure 5: Update train status
DELIMITER //
CREATE PROCEDURE update_train_status(
    IN p_train_no VARCHAR(10),
    IN p_status_date DATE,
    IN p_current_station VARCHAR(10),
    IN p_delay_minutes INT,
    IN p_status VARCHAR(20)
)
BEGIN
    INSERT INTO train_status (train_no, status_date, current_station, delay_minutes, status)
    VALUES (p_train_no, p_status_date, p_current_station, p_delay_minutes, p_status)
    ON DUPLICATE KEY UPDATE
        current_station = p_current_station,
        delay_minutes = p_delay_minutes,
        status = p_status;
END//
DELIMITER ;

-- ========================================
-- FUNCTIONS
-- ========================================

-- Function 1: Calculate fare between two stations
DELIMITER //
CREATE FUNCTION calculate_fare(
    p_train_no VARCHAR(10),
    p_class_id VARCHAR(10),
    p_source VARCHAR(10),
    p_destination VARCHAR(10)
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE distance INT;
    DECLARE multiplier DECIMAL(5,2);
    DECLARE class_mult DECIMAL(5,2);
    DECLARE fare DECIMAL(10,2);
    
    SELECT t.base_fare_multiplier, c.c_multiplier
    INTO multiplier, class_mult
    FROM train t
    JOIN class c ON t.train_no = c.train_no
    WHERE t.train_no = p_train_no AND c.class_id = p_class_id;
    
    SET distance = ABS(
        (SELECT stop_no FROM route_station rs 
         JOIN train t ON rs.route_id = t.route_id 
         WHERE t.train_no = p_train_no AND rs.station_id = p_source) -
        (SELECT stop_no FROM route_station rs 
         JOIN train t ON rs.route_id = t.route_id 
         WHERE t.train_no = p_train_no AND rs.station_id = p_destination)
    );
    
    SET fare = distance * 10 * multiplier * class_mult;
    RETURN fare;
END//
DELIMITER ;

-- Function 2: Get available seats for a train
DELIMITER //
CREATE FUNCTION get_available_seats(
    p_train_no VARCHAR(10),
    p_class_id VARCHAR(10),
    p_travel_date DATE
)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE seats INT;
    
    SELECT available_seats INTO seats
    FROM seat_availability
    WHERE train_no = p_train_no
    AND class_id = p_class_id
    AND travel_date = p_travel_date;
    
    RETURN IFNULL(seats, 0);
END//
DELIMITER ;

-- Function 3: Check if train runs on a specific day
DELIMITER //
CREATE FUNCTION train_runs_on_day(
    p_train_no VARCHAR(10),
    p_date DATE
)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE day_name VARCHAR(10);
    DECLARE running_days VARCHAR(50);
    
    SET day_name = DAYNAME(p_date);
    
    SELECT s.running_days INTO running_days
    FROM schedule s
    WHERE s.train_no = p_train_no;
    
    RETURN LOCATE(day_name, running_days) > 0;
END//
DELIMITER ;

-- Function 4: Get journey duration
DELIMITER //
CREATE FUNCTION get_journey_duration(
    p_train_no VARCHAR(10),
    p_source VARCHAR(10),
    p_destination VARCHAR(10)
)
RETURNS TIME
DETERMINISTIC
BEGIN
    DECLARE start_time TIME;
    DECLARE end_time TIME;
    DECLARE duration TIME;
    
    SELECT rs1.departure_time, rs2.arrival_time
    INTO start_time, end_time
    FROM route_station rs1
    JOIN route_station rs2 ON rs1.route_id = rs2.route_id
    JOIN train t ON t.route_id = rs1.route_id
    WHERE t.train_no = p_train_no
    AND rs1.station_id = p_source
    AND rs2.station_id = p_destination;
    
    SET duration = TIMEDIFF(end_time, start_time);
    RETURN duration;
END//
DELIMITER ;

-- Function 5: Get total bookings for user
DELIMITER //
CREATE FUNCTION get_user_booking_count(p_user_id VARCHAR(10))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE booking_count INT;
    
    SELECT COUNT(*) INTO booking_count
    FROM ticket
    WHERE user_id = p_user_id
    AND status = 'booked';
    
    RETURN booking_count;
END//
DELIMITER ;
