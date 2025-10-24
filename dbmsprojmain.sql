
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
