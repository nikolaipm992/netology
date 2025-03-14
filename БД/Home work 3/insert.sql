-- Исполнители
INSERT INTO Artists (name) VALUES
('Исполнитель 1'),
('Исполнитель 2'),
('Исполнитель 3'),
('Исполнитель 4');

-- Жанры
INSERT INTO Genres (name) VALUES
('Жанр 1'),
('Жанр 2'),
('Жанр 3');

-- Альбомы
INSERT INTO Albums (name, release_year) VALUES
('Альбом 1', 2018),
('Альбом 2', 2019),
('Альбом 3', 2020);

-- Треки
INSERT INTO Tracks (name, duration, album_id) VALUES
('Трек 1', 300, 1),
('Трек 2', 250, 1),
('Трек 3', 400, 2),
('Трек 4', 200, 2),
('Трек 5', 350, 3),
('Трек 6', 500, 3),
('my own', 210, 3), -- Добавленные треки для проверки
('own my', 210, 3),
('my', 210, 3),
('oh my god', 210, 3),
('myself', 210, 3),
('by myself', 210, 3),
('bemy self', 210, 3),
('myself by', 210, 3),
('beemy', 210, 3),
('premyne', 210, 3);

-- Сборники
INSERT INTO Compilations (name, release_year) VALUES
('Сборник 1', 2018),
('Сборник 2', 2019),
('Сборник 3', 2020),
('Сборник 4', 2021);

-- Исполнители-Жанры
INSERT INTO ArtistGenres (artist_id, genre_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 1);

-- Исполнители-Альбомы
INSERT INTO ArtistAlbums (artist_id, album_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 1);

-- Сборники-Треки
INSERT INTO CompilationTracks (compilation_id, track_id) VALUES
(1, 1),
(1, 2),
(2, 3),
(2, 4),
(3, 5),
(3, 6),
(4, 1),
(4, 3);