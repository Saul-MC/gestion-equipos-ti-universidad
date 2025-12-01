-- Script de datos ficticios para pruebas
-- Ejecutar: docker compose exec postgres psql -U postgres -d it_assets -f /app/db/seed_data.sql

-- Limpiar datos existentes (opcional, comentar si quieres conservar datos)
-- TRUNCATE TABLE maintenance_logs, equipment_movements, maintenance_tasks, supplier_contracts, equipment, suppliers, users CASCADE;

-- 0. Insertar Usuarios (contraseñas en texto plano para pruebas: admin123, tecnico123, usuario123)
-- En producción usar bcrypt o similar
INSERT INTO users (id, username, password_hash, full_name, role, email, is_active, created_at) VALUES
('110e8400-e29b-41d4-a716-446655440001', 'admin', 'admin123', 'Administrador del Sistema', 'admin', 'admin@universidad.edu.pe', TRUE, NOW()),
('110e8400-e29b-41d4-a716-446655440002', 'tecnico', 'tecnico123', 'Técnico de TI', 'technician', 'tecnico@universidad.edu.pe', TRUE, NOW()),
('110e8400-e29b-41d4-a716-446655440003', 'usuario', 'usuario123', 'Usuario General', 'user', 'usuario@universidad.edu.pe', TRUE, NOW())
ON CONFLICT (username) DO NOTHING;

-- 1. Insertar Proveedores
INSERT INTO suppliers (id, name, contact_email, phone, category, address, created_at) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'TechSolutions S.A.', 'contacto@techsolutions.com', '+51 987 654 321', 'Hardware', 'Av. Principal 123, Lima', NOW()),
('550e8400-e29b-41d4-a716-446655440002', 'Dell Technologies Perú', 'ventas@dell.pe', '+51 987 654 322', 'Hardware', 'Av. Javier Prado 456, San Isidro', NOW()),
('550e8400-e29b-41d4-a716-446655440003', 'HP Enterprise', 'info@hpenterprise.pe', '+51 987 654 323', 'Hardware', 'Calle Las Begonias 789, Surco', NOW()),
('550e8400-e29b-41d4-a716-446655440004', 'Cisco Systems', 'cisco@cisco.pe', '+51 987 654 324', 'Redes', 'Av. República de Panamá 321', NOW()),
('550e8400-e29b-41d4-a716-446655440005', 'Microsoft Perú', 'licencias@microsoft.pe', '+51 987 654 325', 'Software', 'Torre Real, Av. Canaval y Moreyra', NOW())
ON CONFLICT (id) DO NOTHING;

-- 2. Insertar Contratos
INSERT INTO supplier_contracts (id, supplier_id, contract_number, start_date, end_date, amount, description, created_at) VALUES
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'CON-2024-001', '2024-01-15', '2025-01-14', 50000.00, 'Contrato anual de suministro de laptops', NOW()),
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'CON-2024-002', '2024-02-01', '2025-01-31', 75000.00, 'Servidores y equipos de cómputo', NOW()),
('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 'CON-2024-003', '2024-03-10', '2025-03-09', 30000.00, 'Impresoras y periféricos', NOW()),
('660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440004', 'CON-2024-004', '2024-01-20', '2026-01-19', 120000.00, 'Equipos de red y switches', NOW()),
('660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440005', 'CON-2024-005', '2024-04-01', '2025-03-31', 45000.00, 'Licencias de software Microsoft', NOW())
ON CONFLICT (id) DO NOTHING;

-- 3. Insertar Equipos
INSERT INTO equipment (id, asset_tag, name, type, model, serial_number, purchase_date, cost, location, status, supplier_id, useful_life_years, created_at) VALUES
('770e8400-e29b-41d4-a716-446655440001', 'LAP-001', 'Laptop Dell Latitude 5520', 'Laptop', 'Latitude 5520', 'DL123456789', '2023-01-15', 1200.00, 'Facultad de Ingeniería - Lab 1', 'operational', '550e8400-e29b-41d4-a716-446655440002', 5, NOW()),
('770e8400-e29b-41d4-a716-446655440002', 'LAP-002', 'Laptop HP EliteBook 850', 'Laptop', 'EliteBook 850', 'HP987654321', '2023-02-20', 1100.00, 'Facultad de Ciencias - Oficina 201', 'operational', '550e8400-e29b-41d4-a716-446655440003', 5, NOW()),
('770e8400-e29b-41d4-a716-446655440003', 'SRV-001', 'Servidor Dell PowerEdge R740', 'Servidor', 'PowerEdge R740', 'DELL-SRV-001', '2022-06-10', 8500.00, 'Centro de Datos - Rack A1', 'operational', '550e8400-e29b-41d4-a716-446655440002', 7, NOW()),
('770e8400-e29b-41d4-a716-446655440004', 'SRV-002', 'Servidor HP ProLiant DL380', 'Servidor', 'ProLiant DL380', 'HP-SRV-002', '2022-08-15', 7200.00, 'Centro de Datos - Rack A2', 'operational', '550e8400-e29b-41d4-a716-446655440003', 7, NOW()),
('770e8400-e29b-41d4-a716-446655440005', 'SW-001', 'Switch Cisco Catalyst 2960', 'Switch', 'Catalyst 2960', 'CISCO-SW-001', '2023-03-05', 1500.00, 'Facultad de Ingeniería - Sala de Redes', 'operational', '550e8400-e29b-41d4-a716-446655440004', 6, NOW()),
('770e8400-e29b-41d4-a716-446655440006', 'SW-002', 'Switch HP Aruba 2530', 'Switch', 'Aruba 2530', 'HP-SW-002', '2023-04-12', 1300.00, 'Facultad de Ciencias - Sala de Redes', 'operational', '550e8400-e29b-41d4-a716-446655440003', 6, NOW()),
('770e8400-e29b-41d4-a716-446655440007', 'LAP-003', 'Laptop Dell Inspiron 15', 'Laptop', 'Inspiron 15', 'DL555666777', '2021-11-20', 800.00, 'Facultad de Educación - Lab 2', 'maintenance', '550e8400-e29b-41d4-a716-446655440002', 5, NOW()),
('770e8400-e29b-41d4-a716-446655440008', 'LAP-004', 'Laptop HP Pavilion', 'Laptop', 'Pavilion 15', 'HP111222333', '2020-05-10', 700.00, 'Almacén General', 'retired', '550e8400-e29b-41d4-a716-446655440003', 5, NOW()),
('770e8400-e29b-41d4-a716-446655440009', 'PRT-001', 'Impresora HP LaserJet Pro', 'Impresora', 'LaserJet Pro M404', 'HP-PRT-001', '2023-01-30', 350.00, 'Facultad de Ingeniería - Oficina Admin', 'operational', '550e8400-e29b-41d4-a716-446655440003', 4, NOW()),
('770e8400-e29b-41d4-a716-446655440010', 'PRT-002', 'Impresora Canon PIXMA', 'Impresora', 'PIXMA TR8620', 'CANON-001', '2022-12-05', 280.00, 'Facultad de Ciencias - Secretaría', 'operational', '550e8400-e29b-41d4-a716-446655440001', 4, NOW()),
('770e8400-e29b-41d4-a716-446655440011', 'LAP-005', 'Laptop Lenovo ThinkPad', 'Laptop', 'ThinkPad E14', 'LEN-001', '2019-03-15', 900.00, 'Almacén General', 'obsolete', '550e8400-e29b-41d4-a716-446655440001', 5, NOW()),
('770e8400-e29b-41d4-a716-446655440012', 'SRV-003', 'Servidor Dell PowerEdge R630', 'Servidor', 'PowerEdge R630', 'DELL-SRV-003', '2018-09-20', 6000.00, 'Centro de Datos - Rack B1', 'maintenance', '550e8400-e29b-41d4-a716-446655440002', 7, NOW())
ON CONFLICT (id) DO NOTHING;

-- 4. Insertar Movimientos de Equipos
INSERT INTO equipment_movements (id, equipment_id, from_location, to_location, assigned_to, notes, moved_at) VALUES
('880e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001', 'Almacén General', 'Facultad de Ingeniería - Lab 1', 'Dr. Juan Pérez', 'Asignación inicial para laboratorio de cómputo', '2023-01-20 10:00:00'),
('880e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440002', 'Almacén General', 'Facultad de Ciencias - Oficina 201', 'Dra. María García', 'Asignación para investigación', '2023-02-25 14:30:00'),
('880e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440001', 'Facultad de Ingeniería - Lab 1', 'Facultad de Ingeniería - Lab 2', 'Ing. Carlos López', 'Reubicación por renovación de laboratorio', '2023-11-10 09:15:00'),
('880e8400-e29b-41d4-a716-446655440004', '770e8400-e29b-41d4-a716-446655440005', 'Almacén General', 'Facultad de Ingeniería - Sala de Redes', 'Ing. Roberto Silva', 'Instalación de nueva infraestructura de red', '2023-03-10 11:00:00'),
('880e8400-e29b-41d4-a716-446655440005', '770e8400-e29b-41d4-a716-446655440007', 'Facultad de Educación - Lab 2', 'Taller de Mantenimiento', 'Técnico José Martínez', 'Enviado para reparación de pantalla', '2024-01-15 08:00:00')
ON CONFLICT (id) DO NOTHING;

-- 5. Insertar Tareas de Mantenimiento
INSERT INTO maintenance_tasks (id, equipment_id, scheduled_for, type, priority, status, assigned_team, created_at) VALUES
('990e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001', CURRENT_DATE + INTERVAL '5 days', 'preventive', 'medium', 'pending', 'Equipo de Mantenimiento TI', NOW()),
('990e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440003', CURRENT_DATE + INTERVAL '10 days', 'preventive', 'high', 'pending', 'Equipo de Servidores', NOW()),
('990e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440005', CURRENT_DATE + INTERVAL '3 days', 'preventive', 'medium', 'pending', 'Equipo de Redes', NOW()),
('990e8400-e29b-41d4-a716-446655440004', '770e8400-e29b-41d4-a716-446655440007', CURRENT_DATE - INTERVAL '2 days', 'corrective', 'high', 'completed', 'Taller de Reparaciones', NOW()),
('990e8400-e29b-41d4-a716-446655440005', '770e8400-e29b-41d4-a716-446655440009', CURRENT_DATE + INTERVAL '7 days', 'preventive', 'low', 'pending', 'Equipo de Periféricos', NOW()),
('990e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440012', CURRENT_DATE + INTERVAL '15 days', 'preventive', 'high', 'pending', 'Equipo de Servidores', NOW()),
('990e8400-e29b-41d4-a716-446655440007', '770e8400-e29b-41d4-a716-446655440002', CURRENT_DATE + INTERVAL '1 day', 'preventive', 'medium', 'pending', 'Equipo de Mantenimiento TI', NOW()),
('990e8400-e29b-41d4-a716-446655440008', '770e8400-e29b-41d4-a716-446655440004', CURRENT_DATE + INTERVAL '20 days', 'preventive', 'medium', 'pending', 'Equipo de Servidores', NOW())
ON CONFLICT (id) DO NOTHING;

-- 6. Insertar Bitácoras de Mantenimiento
INSERT INTO maintenance_logs (id, task_id, completed_on, action_taken, cost, notes, created_at) VALUES
('aa0e8400-e29b-41d4-a716-446655440001', '990e8400-e29b-41d4-a716-446655440004', CURRENT_DATE - INTERVAL '2 days', 'Reemplazo de pantalla LCD, limpieza interna, actualización de drivers', 250.00, 'Reparación exitosa, equipo funcionando correctamente', NOW()),
('aa0e8400-e29b-41d4-a716-446655440002', '990e8400-e29b-41d4-a716-446655440001', CURRENT_DATE - INTERVAL '30 days', 'Limpieza de ventiladores, actualización de BIOS, verificación de componentes', 50.00, 'Mantenimiento preventivo rutinario', NOW() - INTERVAL '30 days'),
('aa0e8400-e29b-41d4-a716-446655440003', '990e8400-e29b-41d4-a716-446655440003', CURRENT_DATE - INTERVAL '60 days', 'Actualización de firmware, verificación de puertos, limpieza de polvo', 80.00, 'Switch funcionando óptimamente', NOW() - INTERVAL '60 days'),
('aa0e8400-e29b-41d4-a716-446655440004', '990e8400-e29b-41d4-a716-446655440002', CURRENT_DATE - INTERVAL '90 days', 'Reemplazo de discos duros, actualización de RAM, verificación de redundancia', 1200.00, 'Servidor actualizado y optimizado', NOW() - INTERVAL '90 days')
ON CONFLICT (id) DO NOTHING;

-- Verificar datos insertados
SELECT 'Usuarios:' as tabla, COUNT(*) as total FROM users
UNION ALL
SELECT 'Proveedores:', COUNT(*) FROM suppliers
UNION ALL
SELECT 'Contratos:', COUNT(*) FROM supplier_contracts
UNION ALL
SELECT 'Equipos:', COUNT(*) FROM equipment
UNION ALL
SELECT 'Movimientos:', COUNT(*) FROM equipment_movements
UNION ALL
SELECT 'Tareas mantenimiento:', COUNT(*) FROM maintenance_tasks
UNION ALL
SELECT 'Bitácoras mantenimiento:', COUNT(*) FROM maintenance_logs;

