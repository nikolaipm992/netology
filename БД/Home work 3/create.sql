-- Таблица Исполнители
CREATE TABLE Artists (
    artist_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Таблица Жанры
CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Таблица Альбомы
CREATE TABLE Albums (
    album_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    release_year INT NOT NULL
);

-- Таблица Треки
CREATE TABLE Tracks (
    track_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    duration INT NOT NULL,
    album_id INT REFERENCES Albums(album_id)
);

-- Таблица Сборники
CREATE TABLE Compilations (
    compilation_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    release_year INT NOT NULL
);

-- Связующие таблицы
CREATE TABLE ArtistGenres (
    artist_id INT REFERENCES Artists(artist_id),
    genre_id INT REFERENCES Genres(genre_id),
    PRIMARY KEY (artist_id, genre_id)
);

CREATE TABLE ArtistAlbums (
    artist_id INT REFERENCES Artists(artist_id),
    album_id INT REFERENCES Albums(album_id),
    PRIMARY KEY (artist_id, album_id)
);

CREATE TABLE CompilationTracks (
    compilation_id INT REFERENCES Compilations(compilation_id),
    track_id INT REFERENCES Tracks(track_id),
    PRIMARY KEY (compilation_id, track_id)
);