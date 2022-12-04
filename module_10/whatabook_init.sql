/*
    Title: whatabook.init.sql
    Author: Patrick Loyd
    Date: 03 Dec 2022
    Description: WhatABook database initialization script.
*/

-- drop test user if exists 
DROP USER IF EXISTS 'whatabook_user'@'localhost';

-- create whatabook_user and grant them all privileges to the whatabook database 
CREATE USER 'whatabook_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'MySQL8IsGreat!';

-- grant all privileges to the whatabook database to user whatabook_user on localhost 
GRANT ALL PRIVILEGES ON whatabook.* TO'whatabook_user'@'localhost';

-- drop contstraints if they exist
ALTER TABLE wishlist DROP FOREIGN KEY fk_book;
ALTER TABLE wishlist DROP FOREIGN KEY fk_user;

-- drop tables if they exist
DROP TABLE IF EXISTS store;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS user;

/*
    Create table(s)
*/
CREATE TABLE store (
    store_id    INT             NOT NULL    AUTO_INCREMENT,
    locale      VARCHAR(500)    NOT NULL,
    PRIMARY KEY(store_id)
);

CREATE TABLE book (
    book_id     INT             NOT NULL    AUTO_INCREMENT,
    book_name   VARCHAR(200)    NOT NULL,
    author      VARCHAR(200)    NOT NULL,
    details     VARCHAR(500),
    PRIMARY KEY(book_id)
);

CREATE TABLE user (
    user_id         INT         NOT NULL    AUTO_INCREMENT,
    first_name      VARCHAR(75) NOT NULL,
    last_name       VARCHAR(75) NOT NULL,
    PRIMARY KEY(user_id) 
);

CREATE TABLE wishlist (
    wishlist_id     INT         NOT NULL    AUTO_INCREMENT,
    user_id         INT         NOT NULL,
    book_id         INT         NOT NULL,
    PRIMARY KEY (wishlist_id),
    CONSTRAINT fk_book
    FOREIGN KEY (book_id)
        REFERENCES book(book_id),
    CONSTRAINT fk_user
    FOREIGN KEY (user_id)
        REFERENCES user(user_Id)
);

/*
    insert store record 
*/
INSERT INTO store(locale)
    VALUES('1000 Galvin Rd S, Bellevue, NE 68005');

/*
    insert book records 
*/
INSERT INTO book(book_name, author, details)
    VALUES('Homeland', 'R.A.Salvatore', 'The first part of the The Dark Elf Trilogy');

INSERT INTO book(book_name, author, details)
    VALUES('Exile', 'R.A.Salvatore', 'The second part of The Dark Elf Trilogy');

INSERT INTO book(book_name, author, details)
    VALUES('Sojuorn', 'R.A.Salvatore', "The third part of The Dark Elf Trilogy");

INSERT INTO book(book_name, author)
    VALUES('The Fault in Our Stars', 'John Green');

INSERT INTO book(book_name, author)
    VALUES('The Hunger Games', 'Suzanne Collins');

INSERT INTO book(book_name, author)
    VALUES("Catching Fire", 'Suzanne Collins');

INSERT INTO book(book_name, author)
    VALUES('Mockingjay', 'Suzanne Collins');

INSERT INTO book(book_name, author)
    VALUES("Wizard's First Rule", 'Terry Goodkind');

INSERT INTO book(book_name, author)
    VALUES('Stone of Tears', 'Terry Goodkind');

/*
    insert user
*/ 
INSERT INTO user(first_name, last_name) 
    VALUES('Rick', 'Sanchez');

INSERT INTO user(first_name, last_name)
    VALUES('Morty', 'Smith');

INSERT INTO user(first_name, last_name)
    VALUES('Summer', 'Smith');

/*
    insert wishlist records 
*/
INSERT INTO wishlist(user_id, book_id) 
    VALUES (
        (SELECT user_id FROM user WHERE first_name = 'Rick'), 
        (SELECT book_id FROM book WHERE book_name = 'Sojuorn')
    );

INSERT INTO wishlist(user_id, book_id)
    VALUES (
        (SELECT user_id FROM user WHERE first_name = 'Morty'),
        (SELECT book_id FROM book WHERE book_name = 'Stone of Tears')
    );

INSERT INTO wishlist(user_id, book_id)
    VALUES (
        (SELECT user_id FROM user WHERE first_name = 'Summer'),
        (SELECT book_id FROM book WHERE book_name = 'Mockingjay')
    );
