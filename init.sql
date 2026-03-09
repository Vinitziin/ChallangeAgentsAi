-- Seed data for the assistant's SQL agent demo

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(80),
    price NUMERIC(10,2) NOT NULL,
    stock INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL DEFAULT 1,
    total NUMERIC(10,2) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers
INSERT INTO customers (name, email, city) VALUES
('Ana Silva',     'ana@example.com',     'São Paulo'),
('Bruno Costa',   'bruno@example.com',   'Rio de Janeiro'),
('Carla Mendes',  'carla@example.com',   'Belo Horizonte'),
('Diego Rocha',   'diego@example.com',   'Curitiba'),
('Elena Ferreira','elena@example.com',   'Porto Alegre');

-- Products
INSERT INTO products (name, category, price, stock) VALUES
('Notebook Pro 15',     'Eletrônicos', 4599.90, 25),
('Mouse Wireless X',    'Periféricos',  129.90, 150),
('Teclado Mecânico K7', 'Periféricos',  349.90, 80),
('Monitor 27" 4K',      'Eletrônicos', 2199.90, 40),
('Webcam HD 1080p',     'Periféricos',  259.90, 60),
('Cadeira Ergonômica',  'Móveis',      1899.90, 15),
('Hub USB-C 7 portas',  'Periféricos',  189.90, 200),
('SSD 1TB NVMe',        'Componentes',  449.90, 90);

-- Orders
INSERT INTO orders (customer_id, product_id, quantity, total, status, ordered_at) VALUES
(1, 1, 1, 4599.90, 'delivered',  '2025-01-10 14:30:00'),
(1, 2, 2,  259.80, 'delivered',  '2025-01-10 14:30:00'),
(2, 4, 1, 2199.90, 'shipped',    '2025-02-05 09:15:00'),
(3, 6, 1, 1899.90, 'delivered',  '2025-02-12 11:00:00'),
(3, 3, 1,  349.90, 'delivered',  '2025-02-12 11:00:00'),
(4, 8, 2,  899.80, 'processing', '2025-03-01 16:45:00'),
(5, 5, 1,  259.90, 'pending',    '2025-03-03 08:20:00'),
(2, 7, 3,  569.70, 'shipped',    '2025-03-04 10:00:00');
