-- Drop the books table if it already exists
DROP TABLE IF EXISTS books;

-- Create the books table
CREATE TABLE books (
    ID INT PRIMARY KEY,
    Title VARCHAR(200)
);

-- Insert data into the books table
INSERT INTO books (ID, Title)
VALUES
    (1, 'The Hitchhiker''s Guide to the Galaxy'),
    (2, 'One Hundred Years of Solitude'),
    (3, 'Pride and Prejudice and Zombies'),
    (4, 'The Girl with the Dragon Tattoo'),
    (5, 'To Kill a Mockingbird'),
    (6, 'The Perks of Being a Wallflower'),
    (7, 'The Curious Incident of the Dog in the Night-Time'),
    (8, 'The Fault in Our Stars'),
    (9, 'The Catcher in the Rye'),
    (10, 'The Lost Girl of Paris'),
    (11, 'Under the Stars'' Embrace');

-- Convert text to tsvector 
SELECT to_tsvector('english', 'Innovative technologies are shaping the future');

-- Convert text to tsquery 
SELECT to_tsquery('english', 'cat & rat');

-- Select books where the title matches the tsquery 'Girl'
SELECT * FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'Girl');

-- Select books where the title matches the tsquery 'girl' and 'dragon'
SELECT * FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'girl & dragon');

-- Select books where the title matches the tsquery 'Galaxy' or 'Stars'
SELECT * FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'Galaxy | Stars');

-- Select books where the title does not match 'Perks'
SELECT * FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', '!Perks');

-- Select books where the title matches 'Hundred' followed by 'Solitude'
SELECT * FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'Hundred <-> Solitude');

-- Select books where the title matches 'Hundred <3> Solitude'
SELECT * FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'Hundred <3> Solitude');


-- Create an index on the 'title' column
CREATE INDEX title_idx ON books(title);

-- Alter the books table to add a new column for tsvector
ALTER TABLE books ADD COLUMN title_tsvector tsvector;

-- Select all rows from the books table
SELECT * FROM books;

-- Update the title_tsvector column for all rows
UPDATE books SET title_tsvector=to_tsvector('english',title);

-- Create an index on the 'title_tsvector' column using GIN
CREATE INDEX title_tsvector_idx ON books USING GIN(title_tsvector);

-- Create the books table with id, title, and title_tsvector columns
CREATE TABLE books (
    id serial PRIMARY KEY,
    title text,
    title_tsvector tsvector
);

-- Create a stored procedure to update title_tsvector
CREATE OR REPLACE FUNCTION update_title_tsvector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.title_tsvector := to_tsvector('english', NEW.title);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update title_tsvector
CREATE TRIGGER update_title_tsvector_trigger
BEFORE INSERT ON books
FOR EACH ROW
EXECUTE FUNCTION update_title_tsvector();



-- Selecting book ID, title, and calculated rank, and ordering the results by rank in descending order for relevance
SELECT id, title, ts_rank(to_tsvector('english', title), to_tsquery('english', 'stars')) AS rank
FROM books
WHERE title_tsvector @@ to_tsquery('english', 'stars')
ORDER BY rank DESC;

