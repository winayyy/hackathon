CREATE DATABASE IF NOT EXISTS dataops_demo;

USE dataops_demo;

CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(40)
);

INSERT INTO customers (name, city, status, email, phone)
VALUES
    ('Vinay', 'Bengaluru', 'active',
     'vinay@example.test', '9000000001'),
    ('Srinithi', 'Hyderabad', 'active',
     'srinithi@example.test', '9000000002'),
    ('Shamsul', 'Chennai', 'inactive',
     'shamsul@example.test', '9000000003'),
    ('Sai', 'Pune', 'active',
     'sai@example.test', '9000000004'),
    ('Arup', 'Mumbai', 'inactive',
     'arup@example.test', '9000000005');

-- Restrict the application account to read-only access.
REVOKE ALL PRIVILEGES, GRANT OPTION
FROM 'dataops_reader'@'%';

GRANT SELECT ON dataops_demo.*
TO 'dataops_reader'@'%';
