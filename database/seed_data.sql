-- Demo data: 20 beds across 5 categories + 2 sample patients.
-- Loaded by database/init_db.py right after schema.sql.

INSERT INTO beds (bed_id, ward, type, status) VALUES
 ('ICU-01', 'ICU Wing',        'ICU',       'AVAILABLE'),
 ('ICU-02', 'ICU Wing',        'ICU',       'AVAILABLE'),
 ('ICU-03', 'ICU Wing',        'ICU',       'AVAILABLE'),
 ('ICU-04', 'ICU Wing',        'ICU',       'MAINTENANCE'),
 ('GEN-01', 'General Ward A',  'GENERAL',   'AVAILABLE'),
 ('GEN-02', 'General Ward A',  'GENERAL',   'AVAILABLE'),
 ('GEN-03', 'General Ward A',  'GENERAL',   'AVAILABLE'),
 ('GEN-04', 'General Ward B',  'GENERAL',   'AVAILABLE'),
 ('GEN-05', 'General Ward B',  'GENERAL',   'AVAILABLE'),
 ('GEN-06', 'General Ward B',  'GENERAL',   'AVAILABLE'),
 ('GEN-07', 'General Ward C',  'GENERAL',   'AVAILABLE'),
 ('GEN-08', 'General Ward C',  'GENERAL',   'AVAILABLE'),
 ('EMG-01', 'Emergency Bay',   'EMERGENCY', 'AVAILABLE'),
 ('EMG-02', 'Emergency Bay',   'EMERGENCY', 'AVAILABLE'),
 ('EMG-03', 'Emergency Bay',   'EMERGENCY', 'AVAILABLE'),
 ('EMG-04', 'Emergency Bay',   'EMERGENCY', 'AVAILABLE'),
 ('PED-01', 'Pediatric Wing',  'PEDIATRIC', 'AVAILABLE'),
 ('PED-02', 'Pediatric Wing',  'PEDIATRIC', 'AVAILABLE'),
 ('ISO-01', 'Isolation Wing',  'ISOLATION', 'AVAILABLE'),
 ('ISO-02', 'Isolation Wing',  'ISOLATION', 'AVAILABLE');

INSERT INTO patients (patient_id, name, age, gender, medical_condition, contact) VALUES
 ('PAT-1001', 'Ravi Kumar',   54, 'M', 'Cardiac monitoring', '9800000001'),
 ('PAT-1002', 'Sunita Devi',  29, 'F', 'Post-surgical recovery', '9800000002');
