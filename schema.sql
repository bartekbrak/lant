-- Note that only `games` is used as of now
CREATE TABLE IF NOT EXISTS frequent_words(
  language VARCHAR(3), -- ISO 639-2
  frequency INT,  -- ordinal, starting from 1
  word VARCHAR(255),
  UNIQUE (language, frequency, word)
);
CREATE TABLE IF NOT EXISTS letter_frequencies (
  language VARCHAR(3),
  frequencies TEXT  -- json serialized dict of letter:float frequencies
);
CREATE TABLE IF NOT EXISTS letter_distributions (
  language VARCHAR(3),
  letters_amount INT, -- divisible by six
  distribution VARCHAR(1024) -- like `aaaaabbcdeeee...`, length equal to letters_amount
);

CREATE TABLE IF NOT EXISTS games(
  language VARCHAR(3),
  board_x INT,
  board_y INT,
  -- continuos string but each six letters represent one dice, divisible by six, equals board_x * board_y * 6
  -- 255 is a mistake, I am sure some nerds woul
  dice_set VARCHAR(10240),
  games_played INT,  -- 100 seems a good standard
  average_score FLOAT,  -- the most important bit, the set with highest average_score is best
  wordlist_size INT
);

-- Used when creating letter frequencies, only some letters should be counted in a file.
CREATE TABLE IF NOT EXISTS letter_sets(
  language VARCHAR(3),
  letters TEXT,
  UNIQUE (language)
);


-- indexes
CREATE INDEX IF NOT EXISTS for_the_report ON games (language, wordlist_size);
