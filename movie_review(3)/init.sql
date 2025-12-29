-- User table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Genre table
CREATE TABLE genre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) NOT NULL UNIQUE
);

-- Movie table
CREATE TABLE movie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(128),
    year INTEGER,
    director VARCHAR(64),
    description TEXT,
    poster_url VARCHAR(256),
    average_rating FLOAT DEFAULT 0.0
);

-- Review table
CREATE TABLE review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    rating INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    movie_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (movie_id) REFERENCES movie (id)
);

-- Association table: User Favorites
CREATE TABLE favorites (
    user_id INTEGER,
    movie_id INTEGER,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (movie_id) REFERENCES movie (id)
);

-- Association table: Movie Genres
CREATE TABLE movie_genres (
    movie_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movie (id),
    FOREIGN KEY (genre_id) REFERENCES genre (id)
);

-- Indexes
CREATE INDEX ix_user_username ON user (username);
CREATE INDEX ix_user_email ON user (email);
CREATE INDEX ix_movie_title ON movie (title);
