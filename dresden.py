# Deal with paths
from pathlib import Path
# Text Processing
import re

def split_text(text, chapter_pattern, contents_captured = False, pop0 = True, end_pattern = None):
    """
    Splits string into list of multiple strings
    
    Parameters
    ----------
    text : str
        Target string to split
    chapter_pattern : str
        regular expresion defining where to split string
    contents_captured : bool, default False
        If true, remove any sections captured by pattern under 100 characters, intended to remove table of contents
    pop0 : bool, default True
        Pop off content leading up to first instance of pattern
    end_pattern : str, default None
        alternate pattern to remove extra content after final chapter
    
    Returns
    -------
    list
        list of chapters captured by chapter_pattern
    """
    # Split on chapter seperator
    text = re.split(chapter_pattern, text)
    if contents_captured:
        # Pop off preamble before the table of contents
        text.pop(0);
        # Remove any table of contents entries that matches the chapter pattern
        text = [split for split in text if len(split) > 100]
    if pop0:
        # Pop off content leading up to first chapter
        text.pop(0);
    if end_pattern:
        # Clean up trailing content from after the end of the final chapter
        text[-1] = re.sub(end_pattern, '', text[-1])
    return text

def load_dresden(paths):
    """
    Loads and cleans the entire dresden files from a ``paths`` contain each book in their own folders.
    Adapted from my thesis workflow
    
    Returns
    -------
    dict
        nest dict, index of book_n.chapter_n. "book" for int of book number, "text" for content of chapter
    """
    novels = ['Storm Front', 'Fool Moon', 'Grave Peril', 'Summer Knight', 'Death Masks',
          'Blood Rites', 'Dead Beat', 'Proven Guilty', 'White Night', 'Small Favor', 
          'Turn Coat', 'Changes', 'Ghost Story', 'Cold Days', 'Skin Game', 'Peace Talks', 'Battle Ground']
    anthologies = ['Side Jobs', 'Brief Cases']
    
    novel_dict = {i+1 : novel for i, novel in enumerate(novels)}
    # Full version including anthologies tacked on at the end, It feels like it could easily be misleading to have them come "after" the most recent book
    # I could also break the anthologies into each individual short story, and then arrange absolutely everything in chronological order, but maybe later.
    full_dict = {i+1 : novel for i, novel in enumerate(novels + anthologies)}
    
    books = []
    for path in paths:
        with open(path, 'r', encoding = 'utf-8') as f:
                 books.append(f.read())
    
    # Sorting names to match book names
    raw_docs = {}
    for title, text in zip(sorted(full_dict.values()), books):
        # Basically doing a reverse look up in the dict using the value instead of the key
        # this seemed like the simplest way to easily get everything in the right order
        raw_docs[list(full_dict.keys())[list(full_dict.values()).index(title)]] = text
    # Recreating the dict in ID order, since it would just feel nicer to be honest.
    raw_docs = dict(sorted(raw_docs.items(), key=lambda item: item[0]))
    
    
    # Manually identified comomon patterns to split each book
    int_pat = re.compile('\n\n(?=[0-9]+\n\n)')
    chap_sep = re.compile('\n+\t*(?=Chapter)')
    chap_sep_17 = re.compile('(\n+\t*(?=Chapter)|\nFor my readers who, for whatever reason, aren’t sleeping tonight. Merry Christmas, you magnificent weirdos.)')
    
    enjoyed_pat = re.compile(fr'\nEnjoyed {novels}?.*$', flags=re.DOTALL | re.M)
    author_note_pat = re.compile(fr'\nAuthor’s Note.*$', flags=re.DOTALL | re.M)
    about_author_pat = re.compile(fr'\nAbout the Author.*', flags=re.DOTALL | re.M)
    ack_pat = re.compile(fr'\nACKNOWLEDGMENTS.*', flags=re.DOTALL | re.M)
    
    # Arranging patterns to take care of each book
    chapter_seperators = [int_pat] * 14 + [chap_sep] * 2 + [chap_sep_17]
    ending_seperators = [None] * 2 + [enjoyed_pat] + [None] * 7 + [author_note_pat] * 2 + [enjoyed_pat] * 2 + [None] + [about_author_pat] + [ack_pat]
    contents_capture = [False] * 14 + [True] * 3
    pop0 = [True] * 14 + [False] + [True] + [False]
    
    arguments = zip(range(1,18), chapter_seperators, ending_seperators, contents_capture, pop0)
    
    docs = {}
    for i, chapter_seperator, ending_seperator, contents_captured, pop0 in arguments:
        docs[i] = split_text(raw_docs[i], chapter_seperator, contents_captured, pop0, ending_seperator)
        
    dresden = []
    ch_book = []
    names = []
    for book in range(1,18):
        for idx, ch in enumerate(docs[book]):
            ch_book.append(book)
            names.append(str(book) + '.' + str(idx + 1))
            dresden.append(ch)
    
    return({k : {"book" : vch_book, "text" : vdresden} for k, vch_book, vdresden in zip(names, ch_book, dresden)})