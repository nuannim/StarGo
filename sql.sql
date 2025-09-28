insert into app_users (username, password, role, created_at) VALUES
('user1', '12345', 'user', now()),
('user2', '12345', 'user', now());

INSERT INTO app_places (name, googlemaplink, address, imageurl, created_at, addby_users_id) VALUES
('Mega Bangna', '', '38/1-3 39 หมู่ที่ 6 ทางคู่ขนาน ถนนบางนา-ตราด ตำบล บางแก้ว อำเภอบางพลี สมุทรปราการ 10540', null, now(), 2),
('Ratwinit Bangkaeo', '', '31 หมู่ 13 ซอย เมืองแก้ว 4 ตำบล บางแก้ว อำเภอบางพลี สมุทรปราการ 10540', null, now(), 2);

insert into app_celebrities (firstname, lastname, nickname, imageurl, created_at, addby_users_id) VALUES
('testceleb1', 'testceleb1', 'celeb1', null, now(), 2),
('testceleb2', 'testceleb2', 'celeb2', null, now(), 2);

SELECT setval(
  pg_get_serial_sequence('app_users', 'id'),
  COALESCE((SELECT MAX(id) FROM app_users), 1),
  true
);


SELECT setval(
  pg_get_serial_sequence('app_places', 'id'),
  COALESCE((SELECT MAX(id) FROM app_places), 1),
  true
);
