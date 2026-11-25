-- =====================================================================
-- Diamante en Bruto - Script 02: vistas
-- Ejecutar después de 01_tablas.sql (se puede repetir).
-- =====================================================================

-- ---------------------------------------------------------------------
-- VISTA: vista_inventario_disponible
-- Combina las tablas joya, categoria, material y proveedor.
-- Muestra las joyas que están a la venta (estado DISPONIBLE) con el
-- nombre de su categoría, material y proveedor, sin que el cliente de
-- la API tenga que escribir los JOIN. El proveedor se une con LEFT JOIN
-- porque las joyas que llegan por un empeño no tienen proveedor.
-- Usada en el endpoint GET /reportes/inventario.
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS vista_inventario_disponible;

CREATE VIEW vista_inventario_disponible AS
SELECT
    j.id_joya,
    j.codigo,
    j.nombre        AS joya,
    c.nombre        AS categoria,
    m.nombre        AS material,
    m.pureza,
    j.peso_gramos,
    j.quilates,
    j.precio_venta,
    p.nombre        AS proveedor,
    j.fecha_ingreso
FROM joya j
JOIN categoria c       ON c.id_categoria = j.id_categoria
JOIN material m        ON m.id_material  = j.id_material
LEFT JOIN proveedor p  ON p.id_proveedor = j.id_proveedor
WHERE j.estado = 'DISPONIBLE';