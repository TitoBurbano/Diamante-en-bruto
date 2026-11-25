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

-- ---------------------------------------------------------------------
-- joya: pieza única del inventario. Su estado indica dónde está:
--   DISPONIBLE (a la venta), VENDIDA, EMPENADA (en garantía de un
--   préstamo) o DEVUELTA (el cliente saldó su empeño y la recuperó).
-- id_proveedor es opcional: las joyas que llegan por un empeño no
-- tienen proveedor.
-- ---------------------------------------------------------------------
CREATE TABLE joya (
    id_joya        SERIAL,
    codigo         VARCHAR(30)   NOT NULL,
    nombre         VARCHAR(120)  NOT NULL,
    id_categoria   INTEGER       NOT NULL,
    id_material    INTEGER       NOT NULL,
    id_proveedor   INTEGER,
    peso_gramos    NUMERIC(8,2)  NOT NULL,
    quilates       NUMERIC(6,2),
    precio_compra  NUMERIC(12,2) NOT NULL,
    precio_venta   NUMERIC(12,2) NOT NULL,
    estado         VARCHAR(15)   NOT NULL DEFAULT 'DISPONIBLE',
    fecha_ingreso  DATE          NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_joya        PRIMARY KEY (id_joya),
    CONSTRAINT uq_joya_codigo UNIQUE (codigo),
    CONSTRAINT chk_joya_peso          CHECK (peso_gramos > 0),
    CONSTRAINT chk_joya_quilates      CHECK (quilates IS NULL OR quilates > 0),
    CONSTRAINT chk_joya_precio_compra CHECK (precio_compra >= 0),
    CONSTRAINT chk_joya_precio_venta  CHECK (precio_venta >= 0),
    CONSTRAINT chk_joya_estado        CHECK (estado IN ('DISPONIBLE', 'VENDIDA', 'EMPENADA', 'DEVUELTA')),
    CONSTRAINT fk_joya_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria (id_categoria) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_joya_material FOREIGN KEY (id_material)
        REFERENCES material (id_material) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_joya_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedor (id_proveedor) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Acelera las consultas por estado (inventario disponible, empeñadas...).
CREATE INDEX idx_joya_estado ON joya (estado);


-- ---------------------------------------------------------------------
-- venta: cabecera de una venta de joyas a un cliente.
-- descuento es un monto en pesos (no un porcentaje).
-- Una venta ANULADA debe guardar el motivo de la anulación.
-- ---------------------------------------------------------------------
CREATE TABLE venta (
    id_venta          SERIAL,
    id_cliente        INTEGER       NOT NULL,
    id_empleado       INTEGER       NOT NULL,
    fecha             TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descuento         NUMERIC(12,2) NOT NULL DEFAULT 0,
    total             NUMERIC(12,2) NOT NULL,
    estado            VARCHAR(15)   NOT NULL DEFAULT 'COMPLETADA',
    motivo_anulacion  TEXT,
    CONSTRAINT pk_venta PRIMARY KEY (id_venta),
    CONSTRAINT chk_venta_descuento CHECK (descuento >= 0),
    CONSTRAINT chk_venta_total     CHECK (total >= 0),
    CONSTRAINT chk_venta_estado    CHECK (estado IN ('COMPLETADA', 'ANULADA')),
    CONSTRAINT chk_venta_motivo    CHECK (estado <> 'ANULADA' OR motivo_anulacion IS NOT NULL),
    CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_venta_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- detalle_venta: tabla intermedia N:M entre venta y joya.
-- Guarda el precio al que se vendió cada pieza en ese momento.
-- ---------------------------------------------------------------------
CREATE TABLE detalle_venta (
    id_detalle_venta  SERIAL,
    id_venta          INTEGER       NOT NULL,
    id_joya           INTEGER       NOT NULL,
    precio_unitario   NUMERIC(12,2) NOT NULL,
    CONSTRAINT pk_detalle_venta PRIMARY KEY (id_detalle_venta),
    CONSTRAINT uq_detalle_venta_venta_joya UNIQUE (id_venta, id_joya),
    CONSTRAINT chk_detalle_venta_precio CHECK (precio_unitario >= 0),
    CONSTRAINT fk_detalle_venta_venta FOREIGN KEY (id_venta)
        REFERENCES venta (id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_venta_joya FOREIGN KEY (id_joya)
        REFERENCES joya (id_joya) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- orden_compra: mercancía recibida de un proveedor.
-- ---------------------------------------------------------------------
CREATE TABLE orden_compra (
    id_orden      SERIAL,
    id_proveedor  INTEGER       NOT NULL,
    id_empleado   INTEGER       NOT NULL,
    fecha         DATE          NOT NULL DEFAULT CURRENT_DATE,
    total         NUMERIC(12,2) NOT NULL,
    CONSTRAINT pk_orden_compra PRIMARY KEY (id_orden),
    CONSTRAINT chk_orden_compra_total CHECK (total >= 0),
    CONSTRAINT fk_orden_compra_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedor (id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orden_compra_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- detalle_orden_compra: joyas recibidas en cada orden y su costo.
-- Una joya llega en una sola orden (uq_detalle_orden_joya).
-- ---------------------------------------------------------------------
CREATE TABLE detalle_orden_compra (
    id_detalle_orden  SERIAL,
    id_orden          INTEGER       NOT NULL,
    id_joya           INTEGER       NOT NULL,
    costo             NUMERIC(12,2) NOT NULL,
    CONSTRAINT pk_detalle_orden_compra PRIMARY KEY (id_detalle_orden),
    CONSTRAINT uq_detalle_orden_joya   UNIQUE (id_joya),
    CONSTRAINT chk_detalle_orden_costo CHECK (costo >= 0),
    CONSTRAINT fk_detalle_orden_orden FOREIGN KEY (id_orden)
        REFERENCES orden_compra (id_orden) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_orden_joya FOREIGN KEY (id_joya)
        REFERENCES joya (id_joya) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- empeno: préstamo de dinero con una joya como garantía.
--   tasa_interes: porcentaje mensual.
--   ACTIVO  -> vigente, sin fecha de cierre.
--   SALDADO -> el cliente pagó (monto_pagado obligatorio).
--   VENCIDO -> no pagó a tiempo; la joya pasa a la tienda.
-- ---------------------------------------------------------------------
CREATE TABLE empeno (
    id_empeno          SERIAL,
    id_cliente         INTEGER       NOT NULL,
    id_joya            INTEGER       NOT NULL,
    id_empleado        INTEGER       NOT NULL,
    monto_prestamo     NUMERIC(12,2) NOT NULL,
    tasa_interes       NUMERIC(5,2)  NOT NULL DEFAULT 5.00,
    fecha_inicio       DATE          NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento  DATE          NOT NULL,
    estado             VARCHAR(15)   NOT NULL DEFAULT 'ACTIVO',
    fecha_cierre       DATE,
    monto_pagado       NUMERIC(12,2),
    CONSTRAINT pk_empeno PRIMARY KEY (id_empeno),
    CONSTRAINT chk_empeno_monto   CHECK (monto_prestamo > 0),
    CONSTRAINT chk_empeno_tasa    CHECK (tasa_interes >= 0 AND tasa_interes <= 100),
    CONSTRAINT chk_empeno_fechas  CHECK (fecha_vencimiento > fecha_inicio),
    CONSTRAINT chk_empeno_estado  CHECK (estado IN ('ACTIVO', 'SALDADO', 'VENCIDO')),
    CONSTRAINT chk_empeno_cierre  CHECK (
        (estado = 'ACTIVO'  AND fecha_cierre IS NULL) OR
        (estado <> 'ACTIVO' AND fecha_cierre IS NOT NULL)),
    CONSTRAINT chk_empeno_pago    CHECK (estado <> 'SALDADO' OR monto_pagado IS NOT NULL),
    CONSTRAINT chk_empeno_pagado  CHECK (monto_pagado IS NULL OR monto_pagado >= 0),
    CONSTRAINT fk_empeno_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_empeno_joya FOREIGN KEY (id_joya)
        REFERENCES joya (id_joya) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_empeno_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Regla: una joya no puede tener dos empeños activos al mismo tiempo.
CREATE UNIQUE INDEX uq_empeno_joya_activo ON empeno (id_joya) WHERE estado = 'ACTIVO';

-- =====================================================================
-- Resumen de decisiones ON DELETE (todas con ON UPDATE CASCADE)
--   RESTRICT : joya -> categoria, material; venta -> cliente, empleado;
--              detalle_venta -> joya; orden_compra -> proveedor, empleado;
--              detalle_orden_compra -> joya; empeno -> cliente, joya,
--              empleado. Son registros históricos o contables que no
--              deben quedar huérfanos.
--   CASCADE  : detalle_venta -> venta; detalle_orden_compra -> orden.
--              El detalle no tiene sentido sin su cabecera.
--   SET NULL : joya -> proveedor. La pieza sigue existiendo aunque se
--              elimine el proveedor que la surtió.
-- =====================================================================