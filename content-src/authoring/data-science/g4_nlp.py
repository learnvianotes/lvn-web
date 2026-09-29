from kit import *

G = "Natural Language Processing"

CORPUS = '''
        corpus = ("India, officially the Republic of India, is a country in South Asia. "
                  "It is the seventh-largest country by area, the second-most populous country, "
                  "and the most populous democracy in the world. "
                  "In the Indian Ocean, India is in the vicinity of Sri Lanka and the Maldives.")
'''


@topic(G, "tokenization", "Tokenization, Stemming & Lemmatization", "cut")
def _():
    yield lead("Before a computer can work with text, it has to be cut into pieces (tokens) and words have to be brought to a common form.")
    yield note("The notebook calls this module “Deep Learning”, but everything in it is **text processing (NLP)** — the groundwork that comes before any language model.", "About this module")
    yield section("Why not just split()?", "question-mark")
    yield code('''
        txt = "Hello Geeks. We're hoping you guys are doing great."
        print(len(txt.split(".")))      # 3        ← counts an empty piece after the last "."
        print(txt.split()[:3])          # ['Hello', 'Geeks.', "We're"]   ← punctuation stuck to words
    ''')
    yield section("Tokenizing with NLTK", "scissors")
    yield code('''
        from nltk.tokenize import sent_tokenize, word_tokenize

        txt = "Hello Geeks. We're hoping you guys are doing great."
        print(len(sent_tokenize(txt)))                    # 2
        print(word_tokenize(txt))                         # ['Hello', 'Geeks', '.', 'We', "'re", 'hoping', 'you', 'guys', 'are', 'doing', 'great', '.']
        print([w for w in word_tokenize(txt) if w.isalnum()])   # ['Hello', 'Geeks', 'We', 'hoping', 'you', 'guys', 'are', 'doing', 'great']
    ''')
    yield shell('''
        pip install nltk
        python -m nltk.downloader punkt punkt_tab stopwords wordnet omw-1.4
    ''', caption="Setup")
    yield note("`sent_tokenize` knows that “Dr.” or “U.K.” don't end a sentence; `word_tokenize` splits off punctuation and contractions (“We're” → “We”, “'re”).")
    yield section("Stemming vs lemmatization", "git-compare")
    yield code('''
        from nltk.stem import PorterStemmer, WordNetLemmatizer
        stem, lem = PorterStemmer(), WordNetLemmatizer()

        words = ["change", "changes", "changed", "studies", "better"]
        print([stem.stem(w) for w in words])              # ['chang', 'chang', 'chang', 'studi', 'better']
        print([lem.lemmatize(w) for w in words])          # ['change', 'change', 'changed', 'study', 'better']
        print(lem.lemmatize("changed", pos="v"), lem.lemmatize("better", pos="a"))   # change good
    ''')
    yield table(
        ["", "Stemming", "Lemmatization"],
        ["How", "Chops suffixes by rules", "Looks words up in a dictionary (WordNet)"],
        ["Output", "May not be a real word (`chang`)", "Always a real word (`change`)"],
        ["Speed", "Fast", "Slower"],
        ["Needs part of speech", "No", "For best results (`pos=\"v\"` verb, `\"a\"` adjective)"],
    )
    yield note("Without `pos`, the lemmatizer treats every word as a noun — that's why the notebook got `changed` back unchanged. Tell it the word is a verb and it returns `change`.")


@topic(G, "stop-words", "Stop Words", "filter")
def _():
    yield lead("Stop words are very common words (“is”, “the”, “a”) that carry little meaning on their own. Removing them shrinks the text and highlights the words that matter.")
    yield code('''
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        stop_words = set(stopwords.words("english"))
        print(len(stop_words), "is" in stop_words, "good" in stop_words)   # 198 True False

        txt = "This is not a good time to talk."
        kept = [w for w in word_tokenize(txt) if w.lower() not in stop_words and len(w) >= 2]
        print(kept)                                  # ['good', 'time', 'talk']
    ''')
    yield warn("“not” is a stop word in NLTK's list — so “not a good time” becomes “good time”. For sentiment analysis, removing stop words can flip the meaning; keep negations.", "Careful")
    yield section("Stop words in spaCy", "language")
    yield code('''
        import spacy
        nlp = spacy.load("en_core_web_sm")          # python -m spacy download en_core_web_sm

        print(len(nlp.Defaults.stop_words) > 300)   # True
        print(nlp.vocab["is"].is_stop, nlp.vocab["GFG"].is_stop)   # True False

        nlp.Defaults.stop_words.add("i.e")          # add your own
        nlp.vocab["i.e"].is_stop = True
        nlp.Defaults.stop_words.discard("done")     # or remove one
        nlp.vocab["done"].is_stop = False
        print(nlp.vocab["i.e"].is_stop, nlp.vocab["done"].is_stop)  # True False
    ''')
    yield note("Change both `nlp.Defaults.stop_words` (the list) and `nlp.vocab[word].is_stop` (the flag tokens check) — spaCy keeps them separately.")


@topic(G, "characters", "Characters, ASCII & DIY String Functions", "letter-case")
def _():
    yield lead("Every character is a number. Knowing the codes lets you build string functions yourself — a common interview exercise and the basis of text encoding.")
    yield section("ord() and chr()", "arrows-exchange")
    yield code('''
        text = "The quick brown fox"
        print([ord(c) for c in "Tq "])                    # [84, 113, 32]
        print(chr(97), chr(65), chr(93))                  # a A ]
        codes = [ord(c) for c in text]
        print("".join(chr(n) for n in codes) == text)     # True
        print("".join(chr(n) for n in range(65, 91)))     # ABCDEFGHIJKLMNOPQRSTUVWXYZ
        print("".join(chr(n) for n in range(90, 64, -1))) # ZYXWVUTSRQPONMLKJIHGFEDCBA
    ''')
    yield table(
        ["Range", "Characters"],
        ["48–57", "`0`–`9`"],
        ["65–90", "`A`–`Z`"],
        ["97–122", "`a`–`z` (each lowercase letter = its uppercase + 32)"],
        ["32", "space"],
    )
    yield note("The notebook prints `ascii` instead of its list `ascii_` and gets `<built-in function ascii>` — `ascii` is a built-in function. Avoid names that shadow built-ins (`list`, `str`, `sum`, `ascii`…).", "Correction")
    yield section("DIY upper, lower and title", "code")
    yield code('''
        def upper(text):
            return "".join(chr(ord(c) - 32) if "a" <= c <= "z" else c for c in text)

        def lower(text):
            return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in text)

        def title(text):
            return " ".join(upper(w[:1]) + lower(w[1:]) for w in text.split(" "))

        print(upper("delhi"), lower("CARTOON"))               # DELHI cartoon
        print(title("let us study machine learning today"))   # Let Us Study Machine Learning Today
        print(title("hello  world"))                          # Hello  World
    ''')
    yield note("`w[:1]` instead of `w[0]` keeps `title` from crashing on empty words (two spaces in a row).")
    yield section("DIY isalpha and isdigit", "check")
    yield code('''
        def is_alpha(text):
            return len(text) > 0 and all("A" <= c <= "Z" or "a" <= c <= "z" for c in text)

        def is_digit(text):
            return len(text) > 0 and all("0" <= c <= "9" for c in text)

        print(is_alpha("datascience"), is_alpha("1234"))     # True False
        print(is_digit("1234"), is_digit("machinelearning")) # True False
    ''')
    yield warn("The notebook's `check_alpha` returns `False` for `'datascience'` — its `if len(text) == c` check sits **inside** the loop, so it decides after the first character. Check after the loop (or use `all()` as above).", "Bug in the notebook")
    yield section("Finding runs of digits and words", "search")
    yield code('''
        txt = "The number is 8372493 not 423423"
        runs, current = [], ""
        for ch in txt:
            if ch.isdigit():
                current += ch
            elif current:
                runs.append(current)
                current = ""
        if current:
            runs.append(current)
        print(runs)                                     # ['8372493', '423423']

        sentence = "GFG is launching a new Data Structure in Python Course"
        print([w for w in sentence.split() if w.lower().startswith("i")])   # ['is', 'in']
        print([w for w in sentence.split() if w.lower().endswith("e")])     # ['Structure', 'Course']
        print("let us study data science".find("data"))                     # 13
    ''')


@topic(G, "regex", "Regular Expressions", "regex")
def _():
    yield lead("Regular expressions describe text patterns — phone numbers, emails, hyphenated words — and find, extract or replace them in one line. Python's `re` module.")
    yield section("search, findall, finditer", "search")
    yield code('''
        import re
        m = re.search("hello", "hello world")
        print(m.span(), m.start(), m.end(), m.group())    # (0, 5) 0 5 hello
        print(re.search("data", "hello world"))           # None
        print(re.findall("at", "The rat sat on the mat"))                 # ['at', 'at', 'at']
        print([m.span() for m in re.finditer("hello", "hello world hello earth")])   # [(0, 5), (12, 17)]
    ''')
    yield table(
        ["Function", "Returns"],
        ["`re.search(p, s)`", "The first match (a Match object) or `None`"],
        ["`re.match(p, s)`", "A match only at the **start** of `s`"],
        ["`re.findall(p, s)`", "A list of all matching strings (or groups)"],
        ["`re.finditer(p, s)`", "Match objects one by one — with positions"],
        ["`re.sub(p, repl, s)`", "`s` with matches replaced"],
        ["`re.split(p, s)`", "`s` split at matches"],
    )
    yield section("The building blocks", "puzzle")
    yield table(
        ["Pattern", "Matches"],
        ["`.`", "Any character except newline"],
        ["`\\d` / `\\D`", "A digit / anything but a digit"],
        ["`\\w` / `\\W`", "A word character (letter, digit, _) / anything else"],
        ["`\\s`", "Whitespace"],
        ["`[A-Za-z]`, `[^!,$@]`", "One character from a set / **not** in a set"],
        ["`^` / `$`", "Start / end of the string"],
        ["`*` `+` `?` `{3}` `{2,4}`", "0+, 1+, 0 or 1, exactly 3, 2 to 4 times"],
        ["`(a|b)`", "Group with alternatives"],
    )
    yield code('''
        import re
        print(re.findall(".at", "The rat sat on the mat and a cat"))     # ['rat', 'sat', 'mat', 'cat']
        print(re.findall(r"^\\d", "4 is divisible by 2"), re.findall(r"^\\d", "Hi, 4"))   # ['4'] []
        print(re.findall(r"\\d$", "4 is divisible by 2 and not by 3"))   # ['3']
        print(re.findall("[A-Z]", "Welcome to GFG 1"))                   # ['W', 'G', 'F', 'G']
        print(re.search(r"\\d{3}-\\d{4}-\\d{3}", "call 834-4324-345").group())   # 834-4324-345
    ''')
    yield warn("Write patterns as **raw strings** — `r\"\\d\"` — so Python doesn't treat the backslash as an escape. The notebook's `'\\d'` works but triggers a warning in modern Python.")
    yield section("Cleaning text", "eraser")
    yield code('''
        import re
        print(re.sub(r"[!,$@]", "", "Eshant $ is happ@y !,").strip())    # Eshant  is happy
        print(re.sub(r"\\d", "", "I'm Ashish and 24").strip())            # I'm Ashish and
        print(re.findall(r"\\w+-\\w+-\\w+", "Geeks-for-Geeks and works-it-out"))   # ['Geeks-for-Geeks', 'works-it-out']
        print(re.sub(r"\\s+", " ", "too    many   spaces"))              # too many spaces
    ''')
    yield section("Email patterns", "mail")
    yield code('''
        import re
        EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*\\.[A-Za-z]{2,}"
        text = "Mail eshant@gfg.in or esh@aap.gov.in to contact us"
        print([m.group() for m in re.finditer(EMAIL, text)])        # ['eshant@gfg.in', 'esh@aap.gov.in']

        GFG_OR_GMAIL = r"[\\w.]+@(gfg|gmail)\\.(org|net|in|com)"
        for mail in ["eshant@gfg.org", "eshant@gmail.com", "eshant@yahoo.com"]:
            print(mail, bool(re.fullmatch(GFG_OR_GMAIL, mail)))
    ''', check=False)
    yield shell('''
        ['eshant@gfg.in', 'esh@aap.gov.in']
        eshant@gfg.org True
        eshant@gmail.com True
        eshant@yahoo.com False
    ''', caption="Output")
    yield note("Two slips in the notebook's patterns: `[A-Za-z0-2]` allows only the digits 0–2 (should be `0-9`), and an unescaped `.` matches **any** character — write `\\.` for a literal dot. Use `re.fullmatch` to validate a whole string instead of finding a pattern inside it.", "Correction")
    yield section("Without regex: splitting an email", "cut")
    yield code('''
        mails = ["eshant@gmail.com", "eshant@aap.gov.in", "esh@geeksforgeeks.com"]
        parts = [(m.split("@")[0], *m.split("@")[1].split(".", 1)) for m in mails]
        print(parts)      # [('eshant', 'gmail', 'com'), ('eshant', 'aap', 'gov.in'), ('esh', 'geeksforgeeks', 'com')]
    ''')


@topic(G, "spacy", "spaCy Basics", "language")
def _():
    yield lead("spaCy is an industrial-strength NLP library: one call runs tokenization, part-of-speech tagging, sentence splitting, lemmatization and named-entity recognition.")
    yield shell('''
        pip install spacy
        python -m spacy download en_core_web_sm
    ''', caption="Setup")
    yield section("Tokens", "cut")
    yield code('''
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("The cost of Iphone in U.K is 699$")
        print([t.text for t in doc])            # ['The', 'cost', 'of', 'Iphone', 'in', 'U.K', 'is', '699', '$']
    ''')
    yield note("spaCy keeps “U.K” together and splits “699$” into the number and the currency sign — rules that a plain `split()` can't know.")
    yield section("Parts of speech & lemmas", "tags")
    yield code('''
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("The cost of Iphone in U.K is 699$")
        print([(t.text, t.pos_) for t in doc][:4])   # [('The', 'DET'), ('cost', 'NOUN'), ('of', 'ADP'), ('Iphone', 'PROPN')]
        print([t.lemma_ for t in nlp("She was running faster")])   # ['she', 'be', 'run', 'fast']
    ''')
    yield table(
        ["Tag", "Meaning", "Tag", "Meaning"],
        ["`NOUN`", "Noun", "`VERB`", "Verb"],
        ["`PROPN`", "Proper noun", "`AUX`", "Auxiliary (is, was)"],
        ["`ADJ`", "Adjective", "`ADP`", "Preposition"],
        ["`DET`", "Determiner (the, a)", "`NUM`", "Number"],
    )
    yield section("Sentences & entities", "list-details")
    yield code('''
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is the first sentence. Please check it. Let's study now")
        print([s.text for s in doc.sents])     # ['This is the first sentence.', 'Please check it.', "Let's study now"]
        ents = nlp("Sundar Pichai joined Google in 2004 in California.").ents
        print([(e.text, e.label_) for e in ents])   # [('Sundar Pichai', 'PERSON'), ('Google', 'ORG'), ('2004', 'DATE'), ('California', 'GPE')]
    ''')
    yield cards(
        ("NLTK", "A teaching toolkit: many algorithms and corpora, you assemble the pipeline yourself.", "school"),
        ("spaCy", "Production-ready pipelines, fast, one object (`doc`) with everything — tokens, tags, lemmas, entities.", "rocket"),
    )


@topic(G, "wordnet", "Synonyms & Antonyms with WordNet", "vocabulary")
def _():
    yield lead("WordNet is a dictionary for programs: words are grouped into sets of synonyms (*synsets*) with definitions, and linked to antonyms and broader or narrower words.")
    yield code('''
        from nltk.corpus import wordnet

        syn = wordnet.synsets("book")
        print(syn[0].definition())      # a written work or composition that has been published (printed on pages bound together)
        print(syn[0].name())            # book.n.01
    ''')
    yield section("Synonyms", "arrows-shuffle")
    yield code('''
        from nltk.corpus import wordnet
        synonyms = []
        for s in wordnet.synsets("happy"):
            for lemma in s.lemmas():
                synonyms.append(lemma.name())
        print(sorted(set(synonyms)))    # ['felicitous', 'glad', 'happy', 'well-chosen']
    ''')
    yield note("Use a `set` to drop duplicates — the notebook's list repeats “happy” four times because it appears in four synsets.")
    yield section("Antonyms", "arrows-diff")
    yield code('''
        from nltk.corpus import wordnet
        antonyms = {a.name() for s in wordnet.synsets("healthy") for l in s.lemmas() for a in l.antonyms()}
        print(sorted(antonyms))         # ['unhealthy']
    ''')
    yield table(
        ["Call", "Gives"],
        ["`wordnet.synsets(word)`", "Every sense of the word"],
        ["`synset.definition()` / `.examples()`", "Its meaning / example sentences"],
        ["`synset.lemmas()`", "The words in that sense (synonyms)"],
        ["`lemma.antonyms()`", "Opposites"],
        ["`synset.hypernyms()`", "Broader terms (dog → canine)"],
    )


@topic(G, "text-encoding", "Encoding Text as Numbers", "binary")
def _():
    yield lead("Models work with numbers, not words. The simplest encoding gives every word in the vocabulary an ID — then each sentence becomes a list of IDs, and can be turned back.")
    yield section("Build a vocabulary", "list-numbers")
    yield code(CORPUS + '''
        from nltk.tokenize import word_tokenize, sent_tokenize
        from nltk.corpus import stopwords

        stop = set(stopwords.words("english"))
        def keep(word):
            return word.lower() not in stop and len(word) >= 2      # drop stop words and punctuation

        words = [w.lower() for w in word_tokenize(corpus) if keep(w)]
        vocab = sorted(set(words))                                   # sorted → same IDs every run
        word_to_num = {w: i for i, w in enumerate(vocab, start=1)}
        num_to_word = {i: w for w, i in word_to_num.items()}
        print(len(vocab), vocab[:4])                                 # 18 ['area', 'asia', 'country', 'democracy']
    ''')
    yield note("The notebook builds the vocabulary from `list(set(words))` — sets have no fixed order, so the IDs change every run. Sort first to make the mapping reproducible.", "Correction")
    yield section("Encode and decode", "arrows-exchange")
    yield code(CORPUS + '''
        from nltk.tokenize import word_tokenize, sent_tokenize
        from nltk.corpus import stopwords

        stop = set(stopwords.words("english"))
        keep = lambda w: w.lower() not in stop and len(w) >= 2
        vocab = sorted({w.lower() for w in word_tokenize(corpus) if keep(w)})
        word_to_num = {w: i for i, w in enumerate(vocab, start=1)}
        num_to_word = {i: w for w, i in word_to_num.items()}

        encoded = [[word_to_num[w.lower()] for w in word_tokenize(s) if keep(w)] for s in sent_tokenize(corpus)]
        print(encoded[0])                                            # [5, 10, 12, 5, 3, 15, 2]
        print(" ".join(num_to_word[n] for n in encoded[0]))          # india officially republic india country south asia
    ''')
    yield section("Keeping every word", "list")
    yield p("To decode back to the full sentence, keep stop words and drop only punctuation. The vocabulary grows, but nothing is lost except capitalisation and punctuation:")
    yield code(CORPUS + '''
        from nltk.tokenize import word_tokenize, sent_tokenize
        is_word = lambda w: any(c.isalpha() for c in w)
        vocab = sorted({w.lower() for w in word_tokenize(corpus) if is_word(w)})
        word_to_num = {w: i for i, w in enumerate(vocab, start=1)}
        num_to_word = {i: w for w, i in word_to_num.items()}
        first = sent_tokenize(corpus)[0]
        ids = [word_to_num[w.lower()] for w in word_tokenize(first) if is_word(w)]
        print(" ".join(num_to_word[i] for i in ids))   # india officially the republic of india is a country in south asia
    ''')
    yield cards(
        ("Bag of words / counts", "`CountVectorizer` — how often each vocabulary word occurs (see *Naive Bayes*).", "chart-bar"),
        ("TF-IDF", "Counts weighted down for words common across all documents.", "scale"),
        ("Word embeddings", "Dense vectors where similar words are close (Word2Vec, GloVe) — what neural networks and LLMs build on.", "brain"),
    )
