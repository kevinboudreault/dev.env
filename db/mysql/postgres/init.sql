CREATE TABLE IF NOT EXISTS ROLE (
    id INT PRIMARY KEY,
    name VARCHAR(200),
    uuid UUID NOT NULL
);

CREATE TABLE IF NOT EXISTS USER (
    id INT PRIMARY KEY,
    uuid UUID NOT NULL,
    name VARCHAR(200),
    email VARCHAR(320),
    UNIQUE(uuid)
);

CREATE TABLE IF NOT EXISTS USER_ROLE (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id VARCHAR(30)
);

INSERT INTO ROLE (id,name) VALUES (0,'USER'),(1,'ADMIN');
INSERT INTO USER (id,name,email) VALUES (0,'Base User','base@email.com'),(1,'Base Admin','admin@email.com');
INSERT INTO USER_ROLE (user_id,role_id) VALUES (0,'0'),(1,'0,1');