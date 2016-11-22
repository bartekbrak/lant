#!/usr/bin/env python3
# encoding: utf-8
import argparse
import codecs
import os
from pprint import pprint

from bottle import route, run
from itertools import islice

from .core import Solver

min_word_length = 5


@route('/solver', method='HEAD')
def solver_head():
    pass

wordlist_files_cache = {}
# mem = Memory(cachedir='./cache', verbose=3)
# ansi_colours_converter = Ansi2HTMLConverter(inline=True)
threshold = 1000


# @mem.cache()
# def trans(word, from_language, to_language='en'):
#     ansi = subprocess.run(
#         ('trans', '%s:%s' % (from_language, to_language), word),
#         stdout=subprocess.PIPE,
#         universal_newlines=True
#     ).stdout
#     ansi = ansi.replace('\n\n', '\n')
#     _, rest = ansi.split('\n', 1)
#     translation = re.search(r'\x1b\[1m([^\x1b]+)', rest).group(1)
#     return translation, ansi_colours_converter.convert(rest, full=False)


@route('/solver/<iso>/<gridstring>')
def solver(iso, gridstring):
    print('received gridstring:', gridstring)
    grid = gridstring.lower().split(' ')
    wordlist_filepath = 'language_data_dir/%s/varia/fr_wordlist' % iso
    print(wordlist_filepath)
    if not os.path.isfile(wordlist_filepath):
        print('WORDLIST NOT FOUND! BAD!')
        return dict(data=[])
    words = wordlist_files_cache.setdefault(
        iso, tuple(word.rstrip() for word in codecs.open(wordlist_filepath, encoding='utf-8')))
    print('got grid', grid)
    print('words in file list', len(words))
    words = Solver(grid, min_word_length, words).solve(with_path=True)
    sorted_words = sorted(islice(words, threshold))
    return dict(data=sorted_words)


# @post('/trans')
# def trans():
#     print(request.json)
#     iso, words = 'afr', ['test']
#     ret = {}
#     for word in words:
#         in_target, html = trans(word, iso)
#         ret[word] = {
#             'translated': in_target,
#             'html': html,
#         }
#     return dict(data=ret)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['test', 'run'])
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    if args.action == 'test':
        print('testing')
        pprint(solver('afr', 'deevn seuen ndlen edyrl moydt'))
    else:
        run(host='localhost', port=8080, reloader=True)
