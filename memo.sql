SELECT measurement_time AS "time", sensor_assignment_name AS "metric", measured_value AS "value" 
  FROM measurements
  LEFT JOIN s1.snesor_assignments as sa ON sensor_assignment_name = sa.name
  WHERE
    sa.controller_name = 'common'
  


SELECT 
    measurement_time,
    measured_value,
    sensor_assignment_name
FROM 
    measurements
INNER JOIN 
    sensor_assignments sa ON sensor_assignment_name = sa.name
WHERE 
    sa.controller_name = 'common';
  

with A as (
  select 
    date_format(measurement_time, '%Y-%m-%d-%H-%m') d,
    measured_value v,
    sensor_assignment_name n
  from measurements
)
select d, max(v), min(v), avg(v), count(v)
from A
group by d
;

INSERT INTO sensor_types (name, unit, measurement_type) VALUES
    ('temperature', '°C', 'CONTINUOUS'),
    ('flowrate', 'L/min', 'CONTINUOUS'),
    ('pH', 'pH', 'CONTINUOUS'),
    ('active', '', 'BINARY'),
    ('fault', '', 'BINARY')
;

INSERT INTO sensor_assignments (device_name, sensor_type_name, role, controller_name) VALUES
    ('tankA', 'temperature', 'inlet', 'common'),
    ('tankA', 'temperature', 'outlet', 'common'),
    ('tankA', 'pH', '', 'tank2'),
    ('heatpump1', 'temperature', '', 'tank1'),
    ('heatpump1', 'active', '', 'common'),
    ('heatpump1', 'fault', '', 'common'),
    ('heatpump2', 'temperature', '', 'tank2'),
    ('heatpump2', 'active', '', 'common'),
    ('heatpump2', 'fault', '', 'common'),
    ('blower1', 'active', '', 'common')
;
INSERT INTO sensor_assignments (id, device_name, sensor_type_name, role, controller_name) VALUES
(4110, 'blower1', 'fault', '', 'common')

('2025-02-03 05:20:00', 4110, 0),
insert into measurements values
('2025-02-03 05:23:00', 4110, 0)

SELECT dvc.name FROM devices dvc 
  LEFT JOIN sensor_assignments sa ON sa.device_name = dvc.name
  LEFT JOIN sensor_types sy ON sy.name = sa.sensor_type_name
WHERE sy.measurement_type = 'BINARY'

SELECT table_name, 
       ROUND(index_length/1024/1024, 2) AS "index size(MB)"
FROM information_schema.tables 
WHERE table_schema = 's1' 
  AND table_name = 'measurements';

SELECT
  m.measurement_time as 'time',
  sa.name as 'metric', 
  m.measured_value as 'value'
FROM s1.measurements m
JOIN sensor_assignments sa ON sa.id = m.sensor_assignment_id
JOIN sensor_types st ON st.name = sa.sensor_type_name
WHERE
  st.measurement_type = 'BINARY'
  AND st.name = 'fault'
  AND m.measurement_time BETWEEN '2025-02-03 02:00:00' AND '2025-02-03 03:00:00'

  select 
    DATE_FORMAT(m.measurement_time, '%Y-%m-%d') as day_,
    sa.name as metric,
    m.measured_value as value
  FROM s1.measurements m
  JOIN sensor_assignments sa ON sa.id = m.sensor_assignment_id
  JOIN sensor_types st ON st.name = sa.sensor_type_name 
  WHERE
    measurement_time BETWEEN '2025-02-03' AND '2025-02-04'
    AND st.measurement_type = 'CONTINUOUS'
    

