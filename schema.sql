
CREATE TABLE `url_shortener` (
  `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
  `base_url`	TEXT NOT NULL UNIQUE,
  `shortened_url`	TEXT UNIQUE,
  `date`	TEXT NOT NULL
);
