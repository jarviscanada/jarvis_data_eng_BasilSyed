-- Question 1)
INSERT INTO cd.facilities
	(facid,name,membercost,guestcost,initialoutlay,monthlymaintenance)
	VALUES (9,'Spa',20,30,100000,800);

-- Question 2)
INSERT INTO cd.facilities
    (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
    SELECT (SELECT max(facid) from cd.facilities)+1, 'Spa', 20, 30, 100000, 800; -- BAD DESIGN COULD LEAD TO RACE CONDITION,better to use SERIAL

-- Question 3)
UPDATE cd.facilities
	SET initialoutlay = 10000
	WHERE name='Tennis Court 2';

-- Question 4) 
UPDATE cd.facilities
	SET
		membercost=(SELECT membercost FROM cd.facilities WHERE name='Tennis Court 1')*1.1,
		guestcost=(SELECT guestcost FROM cd.facilities WHERE name='Tennis Court 1')*1.1

	WHERE name = 'Tennis Court 2';

-- Question 5) 
TRUNCATE cd.bookings;

-- Question 6) 
DELETE FROM cd.members WHERE memid=37;

-- Question 7)
SELECT facid, name, membercost, monthlymaintenance FROM cd.facilities
	WHERE membercost > 0 AND membercost < monthlymaintenance/50;

-- Question 8)
Select * FROM cd.facilities where name LIKE '%Tennis%';

-- Question 9)
SELECT * FROM cd.facilities WHERE facid IN (1,5); -- Can also use OR operator

-- Question 10)
SELECT memid, surname, firstname, joindate FROM cd.members
	WHERE joindate >= '2012-09-01';

-- Question 11)
SELECT surname FROM cd.members UNION
	SELECT name FROM cd.facilities;

-- Question 12) 
SELECT starttime FROM cd.bookings
	JOIN cd.members ON cd.bookings.memid = cd.members.memid
	WHERE surname = 'Farrell' AND firstname = 'David';

-- Question 13)
SELECT starttime, name FROM cd.bookings
	JOIN cd.facilities ON cd.bookings.facid = cd.facilities.facid
	WHERE name LIKE 'Tennis%' AND starttime >= '2012-09-21' AND starttime < '2012-09-22' 
	ORDER BY starttime ASC;

-- Question 14)
SELECT mems.firstname AS memfname, mems.surname AS memsname, recs.firstname AS recfname, recs.surname AS recsname
	FROM
		cd.members mems
		left outer JOIN cd.members recs
			ON recs.memid = mems.recommendedby
	ORDER BY memsname, memfname;

-- Question 15)
SELECT DISTINCT mems.firstname AS memfname, mems.surname AS memsname
        FROM
             	cd.members mems
                JOIN cd.members recs
                        ON recs.recommendedby = mems.memid
	ORDER BY memsname, memfname;

-- Question 16)
SELECT DISTINCT
  CONCAT(m.firstname, ' ', m.surname) AS member,
  (
    SELECT CONCAT(r.firstname, ' ', r.surname)
    FROM cd.members r
    WHERE r.memid = m.recommendedby
  ) AS recommender
FROM cd.members m
ORDER BY member;

-- Question 17)

SELECT recommendedby, COUNT(recommendedby) AS count FROM cd.members
        WHERE recommendedby IS NOT NULL
        GROUP BY recommendedby
	ORDER BY recommendedby ASC;

-- Question 18)
SELECT facid, SUM(slots) as "Total Slots" FROM cd.bookings
	GROUP BY facid
	ORDER BY facid;

-- Question 19)
SELECT facid, SUM(slots) as "Total Slots" FROM cd.bookings
	WHERE starttime >= '2012-09-01' AND starttime < '2012-10-01'
	GROUP BY facid
	ORDER BY "Total Slots";

-- Question 20)
SELECT facid, EXTRACT(MONTH FROM starttime) AS month, SUM(slots) as "Total Slots" FROM cd.bookings
        WHERE starttime >= '2012-01-01' AND starttime < '2013-01-01'
        GROUP BY facid, month
        ORDER BY facid, month;

-- Question 21) 
SELECT COUNT(DISTINCT memid) FROM cd.bookings;

-- Question 22) 
SELECT DISTINCT ON (cd.members.memid) surname, firstname, cd.members.memid, cd.bookings.starttime FROM cd.members
	JOIN cd.bookings ON cd.members.memid = cd.bookings.memid
	WHERE cd.bookings.starttime > '2012-09-01'
	ORDER BY memid, cd.bookings.starttime;

-- Question 23) 
SELECT count(*) over(),firstname, surname FROM cd.members
	ORDER BY joindate ASC;

-- Question 24)
SELECT row_number() over(order by joindate),firstname, surname FROM cd.members
	ORDER BY joindate;

-- Question 25)
WITH x AS (
	SELECT facid, SUM(slots) AS total, rank() over(ORDER BY SUM(slots) DESC)
	FROM cd.bookings
	GROUP BY facid
)

SELECT facid, total FROM x WHERE rank = 1;


-- Question 26)
SELECT CONCAT(surname,', ',firstname) FROM cd.members;

-- Question 27)
SELECT memid, telephone FROM cd.members WHERE telephone LIKE '%(%)%';

-- Question 28)
SELECT SUBSTR(surname,1,1) as letter, count(*) as count 
	FROM cd.members
	GROUP BY letter
	ORDER BY letter;
