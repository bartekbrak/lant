# lant - Boggle for other languages.

> Boggle is a word game designed by Allan Turoff and originally distributed by Parker Brothers. The game is played using a plastic grid of lettered dice, in which players attempt to find words in sequences of adjacent letters.
-- [Boggle - wikipedia](https://en.wikipedia.org/wiki/Boggle)

### Inspiration and goals.


I like learning languages, I used to study Celtic philology where I studied Irish, Welsh and other minority languages. 
During that time I got to visit the few places that still have native speakers of these languages and experienced a bit
of their interesting cultures. I learned that there are fewer and fewer speakers and that great efforts are being made
to preserve their linguistic habitats. Also at that time I got introduced to Boggle for English and spent a lot of time
playing with friends expanding and refreshing my vocabulary with each game. And there wasn't a boggle game for Irish. 
I created one and later on, expanded the code to be able to produce such boards for other languages and variants of the 
game (board sizes). 

I imagine playing games in a minority language is a way to help preserve it. It can be fun for both native speakers and 
foreign learners.

I set a goal for myself which is impossible in purpose. I want to create a boggle version for every language there is, 
provided it is possible (some scripts lend themselves to this game better than others, like Japanese kanji or morse code aren't that great). And there are thousands of languages. I expect to find interesting algorithmic challenges on 
the way. 

### The result

[boggle.brak.me](http://boggle.brak.me/) - The results of the algorithm can be seen on my website as an off-line game

### Pre-requisites.

The biggest problem in creating a boggle for a new language is obtaining a quality frequency-sorted wordlist for the language.
So you won't really be able to enjoy this application unless you have some experience in finding such resources. 
Some linguistic knowledge will also be required to deal with languages that use non-latin scripts and in general to 
assess whether the game you created is playable. 

### Code standards

* python3
* 100 chars per line
* Keep it as simple as possible but not simpler
* Performance is important

### Definitions and variable name shortcuts used in the project:

* `iso` - whenever used, refers to 3 letter language identifier [ISO_639-3](https://en.wikipedia.org/wiki/ISO_639-3)
* `iso2` - [2 letter equivalent](https://en.wikipedia.org/wiki/ISO_639-2), for some external systems that use it
* `word form` - inflected word, orthographically distinct form of a lemma 
* `lemma` - canonical, dictionary form of a word, as opposed to `word forms`, also [wikipedia](https://en.wikipedia.org/wiki/Lemma_(morphology))
* `frequency word list` - plan text file with word forms of a given language, sorted by frequency 
of use in the standard text, in descending order , the format is `word1\nword2\n`...
* `standard text` - there is no such thing as a standard text of a language, yet we need one for frequency analysis, in 
such absence we will use subjective judgement and be happy with it
* `board_string` - the ultimate goal of the experiment for a given language, represents dice walls, 
split into chunks of 6 gives you the dice, it is used to display the game

Some definitions are used loosely, while I had some training in linguistics, a better linguist will
be quick to spot opportunities for philosophical debate, because what is a letter really? I'm not 
into this kind of debates. All useful comments are welcome though.

### Log levels

The project uses python logging to deliver two levels of information to `log.txt`:

* `DEBUG` - all steps of the process are recorded
* `INFO` - only the results meaningful to the end goal of finding the right string

You ca also get the breakdown of all results using `report` subcommand. 

### Tests

To run tests:

```
python tests.py
```

This project is mainly used with human present so there aren't many needed. 
More will come when cleverer algorithms get introduced.


### To do 

* Rewrite Solver, the main algorithm to Cython and see if performance gains are possible.
* Find out and document why running on PyPy is at least 10x slower (and getting
slower as script runs, leaks?)

### Licensing

This code is [MIT License](https://tldrlegal.com/license/mit-license) where applicable (a portion was taken from Stack Overflow which is supposedly [CC](https://tldrlegal.com/license/creative-commons-attribution-4.0-international-(cc-by-4))).
The word lists and texts are different matter and to be honest I haven't figured out the licensing 
issues, they are mighty complex. I am doing my best not to steal any one's property but definitely
will by accident. I guess the project will need to be restarted one day when I will have spent more time
on these issues.
