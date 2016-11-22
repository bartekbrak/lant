#!/usr/bin/env python3
import argparse
import logging
import os

import re
import urllib.request
from collections import Counter
from pprint import pprint

import sys

from src.core import DB, Lant

logger = logging.getLogger()


def configure_logging(level=logging.DEBUG, method='log.txt'):
    """
    Configure file-based logging.
    """
    formats = {
        'full': '\033[30m%(levelname)-8s\033[0m %(asctime)-15s %(message)s',
        'simple': '%(message)s',
    }
    if method == 'STDOUT':
        logging.basicConfig(
            stream=sys.stdout,
            level=level,
            format=formats['simple'],
        )
    else:
        logging.basicConfig(
            filename=method,
            filemode='a',
            level=level,
            format=formats['simple'],
        )


def parse_args():
    parser = argparse.ArgumentParser()
    # 5 is my favourite size, 4 is original, I imagine larger boards will appeal to boggle nerds too
    parser.add_argument('--board-size', type=int, default='5')
    parser.add_argument('--round-size', type=int, default='50')
    parser.add_argument('--rounds', type=int, default='100000')
    parser.add_argument('--min-word-length', type=int, default='5')
    parser.add_argument('-i', '--iso', help='693-3 language code', type=str, required=True)
    parser.add_argument('--language-dir', help='language base dir', type=str, default='data')
    parser.add_argument('--word-list-file-name', type=str, default='wordlist')
    parser.add_argument('--wordlist-cap', help="Cap wordlist to x.", type=int, default=5000)
    parser.add_argument('-d', '--db-name', help='Results ddb filename', default='db.sqlite3')
    parser.add_argument(
        '-L', '--logging-level',
        default='INFO',
        choices=['INFO', 'DEBUG', 'NO_LOGS'],
        help='Log this level and up. INFO and DEBUG logged to log.txt.'
    )
    parser.add_argument('--log-method', choices=['STDOUT', 'log.txt'], default='log.txt')

    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.add_parser('report', help='Just report and exit')

    char_frequency = subparsers.add_parser(
        'char_frequency', help='Analyze script of the language based on file.txt')
    char_frequency.add_argument('file')
    char_frequency.add_argument('-t', '--threshold', type=int)

    download_texts = subparsers.add_parser(
        'download_texts', description='Download a Project Gutenberg text')
    download_texts.add_argument('-e', '--etextno', type=int, nargs='+', required=True)

    opensubtitles = subparsers.add_parser(
        'opensubtitle_frequency_list',
        description='Download a qord list from hermitdave/FrequencyWords')
    opensubtitles.add_argument('--iso2', help='iso-639-2 language identifier', required=True)

    namespace = parser.parse_args()

    if namespace.logging_level == 'NO_LOGS':
        namespace.logging_level = 'CRITICAL'

    return namespace


def char_frequency(text, threshold):
    """
    Count characters in a text, skipping some.
    This is used to decide what are playable letters in a given language when you are not sure
    and you rarely be sure outside common languages.
    The output needs to be parsed with brain, checked against articles on the language and or
    consulted with natives. Sometimes it is not obvious whether a given letter should be playable
    or not. /examples?

    It is possible to provide a threshold that will make creating the final string easier.

    """
    not_interesting = r'[0-9\n ”,\-’!;:„?”*()á/_"\'@†$§#%&\][.\ufeff=^£]'
    content = open(text).read().lower()
    eliminated = re.sub(not_interesting, '', content)
    counted = Counter(eliminated)
    pprint(counted)
    summed = sum(counted.values())
    threshold = threshold or summed * 0.01
    sys.stdout.write('threshold %f\n' % threshold)
    above_threshold = {k: v for k, v in counted.items() if v > threshold}
    sys.stdout.write('all %r\n' % ''.join(sorted(counted.keys())))
    sys.stdout.write('cut %r\n' % ''.join(sorted(above_threshold.keys())))


def download_gutenberg_texts(iso, etexts, language_dir):
    """
    A wrapper around Gutenberg library of texts.
    Those texts are not very good for the problem being solved but are easiest to get.

    """
    try:
        import gutenberg
    except ImportError:
        print('pip install Gutenberg==0.4.2')
        sys.exit()

    from gutenberg._util.os import reopen_encoded
    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers
    for etextno in etexts:
        text = load_etext(etextno, refresh_cache=True)
        text = strip_headers(text).strip()
        print(iso, language_dir, etextno)
        filename = os.path.join(language_dir, iso, 'texts', str(etextno))
        logger.debug(filename)
        with reopen_encoded(argparse.FileType('w')(filename), 'w', 'utf8') as outfile:
            outfile.write(text)


def get_opensubtitle_frequency_list(iso2):
    """
    Thanks to wonderful work of hermitdave/FrequencyWords we get ok quality
    frequency sorted wordlists from opensubtitles.

    There are 59 languages available so far.
    The formaty is
        word1 21321
        word2 20001
        ...

    redirect the output to desired file

    """
    url = (
        'https://raw.githubusercontent.com/hermitdave/FrequencyWords/'
        'master/content/2016/{iso2}/{iso2}_50k.txt'
    ).format(iso2=iso2)
    response = urllib.request.urlopen(url)
    bytes_data = response.read()
    wordlist = bytes_data.decode('utf-8')
    without_counts = re.sub('\s?\d+', '', wordlist)
    sys.stdout.write(without_counts)


def main():
    args = parse_args()
    configure_logging(logging._nameToLevel[args.logging_level], args.log_method)
    db = DB(args.db_name).init_schema()
    if args.subcommand == 'report':
        db.report_results_breakdown()
    elif args.subcommand == 'char_frequency':
        char_frequency(args.file, args.threshold)
    elif args.subcommand == 'download_texts':
        download_gutenberg_texts(args.iso, args.etextno, args.language_dir)
    elif args.subcommand == 'opensubtitle_frequency_list':
        get_opensubtitle_frequency_list(args.iso2)
    else:
        logger.info('clear screen \x1bc')

        lant = Lant(
            iso=args.iso,
            board_size=args.board_size,
            min_word_length=args.min_word_length,
            language_dir=args.language_dir,
            wordlist_filename=args.word_list_file_name,
            wordlist_cap=args.wordlist_cap
        )
        wordlist_size = args.wordlist_cap or len(lant.frequent_words_capped)
        occurrence = lant.get_character_occurrence_in_texts()
        initial_board_string = lant.get_board_string(occurrence)

        for i in range(args.rounds):
            average, scrambled_board_string = lant.play_round(initial_board_string, args.round_size)

            db.record_round(
                args.iso, args.board_size, args.board_size,
                scrambled_board_string, args.round_size, average,
                wordlist_size)
            logger.info('%.2f: %s' % (average, scrambled_board_string))


if __name__ == "__main__":
    main()
