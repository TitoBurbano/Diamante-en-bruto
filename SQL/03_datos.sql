-- =====================================================================
-- Diamante en Bruto - Script 03: datos de prueba
-- Ejecutar después de 01_tablas.sql y 02_vistas.sql, sobre tablas vacías.
-- Los ids se generan con SERIAL en el orden de inserción (1, 2, 3...) y
-- los INSERT de las tablas hijas dependen de ese orden.
-- Los datos incluyen casos "sin relación" a propósito: una categoría sin
-- joyas, un proveedor sin órdenes y clientes que nunca han comprado.
-- =====================================================================

INSERT INTO categoria (nombre, descripcion) VALUES
('Anillo',      'Anillos, argollas y solitarios'),
('Collar',      'Collares, cadenas y gargantillas'),
('Pulsera',     'Pulseras y esclavas'),
('Pendientes',  'Aretes y pendientes'),
('Reloj',       'Relojes de pulsera y de bolsillo'),
('Gema suelta', 'Piedras preciosas sin engastar'),
('Broche',      'Broches y prendedores');

INSERT INTO material (nombre, pureza) VALUES
('Oro amarillo', '18k'),
('Oro blanco',   '18k'),
('Oro rosado',   '14k'),
('Plata',        '925'),
('Platino',      '950'),
('Ópalo negro',  'Natural'),
('Diamante',     'Natural');

INSERT INTO proveedor (nombre, nit, telefono, email, ciudad) VALUES
('Diamantes del Norte S.A.S.',        '900123456-1', '6012345678', 'ventas@diamantesdelnorte.co',  'Bogotá'),
('Gemas de Etiopía Ltda.',            '800234567-2', '6044567890', 'contacto@gemasetiopia.co',     'Medellín'),
('Oro y Plata Importados S.A.',       '901345678-3', '6025551234', 'pedidos@oroyplata.co',         'Cali'),
('Relojes Suizos Colombia',           '900456789-4', '6017778899', 'info@relojessuizos.co',        'Bogotá'),
('Platería Artesanal La Candelaria',  '830567890-5', '6013334455', 'taller@platerialacandelaria.co', 'Bogotá'),
('Joyas Express Cartagena',           '901678901-6', '6056667788', 'ventas@joyasexpress.co',       'Cartagena');

INSERT INTO cliente (documento, nombre, telefono, email, es_vip, fecha_registro) VALUES
('1010101010', 'Carlos Andrés Rojas Pérez',   '3001112233', 'carlos.rojas@correo.com',     TRUE,  CURRENT_DATE - 400),
('1020202020', 'María Fernanda Gómez Ruiz',   '3002223344', 'maria.gomez@correo.com',      TRUE,  CURRENT_DATE - 300),
('1030303030', 'Juan Pablo Martínez Silva',   '3003334455', 'juan.martinez@correo.com',    FALSE, CURRENT_DATE - 200),
('1040404040', 'Laura Camila Torres León',    '3004445566', 'laura.torres@correo.com',     FALSE, CURRENT_DATE - 150),
('1050505050', 'Andrés Felipe Castro Díaz',   '3005556677', 'andres.castro@correo.com',    FALSE, CURRENT_DATE - 100),
('1060606060', 'Diana Marcela Herrera Mora',  '3006667788', 'diana.herrera@correo.com',    FALSE, CURRENT_DATE - 90),
('1070707070', 'Sebastián Ortiz Vargas',      '3007778899', 'sebastian.ortiz@correo.com',  FALSE, CURRENT_DATE - 80),
('1080808080', 'Valentina Salazar Mejía',     '3008889900', 'valentina.salazar@correo.com', FALSE, CURRENT_DATE - 70);

INSERT INTO empleado (nombre, cargo, email, activo) VALUES
('Ricardo Salazar Gómez',  'ADMINISTRADOR', 'ricardo.salazar@diamanteenbruto.co', TRUE),
('Paola Andrea Ríos',      'VENDEDOR',      'paola.rios@diamanteenbruto.co',      TRUE),
('Julián David Moreno',    'VENDEDOR',      'julian.moreno@diamanteenbruto.co',   TRUE),
('Natalia Cárdenas Ortiz', 'AVALUADOR',     'natalia.cardenas@diamanteenbruto.co', TRUE),
('Esteban Ruiz Parra',     'VENDEDOR',      'esteban.ruiz@diamanteenbruto.co',    FALSE);

-- Joyas 1-13: llegan por órdenes de compra de proveedores.
-- Joyas 14-18: llegan por empeños (sin proveedor, precio_compra = préstamo).
INSERT INTO joya (codigo, nombre, id_categoria, id_material, id_proveedor, peso_gramos, quilates, precio_compra, precio_venta, estado, fecha_ingreso) VALUES
('DIA-AN-001', 'Anillo solitario diamante 1 ct',          1, 5, 1,    4.20, 1.00,  9000000, 13500000, 'VENDIDA',    CURRENT_DATE - 60),
('DIA-PE-002', 'Pendientes diamante 0.5 ct',              4, 2, 1,    3.10, 0.50,  4200000,  6300000, 'DISPONIBLE', CURRENT_DATE - 60),
('DIA-CO-003', 'Collar diamantes en cascada',             2, 2, 1,   12.50, 2.30, 15000000, 22000000, 'DISPONIBLE', CURRENT_DATE - 60),
('OPA-GE-004', 'Ópalo negro de Etiopía 3.2 ct',           6, 6, 2,    0.64, 3.20,  7000000, 12000000, 'DISPONIBLE', CURRENT_DATE - 50),
('OPA-AN-005', 'Anillo ópalo negro engastado',            1, 1, 2,    5.80, 2.10,  5500000,  9000000, 'VENDIDA',    CURRENT_DATE - 50),
('ORO-AN-006', 'Argolla de matrimonio oro 18k',           1, 1, 3,    6.00, NULL,  1800000,  2600000, 'VENDIDA',    CURRENT_DATE - 40),
('ORO-CO-007', 'Cadena cubana oro 18k',                   2, 1, 3,   25.00, NULL,  7500000, 10500000, 'DISPONIBLE', CURRENT_DATE - 40),
('ORO-PU-008', 'Pulsera de eslabones oro rosado 14k',     3, 3, 3,   14.20, NULL,  3800000,  5400000, 'DISPONIBLE', CURRENT_DATE - 40),
('PLA-PU-009', 'Pulsera de plata 925',                    3, 4, 3,   18.00, NULL,   350000,   620000, 'VENDIDA',    CURRENT_DATE - 40),
('REL-AU-010', 'Reloj suizo automático acero y oro',      5, 1, 4,   95.00, NULL,  8000000, 12500000, 'DISPONIBLE', CURRENT_DATE - 30),
('REL-BO-011', 'Reloj de bolsillo antiguo',               5, 4, 4,   70.00, NULL,  2200000,  3900000, 'DISPONIBLE', CURRENT_DATE - 30),
('PLA-PE-012', 'Pendientes de plata filigrana',           4, 4, 5,    5.50, NULL,   180000,   380000, 'VENDIDA',    CURRENT_DATE - 20),
('PLA-CO-013', 'Collar de plata con dije',                2, 4, 5,    9.80, NULL,   260000,   480000, 'VENDIDA',    CURRENT_DATE - 20),
('EMP-014',    'Anillo diamante 0.8 ct (empeño)',         1, 2, NULL, 3.90, 0.80,  4000000,  8000000, 'EMPENADA',   CURRENT_DATE - 15),
('EMP-015',    'Reloj de oro 18k (empeño)',               5, 1, NULL, 80.00, NULL, 3000000,  6000000, 'EMPENADA',   CURRENT_DATE - 65),
('EMP-016',    'Collar de oro 18k (empeño)',              2, 1, NULL, 20.00, NULL, 1500000,  5000000, 'DEVUELTA',   CURRENT_DATE - 90),
('EMP-017',    'Pulsera de oro blanco (empeño)',          3, 2, NULL, 11.00, NULL, 1800000,  3600000, 'DISPONIBLE', CURRENT_DATE - 120),
('EMP-018',    'Anillo de oro rosado (empeño)',           1, 3, NULL,  4.50, NULL,  900000,  1800000, 'EMPENADA',   CURRENT_DATE - 5);


-- Ventas: los clientes VIP (1 y 2) tienen 10 % de descuento sobre el
-- subtotal. La venta 4 está anulada (su joya volvió a DISPONIBLE).
INSERT INTO venta (id_cliente, id_empleado, fecha, descuento, total, estado, motivo_anulacion) VALUES
(1, 2, CURRENT_TIMESTAMP - INTERVAL '25 days', 1350000, 12150000, 'COMPLETADA', NULL),
(3, 3, CURRENT_TIMESTAMP - INTERVAL '22 days',       0, 11600000, 'COMPLETADA', NULL),
(2, 2, CURRENT_TIMESTAMP - INTERVAL '12 days',   62000,   558000, 'COMPLETADA', NULL),
(4, 3, CURRENT_TIMESTAMP - INTERVAL '8 days',        0,  3900000, 'ANULADA',    'El cliente se arrepintió dentro del plazo de devolución'),
(1, 3, CURRENT_TIMESTAMP - INTERVAL '3 days',    86000,   774000, 'COMPLETADA', NULL);

INSERT INTO detalle_venta (id_venta, id_joya, precio_unitario) VALUES
(1, 1, 13500000),
(2, 5,  9000000),
(2, 6,  2600000),
(3, 9,   620000),
(4, 11, 3900000),
(5, 12,  380000),
(5, 13,  480000);

-- Órdenes de compra a proveedores (el proveedor 6 no tiene ninguna).
INSERT INTO orden_compra (id_proveedor, id_empleado, fecha, total) VALUES
(1, 1, CURRENT_DATE - 60, 28200000),
(2, 1, CURRENT_DATE - 50, 12500000),
(3, 1, CURRENT_DATE - 40, 13450000),
(4, 1, CURRENT_DATE - 30, 10200000),
(5, 1, CURRENT_DATE - 20,   440000);

INSERT INTO detalle_orden_compra (id_orden, id_joya, costo) VALUES
(1, 1,   9000000),
(1, 2,   4200000),
(1, 3,  15000000),
(2, 4,   7000000),
(2, 5,   5500000),
(3, 6,   1800000),
(3, 7,   7500000),
(3, 8,   3800000),
(3, 9,    350000),
(4, 10,  8000000),
(4, 11,  2200000),
(5, 12,   180000),
(5, 13,   260000);

-- Empeños: 1 y 5 activos y vigentes; 2 activo pero ya vencido (sirve
-- para probar "vencer empeño"); 3 saldado; 4 vencido.
INSERT INTO empeno (id_cliente, id_joya, id_empleado, monto_prestamo, tasa_interes, fecha_inicio, fecha_vencimiento, estado, fecha_cierre, monto_pagado) VALUES
(5, 14, 4, 4000000, 4.00, CURRENT_DATE - 15,  CURRENT_DATE + 45, 'ACTIVO',  NULL,               NULL),
(7, 15, 4, 3000000, 5.00, CURRENT_DATE - 65,  CURRENT_DATE - 5,  'ACTIVO',  NULL,               NULL),
(8, 16, 4, 1500000, 4.00, CURRENT_DATE - 90,  CURRENT_DATE - 30, 'SALDADO', CURRENT_DATE - 45,  1590000),
(6, 17, 4, 1800000, 5.00, CURRENT_DATE - 120, CURRENT_DATE - 60, 'VENCIDO', CURRENT_DATE - 60,  NULL),
(1, 18, 4,  900000, 4.00, CURRENT_DATE - 5,   CURRENT_DATE + 85, 'ACTIVO',  NULL,               NULL);