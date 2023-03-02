DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL,
    password TEXT NOT NULL
);

INSERT INTO accounts(account,password) VALUES("ldl","123");

DROP TABLE IF EXISTS events;

CREATE TABLE events 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account TEXT NOT NULL, 
    type TEXT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL
);

DROP TABLE IF EXISTS types;

CREATE TABLE types 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL
);

INSERT INTO types(type) 
VALUES
("Other"),("Career"),("Daily"),("Health"),("Travel");