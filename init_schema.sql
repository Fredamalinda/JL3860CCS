DROP TABLE IF EXISTS workers;
DROP TABLE IF EXISTS submissions;

CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,
    worker TEXT NOT NULL,
    completed INTEGER DEFAULT 0,     -- 1 = checked / 0 = not checked
    photo TEXT,
    notes TEXT,
    timestamp TEXT NOT NULL,
    manager_initials TEXT,
    approved INTEGER DEFAULT 0
);

INSERT INTO workers (name) VALUES
('Aidan S.'),
('Ryan R.'),
('Tanner J.'),
('Jackie J.'),
('Ethan H.'),
('Zachary H.'),
('Mike H.'),
('Broderick S.'),
('Kayden S.'),
('Cyan P.');
