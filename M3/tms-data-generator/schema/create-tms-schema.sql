DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS order_timeline_events;
DROP TABLE IF EXISTS transportation_orders;
DROP TABLE IF EXISTS driver_availability;
DROP TABLE IF EXISTS vehicle_availability;
DROP TABLE IF EXISTS availability_reason;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS vehicles;

CREATE TABLE vehicles (
    id INT PRIMARY KEY,
    make VARCHAR(50),
    model VARCHAR(50),
    year INT,
    fuel_tank_capacity DECIMAL(5,1)
);

CREATE TABLE drivers (
    id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    contract_type VARCHAR(20),
    status VARCHAR(20)
);

CREATE TABLE customers (
    id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    customer_type VARCHAR(20),
    address VARCHAR(255)
);

CREATE TABLE transportation_orders (
    id INT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP NOT NULL,
    expected_delivery DATE,
    shipping_address VARCHAR(255),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(50),
    shipping_zip_code VARCHAR(20),
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_timeline_events (
    id INT PRIMARY KEY,
    order_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    title VARCHAR(100),
    description TEXT,
    executed_by VARCHAR(100),
    FOREIGN KEY (order_id) REFERENCES transportation_orders(id)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    item_type VARCHAR(20) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES transportation_orders(id)
);

-- Availability reason dictionary
CREATE TABLE availability_reason (
    reason_code VARCHAR(50) PRIMARY KEY,
    reason_description VARCHAR(255) NOT NULL,
    is_available BOOLEAN NOT NULL,
    applies_to VARCHAR(20) NOT NULL -- 'DRIVER', 'VEHICLE', or 'BOTH'
);

-- Driver availability tracking
CREATE TABLE driver_availability (
    id INT PRIMARY KEY,
    driver_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    reason_code VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (reason_code) REFERENCES availability_reason(reason_code)
);

-- Vehicle availability tracking
CREATE TABLE vehicle_availability (
    id INT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    reason_code VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (reason_code) REFERENCES availability_reason(reason_code)
);

-- Insert availability reason codes
INSERT INTO availability_reason (reason_code, reason_description, is_available, applies_to) VALUES
-- Driver reasons
('WORKING', 'Standardowy czas pracy kierowcy', TRUE, 'DRIVER'),
('REST', 'Planowany odpoczynek (np. weekend, 45h)', FALSE, 'DRIVER'),
('HOLIDAY', 'Urlop', FALSE, 'DRIVER'),
('SICK', 'Zwolnienie lekarskie', FALSE, 'DRIVER'),
('TRAINING', 'Szkolenie/Kurs', FALSE, 'DRIVER'),
('AVAILABLE', 'Kierowca dostępny do pracy', TRUE, 'DRIVER'),
-- Vehicle reasons
('READY', 'Pojazd gotowy do użytku', TRUE, 'VEHICLE'),
('MAINTENANCE', 'Planowany serwis/przegląd', FALSE, 'VEHICLE'),
('BREAKDOWN', 'Awaria/Naprawa', FALSE, 'VEHICLE'),
('REGISTRATION', 'Badanie techniczne', FALSE, 'VEHICLE'),
('WASHING', 'Mycie pojazdu', FALSE, 'VEHICLE');

CREATE INDEX idx_timeline_order ON order_timeline_events(order_id);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_orders_customer ON transportation_orders(customer_id);
CREATE INDEX idx_orders_status ON transportation_orders(status);
CREATE INDEX idx_driver_availability_driver ON driver_availability(driver_id);
CREATE INDEX idx_driver_availability_time ON driver_availability(start_time, end_time);
CREATE INDEX idx_vehicle_availability_vehicle ON vehicle_availability(vehicle_id);
CREATE INDEX idx_vehicle_availability_time ON vehicle_availability(start_time, end_time);
