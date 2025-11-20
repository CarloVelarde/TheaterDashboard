USE theater_db;

-- Clear existing data
DELETE FROM ConcessionSales;
DELETE FROM TicketSales;
DELETE FROM Showtimes;
DELETE FROM Concessions;
DELETE FROM Customers;
DELETE FROM Movies;
DELETE FROM Distributors;
DELETE FROM Auditoriums;

-- Reset auto increment
ALTER TABLE Auditoriums AUTO_INCREMENT = 1;
ALTER TABLE Distributors AUTO_INCREMENT = 1;
ALTER TABLE Movies AUTO_INCREMENT = 1;
ALTER TABLE Customers AUTO_INCREMENT = 1;
ALTER TABLE Concessions AUTO_INCREMENT = 1;
ALTER TABLE Showtimes AUTO_INCREMENT = 1;
ALTER TABLE TicketSales AUTO_INCREMENT = 1;
ALTER TABLE ConcessionSales AUTO_INCREMENT = 1;

-- Auditoriums
INSERT INTO Auditoriums (TheaterID, ProjType, SeatCapacity) VALUES
   (1, '2D',  5),
   (2, '2D', 100),
   (3, '3D', 80),
   (4, 'IMAX', 150);

-- Distributors
INSERT INTO Distributors (DistributorID, DistributorName, DistributionFee) VALUES
   (1, 'Blockbuster Studios', 15.00),
   (2, 'Anime Forge', 12.00),
   (3, 'Pixar', 18.00),
   (4, 'Disney', 10.00);

-- Movies (mix of active, inactive, upcoming)
INSERT INTO Movies (MovieID, Title, Genre, Runtime, ReleaseDate, Price, IsActive, DistributorID) VALUES
   (1, 'Minecraft 2',           'Adventure', 120, '2025-10-01', 12.50, 1, 1),
   (2, 'Demon Slayer',          'Action',    110, '2025-09-20', 11.00, 1, 2),
   (3, 'Hunger Games',          'Drama',     130, '2025-08-15', 10.50, 0, 3),
   (4, 'Temple Run Live Action','Action',    125, '2025-12-10', 13.00, 0, 4),
   (5, 'Cozy Couch Marathon',   'Comedy',     95, '2025-11-25',  9.00, 0, 1);

-- Customers
INSERT INTO Customers (CustomerID, FName, LName, MembershipStatus) VALUES
   (1, 'Carlo',   'Velarde', 1),
   (2, 'Lauren',  'Johnson', 1),
   (3, 'Dom',     'Martinez',0),
   (4, 'Luke',    'Skyler',  0),
   (5, 'Keegan',  'Stone',   1),
   (6, 'Jenna',   'Nguyen',  0);

-- Concessions
INSERT INTO Concessions (ConcessionID, ConcessionPrice, Category) VALUES
   (1,  8.50, 'Popcorn'),
   (2,  5.00, 'Beverage'),
   (3,  6.00, 'Snack'),
   (4, 12.00, 'Meal'),
   (5,  4.50, 'Beverage');

-- Showtimes (no overlaps per auditorium)
INSERT INTO Showtimes (ShowtimeID, MovieID, TheaterID, StartTime, EndTime, Status, IsSoldOut) VALUES
   (1, 1, 1, '2025-11-20 18:00:00', '2025-11-20 20:00:00', 'Scheduled', 0),
   (2, 2, 2, '2025-11-20 19:00:00', '2025-11-20 21:00:00', 'Scheduled', 0),
   (3, 1, 1, '2025-11-20 20:30:00', '2025-11-20 22:30:00', 'Scheduled', 0),
   (4, 3, 3, '2025-11-19 17:00:00', '2025-11-19 19:00:00', 'Completed', 0),
   (5, 4, 4, '2025-12-15 18:00:00', '2025-12-15 20:30:00', 'Scheduled', 0),
   (6, 5, 2, '2025-11-25 16:00:00', '2025-11-25 18:00:00', 'Scheduled', 0);

-- TicketSales (Showtime 1 will be sold out: 5 seats, 5 tickets)
INSERT INTO TicketSales (TicketSaleID, CustomerID, ShowtimeID, TicketPrice, TimeTicketSold) VALUES
   (1, 1, 1, 12.50, '2025-11-20 10:00:00'),
   (2, 2, 1, 12.50, '2025-11-20 11:00:00'),
   (3, 3, 1, 12.50, '2025-11-20 12:00:00'),
   (4, 4, 1, 12.50, '2025-11-20 13:00:00'),
   (5, 5, 1, 12.50, '2025-11-20 14:00:00'),
   (6, 1, 2, 11.00, '2025-11-20 12:30:00'),
   (7, 2, 2, 11.00, '2025-11-20 15:45:00'),
   (8, 6, 3, 12.50, '2025-11-20 19:00:00'),
   (9, 3, 4, 10.50, '2025-11-19 13:00:00'),
   (10,4, 5, 13.00, '2025-12-10 10:00:00');

-- ConcessionSales
INSERT INTO ConcessionSales (ConcessionSaleID, CustomerID, ConcessionID, TimeConcessionSold) VALUES
   (1, 1, 1, '2025-11-20 17:30:00'),
   (2, 2, 2, '2025-11-20 17:45:00'),
   (3, 3, 1, '2025-11-20 18:10:00'),
   (4, 4, 4, '2025-11-20 18:20:00'),
   (5, 5, 3, '2025-11-19 19:00:00'),
   (6, 6, 2, '2025-11-19 19:10:00');
