create table person (
	id INT,
	first_name VARCHAR(50),
	last_name VARCHAR(50),
	email VARCHAR(70),
	gender VARCHAR(10),
	country_of_birth VARCHAR(20),
	car_make VARCHAR(20)
);


INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (1, 'Vikki', 'Balsillie', 'vbalsillie0@mashable.com', 'Female', 'Indonesia', 'Nissan');
INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (2, 'Lorettalorna', 'Fetteplace', 'lfetteplace2@tripod.com', 'Female', 'United Kingdom', 'Plymouth');
INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (3, 'Ileana', 'Guerin', 'iguerin3@unicef.org', 'Female', 'Bulgaria', null);
INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (4, 'Walden', 'Milmo', null, 'Male', 'Russia', 'Ford');
INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (5, 'Quincy', 'Bromont', null, 'Male', 'China', 'Lexus');
INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (6, 'Maria', 'Iddon', 'middon8@tripadvisor.com', 'Female', 'Philippines', 'Land Rover');
INSERT INTO person (id, first_name, last_name, email, gender, country_of_birth, car_make) VALUES (7, 'Rog', 'McArdell', 'rmcardell9@list-manage.com', 'Male', 'Poland', null);


WITH no_email AS (SELECT * FROM person WHERE email IS NOT NULL)
SELECT id,first_name,last_name FROM no_email;

WITH email AS (SELECT * FROM person WHERE email IS NULL),
car AS (SELECT * FROM person WHERE car_make IS NULL)
SELECT * FROM person EXCEPT
(SELECT * FROM email UNION ALL
SELECT * FROM car);

DROP TABLE person;

