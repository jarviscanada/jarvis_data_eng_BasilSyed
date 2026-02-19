# Introduction

This project is a hands-on SQL learning activity focused on building core RDBMS skills by writing and running real queries against a small club-style database. The product is a set of SQL solutions that create tables, insert and update data, and answer common reporting questions using joins, filters, grouping, window functions, and CTEs. The primary users are developers, data engineers, and analysts who need practical SQL practice for work. The work is designed to be executed in a PostgreSQL environment (schema `cd`) and tracked using Git for version control. 

# SQL Queries

###### Table Setup (DDL)

```sql
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
````

###### Question 1: Insert a new facility (explicit values)

```sql
INSERT INTO cd.facilities
	(facid,name,membercost,guestcost,initialoutlay,monthlymaintenance)
	VALUES (9,'Spa',20,30,100000,800);
```

###### Question 2: Insert a new facility (next facid using max)

```sql
INSERT INTO cd.facilities
    (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
    SELECT (SELECT max(facid) from cd.facilities)+1, 'Spa', 20, 30, 100000, 800; -- BAD DESIGN COULD LEAD TO RACE CONDITION,better to use SERIAL
```

###### Question 3: Update initial outlay for Tennis Court 2

```sql
UPDATE cd.facilities
	SET initialoutlay = 10000
	WHERE name='Tennis Court 2';
```

###### Question 4: Increase Tennis Court 2 costs by 10% of Tennis Court 1

```sql
UPDATE cd.facilities
	SET
		membercost=(SELECT membercost FROM cd.facilities WHERE name='Tennis Court 1')*1.1,
		guestcost=(SELECT guestcost FROM cd.facilities WHERE name='Tennis Court 1')*1.1
	WHERE name = 'Tennis Court 2';
```

###### Question 5: Remove all bookings (truncate)

```sql
TRUNCATE cd.bookings;
```

###### Question 6: Delete member with memid = 37

```sql
DELETE FROM cd.members WHERE memid=37;
```

###### Question 7: Facilities with membercost > 0 and < monthlymaintenance/50

```sql
SELECT facid, name, membercost, monthlymaintenance
FROM cd.facilities
WHERE membercost > 0 AND membercost < monthlymaintenance/50;
```

###### Question 8: Find facilities with "Tennis" in the name

```sql
SELECT *
FROM cd.facilities
WHERE name LIKE '%Tennis%';
```

###### Question 9: Find facilities with facid 1 or 5

```sql
SELECT *
FROM cd.facilities
WHERE facid IN (1,5); -- Can also use OR operator
```

###### Question 10: Members who joined on or after 2012-09-01

```sql
SELECT memid, surname, firstname, joindate
FROM cd.members
WHERE joindate >= '2012-09-01';
```

###### Question 11: List all surnames and facility names (union)

```sql
SELECT surname FROM cd.members
UNION
SELECT name FROM cd.facilities;
```

###### Question 12: Start times for bookings by David Farrell

```sql
SELECT starttime
FROM cd.bookings
JOIN cd.members ON cd.bookings.memid = cd.members.memid
WHERE surname = 'Farrell' AND firstname = 'David';
```

###### Question 13: Tennis bookings on 2012-09-21

```sql
SELECT starttime, name
FROM cd.bookings
JOIN cd.facilities ON cd.bookings.facid = cd.facilities.facid
WHERE name LIKE 'Tennis%'
  AND starttime >= '2012-09-21'
  AND starttime < '2012-09-22'
ORDER BY starttime ASC;
```

###### Question 14: Members and their recommenders (left join)

```sql
SELECT
	mems.firstname AS memfname,
	mems.surname AS memsname,
	recs.firstname AS recfname,
	recs.surname AS recsname
FROM cd.members mems
LEFT OUTER JOIN cd.members recs
	ON recs.memid = mems.recommendedby
ORDER BY memsname, memfname;
```

###### Question 15: Members who have recommended someone

```sql
SELECT DISTINCT mems.firstname AS memfname, mems.surname AS memsname
FROM cd.members mems
JOIN cd.members recs
	ON recs.recommendedby = mems.memid
ORDER BY memsname, memfname;
```

###### Question 16: Member full name and recommender full name (subquery)

```sql
SELECT DISTINCT
  CONCAT(m.firstname, ' ', m.surname) AS member,
  (
    SELECT CONCAT(r.firstname, ' ', r.surname)
    FROM cd.members r
    WHERE r.memid = m.recommendedby
  ) AS recommender
FROM cd.members m
ORDER BY member;
```

###### Question 17: Count how many recommendations each member made

```sql
SELECT recommendedby, COUNT(recommendedby) AS count
FROM cd.members
WHERE recommendedby IS NOT NULL
GROUP BY recommendedby
ORDER BY recommendedby ASC;
```

###### Question 18: Total slots booked per facility

```sql
SELECT facid, SUM(slots) as "Total Slots"
FROM cd.bookings
GROUP BY facid
ORDER BY facid;
```

###### Question 19: Total slots booked per facility in September 2012

```sql
SELECT facid, SUM(slots) as "Total Slots"
FROM cd.bookings
WHERE starttime >= '2012-09-01' AND starttime < '2012-10-01'
GROUP BY facid
ORDER BY "Total Slots";
```

###### Question 20: Total slots booked per facility per month in 2012

```sql
SELECT
	facid,
	EXTRACT(MONTH FROM starttime) AS month,
	SUM(slots) as "Total Slots"
FROM cd.bookings
WHERE starttime >= '2012-01-01' AND starttime < '2013-01-01'
GROUP BY facid, month
ORDER BY facid, month;
```

###### Question 21: Count of distinct members who made bookings

```sql
SELECT COUNT(DISTINCT memid)
FROM cd.bookings;
```

###### Question 22: First booking after 2012-09-01 for each member (DISTINCT ON)

```sql
SELECT DISTINCT ON (cd.members.memid)
	surname,
	firstname,
	cd.members.memid,
	cd.bookings.starttime
FROM cd.members
JOIN cd.bookings ON cd.members.memid = cd.bookings.memid
WHERE cd.bookings.starttime > '2012-09-01'
ORDER BY memid, cd.bookings.starttime;
```

###### Question 23: Add total row count using a window function

```sql
SELECT count(*) over(), firstname, surname
FROM cd.members
ORDER BY joindate ASC;
```

###### Question 24: Row number ordered by join date

```sql
SELECT row_number() over(order by joindate), firstname, surname
FROM cd.members
ORDER BY joindate;
```

###### Question 25: Facility with the highest total slots (CTE + rank)

```sql
WITH x AS (
	SELECT facid, SUM(slots) AS total, rank() over(ORDER BY SUM(slots) DESC)
	FROM cd.bookings
	GROUP BY facid
)
SELECT facid, total
FROM x
WHERE rank = 1;
```

###### Question 26: Format member name as "surname, firstname"

```sql
SELECT CONCAT(surname,', ',firstname)
FROM cd.members;
```

###### Question 27: Members with a phone number containing parentheses

```sql
SELECT memid, telephone
FROM cd.members
WHERE telephone LIKE '%(%)%';
```

###### Question 28: Count members grouped by first letter of surname

```sql
SELECT SUBSTR(surname,1,1) as letter, count(*) as count
FROM cd.members
GROUP BY letter
ORDER BY letter;
```

EOF

