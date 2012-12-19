CREATE TABLE information (ID integer, source text, source_id text, creator text, time bigint, location text, lat decimal(10,5), lon decimal(10,5), data text);
SELECT AddGeometryColumn ('','information','geom',4326,'POINT',2);
CREATE INDEX time_idx ON information (time);
CREATE UNIQUE INDEX source_id_idx ON information (source_id);