CREATE TABLE IF NOT EXISTS cd.facilities (
	facid INT PRIMARY KEY,
	name varchar(100) NOT NULL,
	membercost NUMERIC NOT NULL,
	guestcost NUMERIC NOT NULL,
	initialoutlay NUMERIC NOT NULL,
	monthlymaintenance NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS cd.bookings (
	bookid INT PRIMARY KEY,
	facid INT NOT NULL REFERENCES cd.facilities(facid),
	memid INT NOT NULL REFERENCES cd.members(memid),
	starttime timestamp NOT NULL,
	slots INT NOT NULL
);


CREATE TABLE IF NOT EXISTS cd.members (
	memid INT PRIMARY KEY,
	surname VARCHAR (200) NOT NULL,
	firstname VARCHAR (200) NOT NULL,
	address varchar (300) NOT NULL,
	zipcode INT NOT NULL,
	telephone varchar (20) NOT NULL,
	recommendedby INT REFERENCES cd.members(memid) ON DELETE SET NULL,
	joindate timestamp NOT NULL
);

