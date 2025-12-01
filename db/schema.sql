CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios para autenticación
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    role VARCHAR(40) DEFAULT 'user',
    email VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE TABLE IF NOT EXISTS suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(150),
    phone VARCHAR(40),
    category VARCHAR(80),
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS supplier_contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID REFERENCES suppliers (id) ON DELETE CASCADE,
    contract_number VARCHAR(80) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    amount NUMERIC(14,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS equipment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_tag VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(150),
    type VARCHAR(80),
    model VARCHAR(120),
    serial_number VARCHAR(120),
    purchase_date DATE,
    cost NUMERIC(14,2),
    location VARCHAR(120),
    status VARCHAR(40) DEFAULT 'operational',
    useful_life_years INT DEFAULT 5,
    supplier_id UUID REFERENCES suppliers (id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS equipment_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment (id) ON DELETE CASCADE,
    from_location VARCHAR(120),
    to_location VARCHAR(120),
    assigned_to VARCHAR(120),
    notes TEXT,
    moved_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID REFERENCES equipment (id) ON DELETE CASCADE,
    scheduled_for DATE NOT NULL,
    type VARCHAR(40) CHECK (type IN ('preventive','corrective')),
    priority VARCHAR(20) CHECK (priority IN ('low','medium','high')),
    status VARCHAR(30) DEFAULT 'scheduled',
    assigned_team VARCHAR(120),
    reminder_token VARCHAR(120),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS maintenance_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES maintenance_tasks (id) ON DELETE CASCADE,
    completed_on DATE,
    action_taken TEXT,
    cost NUMERIC(14,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE VIEW equipment_health AS
SELECT
    e.id,
    e.asset_tag,
    e.location,
    e.status,
    EXTRACT(YEAR FROM age(now(), e.purchase_date)) AS age_years,
    COALESCE(SUM(l.cost),0) AS total_maintenance_cost
FROM equipment e
LEFT JOIN maintenance_tasks t ON t.equipment_id = e.id
LEFT JOIN maintenance_logs l ON l.task_id = t.id
GROUP BY e.id;

