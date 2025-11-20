DROP DATABASE IF EXISTS theater_db;
CREATE DATABASE theater_db;
USE theater_db;

-- ============================
-- TABLE DEFINITIONS
-- ============================

CREATE TABLE Auditoriums (
    TheaterID INT PRIMARY KEY AUTO_INCREMENT,
    ProjType VARCHAR(4) NOT NULL,
    SeatCapacity INT NOT NULL,
    CHECK (ProjType IN ('2D', '3D', 'IMAX'))
);

CREATE TABLE Distributors (
    DistributorID INT PRIMARY KEY AUTO_INCREMENT,
    DistributorName VARCHAR(100) NOT NULL,
    DistributionFee DECIMAL(6,2) NOT NULL
);

CREATE TABLE Movies (
    MovieID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(100) NOT NULL,
    Genre VARCHAR(50) NOT NULL,
    Runtime INT NOT NULL,
    ReleaseDate DATE NOT NULL,
    Price DECIMAL(6,2) NOT NULL,
    IsActive TINYINT(1) NOT NULL,
    DistributorID INT NOT NULL,
    FOREIGN KEY (DistributorID) REFERENCES Distributors(DistributorID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Showtimes (
    ShowtimeID INT PRIMARY KEY AUTO_INCREMENT,
    MovieID INT NOT NULL,
    TheaterID INT NOT NULL,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,
    Status VARCHAR(20) NOT NULL,
    IsSoldOut TINYINT(1) NOT NULL DEFAULT 0,
    CHECK (Status IN ('Scheduled', 'In Progress', 'Completed', 'Canceled')),
    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (TheaterID) REFERENCES Auditoriums(TheaterID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FName VARCHAR(50) NOT NULL,
    LName VARCHAR(50),
    MembershipStatus TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE TicketSales (
    TicketSaleID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    ShowtimeID INT NOT NULL,
    TicketPrice DECIMAL(6,2) NOT NULL,
    TimeTicketSold DATETIME NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (ShowtimeID) REFERENCES Showtimes(ShowtimeID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Concessions (
    ConcessionID INT PRIMARY KEY AUTO_INCREMENT,
    ConcessionPrice DECIMAL(6,2) NOT NULL,
    Category VARCHAR(10) NOT NULL,
    CHECK (Category IN ('Meal','Popcorn','Beverage','Snack'))
);

CREATE TABLE ConcessionSales (
    ConcessionSaleID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    ConcessionID INT NOT NULL,
    TimeConcessionSold DATETIME NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (ConcessionID) REFERENCES Concessions(ConcessionID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ============================
-- TRIGGERS
-- ============================

-- Update sold-out status
DELIMITER //
CREATE TRIGGER UpdateShowtimeStatus
AFTER INSERT ON TicketSales
FOR EACH ROW
BEGIN
    DECLARE v_Capacity INT;
    DECLARE v_Sold INT;

    SELECT A.SeatCapacity
      INTO v_Capacity
    FROM Auditoriums A
    JOIN Showtimes S ON A.TheaterID = S.TheaterID
    WHERE S.ShowtimeID = NEW.ShowtimeID;

    SELECT COUNT(*) INTO v_Sold
    FROM TicketSales
    WHERE ShowtimeID = NEW.ShowtimeID;

    IF v_Sold >= v_Capacity THEN
        UPDATE Showtimes
        SET IsSoldOut = 1
        WHERE ShowtimeID = NEW.ShowtimeID;
    END IF;
END//
DELIMITER ;

-- Prevent overlapping showtimes
DELIMITER //
CREATE TRIGGER EnforceShowtimeOverlap
BEFORE INSERT ON Showtimes
FOR EACH ROW
BEGIN
    DECLARE v_Conflict INT;

    SELECT COUNT(*)
      INTO v_Conflict
    FROM Showtimes S
    WHERE S.TheaterID = NEW.TheaterID
      AND NEW.StartTime < S.EndTime
      AND NEW.EndTime > S.StartTime;

    IF v_Conflict > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Scheduling conflict.';
    END IF;
END//
DELIMITER ;

-- Prevent invalid ticket sales
DELIMITER //
CREATE TRIGGER PreventInvalidTicketSales
BEFORE INSERT ON TicketSales
FOR EACH ROW
BEGIN
    DECLARE v_Start DATETIME;
    DECLARE v_End DATETIME;
    DECLARE v_SoldOut TINYINT(1);

    SELECT StartTime, EndTime, IsSoldOut
      INTO v_Start, v_End, v_SoldOut
    FROM Showtimes
    WHERE ShowtimeID = NEW.ShowtimeID;

    IF v_SoldOut = 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Sold out.';
    END IF;

    IF NEW.TimeTicketSold > v_End THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Show completed.';
    END IF;

    IF NEW.TimeTicketSold BETWEEN v_Start AND v_End THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Show in progress.';
    END IF;
END//
DELIMITER ;

-- ============================
-- VIEWS
-- ============================

CREATE OR REPLACE VIEW ShowtimeStatusView AS
SELECT
    s.ShowtimeID,
    s.MovieID,
    s.TheaterID,
    s.StartTime,
    s.EndTime,
    s.IsSoldOut,
    CASE
        WHEN IsSoldOut = 1 THEN 'Sold Out'
        WHEN NOW() < StartTime THEN 'Scheduled'
        WHEN NOW() BETWEEN StartTime AND EndTime THEN 'In Progress'
        WHEN NOW() > EndTime THEN 'Completed'
        ELSE 'Unknown'
    END AS DynamicStatus
FROM Showtimes s;

CREATE OR REPLACE VIEW UpcomingShowtimesView AS
SELECT
    s.ShowtimeID,
    s.MovieID,
    m.Title AS MovieTitle,
    s.TheaterID,
    s.StartTime,
    s.EndTime,
    s.IsSoldOut,
    CASE
        WHEN IsSoldOut = 1 THEN 'Sold Out'
        WHEN NOW() < StartTime THEN 'Scheduled'
        WHEN NOW() BETWEEN StartTime AND EndTime THEN 'In Progress'
        ELSE 'Unknown'
    END AS DynamicStatus
FROM Showtimes s
JOIN Movies m ON s.MovieID = m.MovieID
WHERE s.EndTime > NOW();

-- ============================
-- PROCEDURES
-- ============================

DELIMITER $$
CREATE PROCEDURE Process_Ticket_Purchase(
    IN p_CustomerID INT,
    IN p_ShowtimeID INT
)
BEGIN
    DECLARE v_Price DECIMAL(6,2);
    DECLARE v_Start DATETIME;
    DECLARE v_End DATETIME;
    DECLARE v_SoldOut TINYINT(1);
    DECLARE v_Cap INT;
    DECLARE v_Sold INT;

    SELECT s.StartTime, s.EndTime, s.IsSoldOut, m.Price
      INTO v_Start, v_End, v_SoldOut, v_Price
    FROM Showtimes s
    JOIN Movies m ON s.MovieID = m.MovieID
    WHERE s.ShowtimeID = p_ShowtimeID;

    IF v_SoldOut = 1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sold out'; END IF;
    IF NOW() > v_End THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Show completed'; END IF;
    IF NOW() BETWEEN v_Start AND v_End THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Show in progress'; END IF;

    SELECT SeatCapacity INTO v_Cap
    FROM Auditoriums a
    JOIN Showtimes s ON a.TheaterID = s.TheaterID
    WHERE s.ShowtimeID = p_ShowtimeID;

    SELECT COUNT(*) INTO v_Sold
    FROM TicketSales
    WHERE ShowtimeID = p_ShowtimeID;

    IF v_Sold >= v_Cap THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Auditorium full';
    END IF;

    INSERT INTO TicketSales(CustomerID, ShowtimeID, TicketPrice, TimeTicketSold)
    VALUES (p_CustomerID, p_ShowtimeID, v_Price, NOW());
END$$
DELIMITER ;

-- ============================
-- FUNCTIONS
-- ============================

DELIMITER $$
CREATE FUNCTION get_number_of_ticket_sales(p_Date DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_Count INT;

    SELECT COUNT(*) INTO v_Count
    FROM TicketSales
    WHERE DATE(TimeTicketSold) = p_Date;

    RETURN v_Count;
END $$
DELIMITER ;

DELIMITER $$
CREATE FUNCTION get_movie_profits(p_MovieID INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE v_Revenue DECIMAL(10,2);
    DECLARE v_Fee DECIMAL(6,2);

    SELECT IFNULL(SUM(ts.TicketPrice),0)
      INTO v_Revenue
    FROM TicketSales ts
    JOIN Showtimes s ON ts.ShowtimeID = s.ShowtimeID
    WHERE s.MovieID = p_MovieID;

    SELECT d.DistributionFee
      INTO v_Fee
    FROM Movies m
    JOIN Distributors d ON m.DistributorID = d.DistributorID
    WHERE m.MovieID = p_MovieID;

    RETURN v_Revenue - (v_Revenue * (v_Fee / 100));
END $$
DELIMITER ;

