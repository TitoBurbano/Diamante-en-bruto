-- =====================================================================
-- Diamante en Bruto - Sistema de gestión de joyería
-- Script 01: tablas, restricciones y llaves foráneas
-- Ejecutar sobre una base de datos PostgreSQL 14+
-- Todas las restricciones tienen nombre explícito:
--   pk_  llave primaria     uq_  unicidad     chk_  validación
--   fk_  llave foránea      idx_ índice
-- =====================================================================

-- Eliminación en orden inverso a las dependencias (hijas primero).
DROP TABLE IF EXISTS empeno CASCADE;
DROP TABLE IF EXISTS detalle_orden_compra CASCADE;
DROP TABLE IF EXISTS orden_compra CASCADE;
DROP TABLE IF EXISTS detalle_venta CASCADE;
DROP TABLE IF EXISTS venta CASCADE;
DROP TABLE IF EXISTS joya CASCADE;
DROP TABLE IF EXISTS empleado CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS proveedor CASCADE;
DROP TABLE IF EXISTS material CASCADE;
DROP TABLE IF EXISTS categoria CASCADE;

-- ---------------------------------------------------------------------
-- categoria: tipo de joya (anillo, collar, reloj, gema suelta, etc)
-- ---------------------------------------------------------------------
CREATE TABLE categoria (
    id_categoria  SERIAL,
    nombre        VARCHAR(60) NOT NULL,
    descripcion   TEXT,
    CONSTRAINT pk_categoria        PRIMARY KEY (id_categoria),
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
);

-- ---------------------------------------------------------------------
-- material: material principal de la pieza y su pureza
-- ---------------------------------------------------------------------
CREATE TABLE material (
    id_material  SERIAL,
    nombre       VARCHAR(60) NOT NULL,
    pureza       VARCHAR(30) NOT NULL,
    CONSTRAINT pk_material              PRIMARY KEY (id_material),
    CONSTRAINT uq_material_nombre_pureza UNIQUE (nombre, pureza)
);

-- ---------------------------------------------------------------------
-- proveedor: empresas que surten mercancía a la joyería
-- ---------------------------------------------------------------------
CREATE TABLE proveedor (
    id_proveedor  SERIAL,
    nombre        VARCHAR(120) NOT NULL,
    nit           VARCHAR(20)  NOT NULL,
    telefono      VARCHAR(20),
    email         VARCHAR(150),
    ciudad        VARCHAR(80),
    CONSTRAINT pk_proveedor       PRIMARY KEY (id_proveedor),
    CONSTRAINT uq_proveedor_nit   UNIQUE (nit),
    CONSTRAINT uq_proveedor_email UNIQUE (email),
    CONSTRAINT chk_proveedor_email CHECK (email LIKE '%@%')
);

-- ---------------------------------------------------------------------
-- cliente: compradores y personas que piden préstamos (empeños)
-- ---------------------------------------------------------------------
CREATE TABLE cliente (
    id_cliente      SERIAL,
    documento       VARCHAR(20)  NOT NULL,
    nombre          VARCHAR(120) NOT NULL,
    telefono        VARCHAR(20),
    email           VARCHAR(150),
    es_vip          BOOLEAN      NOT NULL DEFAULT FALSE,
    fecha_registro  DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_cliente           PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cliente_documento UNIQUE (documento),
    CONSTRAINT uq_cliente_email     UNIQUE (email),
    CONSTRAINT chk_cliente_email    CHECK (email LIKE '%@%')
);

-- ---------------------------------------------------------------------
-- empleado: personal que atiende ventas, compras y empeños
-- ---------------------------------------------------------------------
CREATE TABLE empleado (
    id_empleado  SERIAL,
    nombre       VARCHAR(120) NOT NULL,
    cargo        VARCHAR(30)  NOT NULL,
    email        VARCHAR(150) NOT NULL,
    activo       BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT pk_empleado       PRIMARY KEY (id_empleado),
    CONSTRAINT uq_empleado_email UNIQUE (email),
    CONSTRAINT chk_empleado_email CHECK (email LIKE '%@%'),
    CONSTRAINT chk_empleado_cargo CHECK (cargo IN ('VENDEDOR', 'ADMINISTRADOR', 'AVALUADOR'))
);