
# encoding: utf-8
import codecs
import copy
import logging
import os
import re
import sqlite3
import sys
from collections import OrderedDict, defaultdict
from random import randint, sample, shuffle

from tabulate import tabulate

from src.utils import split_by_n
from .utils import elapsed

logger = logging.getLogger()


class Lant(object):
    """
    Collects code used for all the steps of the preparation of a new game. In short.:
    1. Analyze stanard text to decide what letters are going to be allowed in the game.
    2. Get letter frequency for a given size of board.
    3. Multiply the allowed letters according to their frequency to get enough for given board size
    4. Randomize how letters are distributed on a dice set.
    5. Randomize the dice (shake the virtual game box) and play boggle game using dictionary (
       the word frequency list) and record the number of words found for this distribution.
    6. Repeat step 5. statistically significant number of times and go back to point 4.


    """
    # The results are added manually from char frequency subcommand
    allowed_characters = {
        'rus': 'абвгдежзийклмнопрстуфхцчшщъыьэюяё',
        'spa': 'abcdefghijklmnñopqrstuvwxyzáéíóúüñ',
        'pol': 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż',
        'eng': 'abcdefghijklmnopqrstuvwxyz',
        'afr': 'abcdefghijklmnoprstuvwyz',
        'ara': 'ءآأؤإئابةتثجحخدذرزسشصضطظعغـفقكلمنهوىيٹپڈژںھ',
        'ces': 'abcdefghijklmnoprstuvyzéíúýčďěňřšťůž',
        'por': 'abcdefghijlmnopqrstuvxyzáâãàçéêíóôõú'
    }
    # The game tries to preserve it's off-line, physical nature, therefore
    # we will 'use' dice, a die has six sides
    LETTERS_ON_A_DIE = 6

    def __init__(
            self,
            iso,
            board_size,
            min_word_length=5,
            language_dir='data',
            wordlist_filename='wordlist',
            wordlist_cap=sys.maxsize,
    ):
        self.iso = iso
        assert iso in self.allowed_characters, "Define this language allowed letters manually."
        self.board_size = board_size
        self.dice_walls_no = board_size * board_size * self.LETTERS_ON_A_DIE
        assert self.dice_walls_no > len(self.allowed_characters[iso]), \
            'board size too small (%s dice walls).' % self.dice_walls_no
        self.texts_path = os.path.join(language_dir, self.iso, 'texts')
        assert os.path.exists(self.texts_path), 'File missing %s' % self.texts_path
        assert len(os.listdir(self.texts_path)) > 0, 'No texts found in %s' % self.texts_path
        self.wordlist_filepath = os.path.join(language_dir, self.iso, wordlist_filename)
        assert os.path.exists(self.wordlist_filepath), 'File missing %s' % self.wordlist_filepath
        logger.debug("I'm opening %r word list." % self.wordlist_filepath)
        self.frequent_words_capped = tuple(
            word.rstrip() for word in codecs.open(self.wordlist_filepath, encoding='utf-8')
        )[:wordlist_cap]
        logger.debug('Word list is %s lines long.' % len(self.frequent_words_capped))
        # The game originally allows words of length 3+, however I propose to test 5+ to limit the
        # number of words used, I assume boggle that encourages longer words is more fun
        self.min_word_length = min_word_length
        logger.debug(self.tell_me_what_texts_you_have())

    def tell_me_what_texts_you_have(self):
        """
        In letter frequency analysis, we need to look at a sufficiently long text and count the
        letters. Log what's availble.

        """
        return "I have these texts to analyze for %r in %s : %s" % (
            self.iso,
            os.path.realpath(self.texts_path),
            '\n'.join(sorted(os.listdir(self.texts_path)))
        )

    def strip_texts_from_disallowed_chars(self):
        """
        Glue all available texts together and strip non-playable characters (like punctuation).
        Return: lowercase string.
        """
        logger.debug('- strip_texts_from_disallowed_chars')
        processed = ''
        for text_file in sorted(os.listdir(self.texts_path)):
            logger.debug('Processing %s.' % text_file)
            path = os.path.join(self.texts_path, text_file)
            with codecs.open(path, encoding='utf-8') as f:
                processed += f.read().lower()
        return re.sub(r'[^%s]' % self.allowed_characters[self.iso], '', processed)

    def get_character_occurrence_in_texts(self):
        """
        Get a dictionary of all allowed characters in per cent.
        Could probably be done with collections.Counter
        """
        logger.debug('- get_character_occurrence_in_texts')
        occurrences = defaultdict(int)
        processed_texts = self.strip_texts_from_disallowed_chars()
        for char in processed_texts:
            if char in self.allowed_characters[self.iso]:
                occurrences[char] += 1
        for char in occurrences:
            occurrences[char] /= float(len(processed_texts))
        return occurrences

    def get_board_string(self, frequency):
        """
        A board string is a string with all the letters from all the dice in order. split into
        chunks of 6 to get the dice.
        It is built from the frequency. The frequency is first rounded down for each letter and then
        for the few missing dice, we up the least used letters until we have enough.

        """
        logger.debug('- get_board_string')
        frequency = OrderedDict(sorted(frequency.items(), key=lambda kv: kv[1], reverse=True))
        total_of_rounded_down = 0

        frequency_rounded_down = copy.copy(frequency)
        for c in frequency:
            how_many_of_one_letter_rounded_down = int(frequency[c] * self.dice_walls_no)
            frequency_rounded_down[c] = how_many_of_one_letter_rounded_down
            total_of_rounded_down += how_many_of_one_letter_rounded_down

        how_many_missing = self.dice_walls_no - total_of_rounded_down
        logger.info("After distributing according to frequency I'm missing :%s" % how_many_missing)

        # fill up the underrepresented letters
        for c in reversed(frequency_rounded_down):
            frequency_rounded_down[c] += 1
            how_many_missing -= 1
            if how_many_missing == 0:
                break

        frequency_levelled = frequency_rounded_down
        ret = ''
        total_letters = 0
        for c in frequency_levelled:
            total_letters += frequency_levelled[c]
            percentage = frequency[c] * 100
            how_many_such_letters = frequency_levelled[c]
            logger.info('%s %05.2f %3s %s' %
                        (c, percentage, how_many_such_letters, c * how_many_such_letters))
            ret += c * how_many_such_letters
        logger.info('%s letters in total' % total_letters)
        return ret

    def scramble_board_string(self, board_string):
        """
        Randomize the dsitribution of letters in a board string.
        Like random.shuffle but *not* in place.
        >>> scramble_board_string('abcd')
        'dacb'
        """
        return ''.join(sample(board_string, len(board_string)))

    def dice_array_from_board_string(self, scrambled_board_string):
        """
        Create the dice from the string
        >>> s = 'abcdef123456' * 8
        >>> dice_array_from_board_string(s)
        ['abcdef',
         '123456',
         ...
        ]

        """
        return list(split_by_n(scrambled_board_string, self.LETTERS_ON_A_DIE))

    def rotate_the_dice_and_pick(self, dice):
        """Rotate each dice randomly and pick the player facing letter.
        >>> s = 'abcdef123456' * 8
        >>> rotate_the_dice_and_pick(dice_array_from_board_string(s))
        ['c', '6', 'c', '4', 'c', '4', 'd', ...]
        """

        return [die[randint(0, 5)] for die in dice]

    def shake_the_box(self, dice):
        """ Shuffle the array to simulate shaking the box. Can be either on a set of dice or
        set of player facing letters.
        >>> shake_the_box(['a', 'b', 'c'])
        ['b', 'a', 'c']
        """
        shuffle(dice)
        return dice

    def get_board(self, board_array):
        """Prepare a structure that Solver expects."""
        return [''.join(a) for a in list(split_by_n(board_array, self.board_size))]

    @elapsed(logger.debug)
    def solve(self, board):
        return Solver(board, self.min_word_length, self.frequent_words_capped).solve()

    @elapsed(logger.debug, 'Round took')
    def play_round(self, initial_board_string, round_length=50):
        """
        Main method, contains all steps to play a round.
        A round consists of x games on the same dice set, but the "box" is shaken each
        time simulating real life game play.

        The result is an average for given dice distribution.

        """
        logger.debug('initial_board_string %r', initial_board_string)
        scrambled_board_string = self.scramble_board_string(initial_board_string)
        logger.debug('scrambled_board_string %r', scrambled_board_string)
        dice_array = self.dice_array_from_board_string(scrambled_board_string)
        logger.debug('dice_array %r', dice_array)
        word_counts = []
        game_no = 0
        while game_no < round_length:
            logger.debug('Start game no %s.' % game_no)
            randomized_dice_array = self.shake_the_box(dice_array)
            logger.debug('randomized_dice_array %r', randomized_dice_array)
            player_facing_letters = self.rotate_the_dice_and_pick(randomized_dice_array)
            logger.debug('player_facing_letters %r', player_facing_letters)
            board = self.get_board(player_facing_letters)
            words_found = list(self.solve(board))
            logger.debug('board:\n%s' % '\n'.join(board))
            logger.debug('found (%s): %s' % (len(words_found), ' '.join(words_found)))
            word_counts.append(len(words_found))
            game_no += 1
        average = sum(word_counts) / len(word_counts)
        return average, scrambled_board_string


class Solver(object):
    """
    Class-shaped rip off of http://stackoverflow.com/a/750012.

    Sample board:
    ['abcda', 'bcdab', 'cdabc', 'dabcd', 'cdabc']
    """
    def __init__(self, board, min_word_length, dictionary):
        self.board = board
        nrows, ncols = len(board), len(board[0])
        # A dictionary word that could be a solution must use only the boards's
        # letters and have length >= min_word_length. (With a case-insensitive match.)
        usable_chars = ''.join(set(''.join(board)))
        logger.debug("I'm using reduced scope %r." % usable_chars)
        # FIXME: this regex needs to escape certain characters like `-`,
        # they are not playable by definition now but who knows, maybe in the future, hyphen
        # will be ok
        bogglable = re.compile('[%s]{%s,}$' % (usable_chars, min_word_length), re.I | re.U).match
        words = set(word for word in dictionary if bogglable(word))
        logger.debug('Word list cut down to %s words.' % len(words))
        self.words = words
        self.prefixes = set(word[:i] for word in words for i in range(2, len(word) + 1))
        self.ncols = ncols
        self.nrows = nrows

    def __extending(self, prefix, path):
        if prefix in self.words:
            yield (prefix, path)
        for (nx, ny) in self.__neighbors(path[-1][0], path[-1][1]):
            if (nx, ny) not in path:
                prefix1 = prefix + self.board[ny][nx]
                if prefix1 in self.prefixes:
                    for result in self.__extending(prefix1, path + ((nx, ny),)):
                        yield result

    def __neighbors(self, x, y):
        for nx in range(max(0, x - 1), min(x + 2, self.ncols)):
            for ny in range(max(0, y - 1), min(y + 2, self.nrows)):
                yield (nx, ny)

    def solve(self, with_path=False):
        # yields str: word
        for y, row in enumerate(self.board):
            for x, letter in enumerate(row):
                for word, path in self.__extending(letter, ((x, y),)):
                    # path example: ((0, 0), (0, 1), (1, 2), (2, 1), (1, 0))
                    if with_path:
                        yield word, path
                    else:
                        yield word


class DB(object):
    """
    Persistence for the results of the games.
    Sqlite is quite sufficient for now.
    """
    def __init__(self, db_file_name):
        self.con = sqlite3.connect(db_file_name, isolation_level=None)
        self.cursor = self.con.cursor()

    def init_schema(self):
        # schema is written so that this can be run idempotently (IF EXISTS everywhere)
        with open('schema.sql') as f:
            self.cursor.executescript(f.read())
            return self

    def record_round(
            self, language, board_x, board_y,
            dice_set, games_played, average_score, wordlist_size):
        self.cursor.execute(
            'INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?)',
            (language, board_x, board_y, dice_set, games_played, average_score, wordlist_size)
        )

    def report_results_breakdown(self):
        self.cursor.execute('''
            SELECT MAX(average_score), COUNT(*), language, board_x, board_y, wordlist_size, dice_set
            FROM games
            GROUP BY language, wordlist_size
            ;
        ''')
        result = self.cursor.fetchall()
        print(tabulate(result))
