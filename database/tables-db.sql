CREATE DATABASE IF NOT EXISTS MeteoV6;
USE MeteoV6;

CREATE TABLE Tari (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nume_tara VARCHAR(255) UNIQUE NOT NULL,
    latitudine FLOAT NOT NULL,
    longitudine FLOAT NOT NULL
);

CREATE TABLE Orase (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_tara INT,
    nume_oras VARCHAR(255) NOT NULL,
    latitudine FLOAT NOT NULL,
    longitudine FLOAT NOT NULL,
    UNIQUE(id_tara, nume_oras),
    FOREIGN KEY (id_tara) REFERENCES Tari(id)
);

CREATE TABLE Temperaturi (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    valoare FLOAT NOT NULL,
    timestamp TIMESTAMP(6),
    id_oras INT NOT NULL,
    UNIQUE(id_oras, timestamp),
    FOREIGN KEY (id_oras) REFERENCES Orase(id)
);
