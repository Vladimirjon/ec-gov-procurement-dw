-- DDL de respaldo de la estrella construida en Power BI para el Hito 3.
-- Fuentes: ADR 0004 y 0005, docs/h3/diseno-dimensional.md y
-- reports/powerbi/h3/queries/{DimTiempo,DimEntidad,DimMetodo,FactContratacion}.pq.
-- PostgreSQL probado: 17.12 (imagen oficial postgres:17.12-bookworm).
-- Reejecución: IF NOT EXISTS conserva las tablas existentes y sus filas.
-- Inicializa el esquema; los cambios a tablas existentes requieren una migración.

BEGIN;

CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_id bigint PRIMARY KEY,
    month_start date NOT NULL UNIQUE,
    year bigint NOT NULL,
    semester bigint NOT NULL,
    quarter bigint NOT NULL,
    month bigint NOT NULL,
    month_name text NOT NULL,
    year_month text NOT NULL
);

COMMENT ON TABLE dw.dim_date IS
    'Una fila por mes calendario de enero de 2021 a diciembre de 2025, con clave AAAAMM.';

-- Las claves de entidad y método corresponden a los índices del modelo H3.
CREATE TABLE IF NOT EXISTS dw.dim_entity (
    entity_id bigint PRIMARY KEY,
    ruc_root text NOT NULL UNIQUE,
    entity_name text NOT NULL,
    entity_type text NOT NULL,
    parent_entity text,
    valid_from date,
    valid_to date
);

COMMENT ON TABLE dw.dim_entity IS
    'Una fila por raíz de RUC de un comprador admitido del gobierno central, más el miembro Sin clasificar.';

CREATE TABLE IF NOT EXISTS dw.dim_method (
    method_id bigint PRIMARY KEY,
    ocds_method text NOT NULL,
    procedure text NOT NULL,
    method_name text NOT NULL,
    UNIQUE (ocds_method, procedure)
);

COMMENT ON TABLE dw.dim_method IS
    'Una fila por par de método OCDS y procedimiento normalizado, incluido el miembro Sin licitación.';

CREATE TABLE IF NOT EXISTS dw.fact_contract_process (
    date_id bigint NOT NULL,
    entity_id bigint NOT NULL,
    method_id bigint NOT NULL,
    ocid text PRIMARY KEY,
    awarded_amount numeric,
    estimated_amount numeric,
    process_count bigint NOT NULL CHECK (process_count = 1),
    award_count bigint NOT NULL CHECK (award_count >= 0),
    process_with_both_amounts bigint NOT NULL,
    FOREIGN KEY (date_id) REFERENCES dw.dim_date (date_id),
    FOREIGN KEY (entity_id) REFERENCES dw.dim_entity (entity_id),
    FOREIGN KEY (method_id) REFERENCES dw.dim_method (method_id),
    CHECK (process_with_both_amounts = CASE
        WHEN awarded_amount IS NOT NULL AND estimated_amount IS NOT NULL THEN 1
        ELSE 0
    END)
);

COMMENT ON TABLE dw.fact_contract_process IS
    'Una fila por proceso de contratación (ocid) admitido del gobierno central con fecha de release entre 2021 y 2025.';

COMMIT;
