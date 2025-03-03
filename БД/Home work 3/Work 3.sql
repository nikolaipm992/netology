-- 1. Количество исполнителей в каждом жанре
SELECT g.name, COUNT(ag.artist_id) AS artist_count
FROM Genres g
LEFT JOIN ArtistGenres ag ON g.genre_id = ag.genre_id
GROUP BY g.name;

-- 2. Количество треков, вошедших в альбомы 2019–2020 годов
SELECT COUNT(t.track_id) AS track_count
FROM Tracks t
JOIN Albums a ON t.album_id = a.album_id
WHERE a.release_year BETWEEN 2019 AND 2020;

-- 3. Средняя продолжительность треков по каждому альбому
SELECT a.name, AVG(t.duration) AS avg_duration
FROM Albums a
JOIN Tracks t ON a.album_id = t.album_id
GROUP BY a.name;

-- 4. Все исполнители, которые не выпустили альбомы в 2020 году
SELECT ar.name
FROM Artists ar
WHERE ar.artist_id NOT IN (
    SELECT aa.artist_id
    FROM ArtistAlbums aa
    JOIN Albums al ON aa.album_id = al.album_id
    WHERE al.release_year = 2020
);

-- 5. Названия сборников, в которых присутствует конкретный исполнитель (например, "Исполнитель 1")
SELECT c.name
FROM Compilations c
JOIN CompilationTracks ct ON c.compilation_id = ct.compilation_id
JOIN Tracks t ON ct.track_id = t.track_id
JOIN Albums a ON t.album_id = a.album_id
JOIN ArtistAlbums aa ON a.album_id = aa.album_id
JOIN Artists ar ON aa.artist_id = ar.artist_id
WHERE ar.name = 'Исполнитель 1';