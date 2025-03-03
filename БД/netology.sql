-- Создание таблицы Жанры
CREATE TABLE Genres (
    genre_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

-- Создание таблицы Исполнители
CREATE TABLE Performers (
    performer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

-- Создание промежуточной таблицы для связи Жанры ↔ Исполнители
CREATE TABLE Performers_Genres (
    performer_id INT NOT NULL,
    genre_id INT NOT NULL,
    FOREIGN KEY (performer_id) REFERENCES Performers(performer_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),
    PRIMARY KEY (performer_id, genre_id)
);

-- Создание таблицы Альбомы
CREATE TABLE Albums (
    album_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    year INT NOT NULL
);

-- Создание промежуточной таблицы для связи Исполнители ↔ Альбомы
CREATE TABLE Performers_Albums (
    performer_id INT NOT NULL,
    album_id INT NOT NULL,
    FOREIGN KEY (performer_id) REFERENCES Performers(performer_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    PRIMARY KEY (performer_id, album_id)
);

-- Создание таблицы Треки
CREATE TABLE Tracks (
    track_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    duration TIME NOT NULL,
    album_id INT NOT NULL,
    FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);

-- Создание таблицы Сборники
CREATE TABLE Collections (
    collection_id INT PRIMARY KEY AUTO_INCREMENT,
    collection_name VARCHAR(255) NOT NULL,
    collection_year INT NOT NULL
);

-- Создание промежуточной таблицы для связи Сборники ↔ Треки
CREATE TABLE Collections_Tracks (
    collection_id INT NOT NULL,
    track_id INT NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES Collections(collection_id),
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
    PRIMARY KEY (collection_id, track_id)
);