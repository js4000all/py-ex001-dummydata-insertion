CREATE TABLE _mio (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    unixtime BIGINT NOT NULL,  -- UNIXタイムスタンプ（秒またはミリ秒）
    data33 FLOAT NULL,  
    data34 FLOAT NULL,
    data35 FLOAT NULL,
    data36 FLOAT NULL,
    data37 FLOAT NULL,
    data38 FLOAT NULL,
    data39 FLOAT NULL,
    data40 FLOAT NULL,
    data41 FLOAT NULL,
    data42 FLOAT NULL,
    data43 FLOAT NULL,
    data44 FLOAT NULL,
    data45 FLOAT NULL,
    data46 FLOAT NULL,
    data47 FLOAT NULL,
    data48 FLOAT NULL,
    data49 FLOAT NULL,
    data50 FLOAT NULL,
    data51 FLOAT NULL,
    data52 FLOAT NULL,
    data53 FLOAT NULL,
    data54 FLOAT NULL,
    data55 FLOAT NULL,
    data56 FLOAT NULL,
    data57 FLOAT NULL,
    data58 FLOAT NULL,
    data59 FLOAT NULL,
    data60 FLOAT NULL,
    data61 FLOAT NULL,
    data62 FLOAT NULL,
    data63 FLOAT NULL,
    data64 FLOAT NULL,
    data65 FLOAT NULL,
    data66 FLOAT NULL,
    data67 FLOAT NULL,
    data68 FLOAT NULL,
    data69 FLOAT NULL,
    data70 FLOAT NULL,
    data71 FLOAT NULL,
    data72 FLOAT NULL,
    data73 FLOAT NULL,
    data74 FLOAT NULL,
    data75 FLOAT NULL,
    data76 FLOAT NULL,
    data77 FLOAT NULL,
    data78 FLOAT NULL,
    data79 FLOAT NULL,
    data80 FLOAT NULL,
    data81 FLOAT NULL,
    data82 FLOAT NULL,
    data83 FLOAT NULL,
    INDEX idx_unixtime (unixtime)
) ENGINE=InnoDB;
---
CREATE TABLE _mer (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    unixtime BIGINT NOT NULL,  -- UNIXタイムスタンプ（秒またはミリ秒）
    data01 FLOAT NULL,  
    data02 FLOAT NULL,
    data03 FLOAT NULL,
    data04 FLOAT NULL,
    data05 FLOAT NULL,
    data06 FLOAT NULL,
    data07 FLOAT NULL,
    data08 FLOAT NULL,
    data09 FLOAT NULL,
    data10 FLOAT NULL,
    data11 FLOAT NULL,
    data12 FLOAT NULL,
    data13 FLOAT NULL,
    data14 FLOAT NULL,
    data15 FLOAT NULL,
    data16 FLOAT NULL,
    data17 FLOAT NULL,
    data18 FLOAT NULL,
    data19 FLOAT NULL,
    data20 FLOAT NULL,
    data21 FLOAT NULL,
    data22 FLOAT NULL,
    data23 FLOAT NULL,
    data24 FLOAT NULL,
    data25 FLOAT NULL,
    data26 FLOAT NULL,
    data27 FLOAT NULL,
    data28 FLOAT NULL,
    data29 FLOAT NULL,
    data30 FLOAT NULL,
    data31 FLOAT NULL,
    data32 FLOAT NULL,
    data33 FLOAT NULL,
    data34 FLOAT NULL,
    data35 FLOAT NULL,
    data36 FLOAT NULL,
    data37 FLOAT NULL,
    data38 FLOAT NULL,
    data39 FLOAT NULL,
    data40 FLOAT NULL,
    data41 FLOAT NULL,
    data42 FLOAT NULL,
    data43 FLOAT NULL,
    data44 FLOAT NULL,
    data45 FLOAT NULL,
    data46 FLOAT NULL,
    data47 FLOAT NULL,
    data48 FLOAT NULL,
    data49 FLOAT NULL,
    data50 FLOAT NULL,
    data51 FLOAT NULL,
    data52 FLOAT NULL,
    data53 FLOAT NULL,
    data54 FLOAT NULL,
    data55 FLOAT NULL,
    data56 FLOAT NULL,
    INDEX idx_unixtime (unixtime)
) ENGINE=InnoDB;
---

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
    

