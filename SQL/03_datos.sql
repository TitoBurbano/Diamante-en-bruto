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