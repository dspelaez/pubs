from __future__ import unicode_literals

import os
import re
import textwrap

from . import color
from .bibstruct import TYPE_KEY


CHARS = re.compile('[{}\n\t\r]')


def sanitize(s):
    return CHARS.sub('', s)


# should be adaptated to bibtexparser dicts
def person_repr(p):
    raise NotImplementedError
    return ' '.join(s for s in [
        ' '.join(p.first(abbr=True)),
        ' '.join(p.last(abbr=False)),
        ' '.join(p.lineage(abbr=True))] if s)


def short_authors(bibdata):
    try:
        authors = [p for p in bibdata['author']]
        if len(authors) < 3:
            return ' and '.join(authors)
        else:
            return authors[0] + (' et al.' if len(authors) > 1 else '')
    except KeyError:  # When no author is defined
        return ''

def wrap_text(string, compress=True):
    with os.popen('stty size', 'r') as win:
        rows, columns = win.read().split()
    
    maxwidth = int(0.9 * int(columns))
    if compress:
        lst = textwrap.wrap(string, maxwidth)
        if len(lst) == 1:
            return ' '.join(lst)
        else:
            return lst[0] + '...'

    else:
        return '\n   '.join(textwrap.wrap(string, maxwidth))


def bib_oneliner(bibdata):
    authors = sanitize(short_authors(bibdata))
    journal = ''
    if 'journal' in bibdata:
        journal = ' ' + bibdata['journal']
    elif bibdata[TYPE_KEY] == 'book':
        journal = ' ' + bibdata.get('publisher', '')
    elif bibdata[TYPE_KEY] == 'inproceedings':
        journal = ' ' + bibdata.get('booktitle', '')

    title = wrap_text(sanitize(bibdata.get('title', '')), compress=True)
    journal = wrap_text(sanitize(journal), compress=True)

    string = '{authors}{year}\n  \"{title}\"\n  {journal}'.format(
        authors=color.dye_out(authors, 'author'),
        title=color.dye_out(title, 'title'),
        journal=color.dye_out(journal, 'publisher'),
        year=' ({})'.format(color.dye_out(bibdata['year'], 'year'))
             if 'year' in bibdata else '')

    return string


def bib_desc(bib_data):
    article = bib_data[list(bib_data.keys())[0]]
    s = '\n'.join('author: {}'.format(p)
                  for p in article['author'])
    s += '\n'
    s += '\n'.join('{}: {}'.format(k, v) for k, v in article.items())
    return s


def paper_oneliner(p, citekey_only=False):
    if citekey_only:
        return p.citekey
    else:
        bibdesc = bib_oneliner(p.get_unicode_bibdata())
        doc_str = ''
        if p.docpath is not None:
            doc_extension = os.path.splitext(p.docpath)[1]
            doc_str = color.dye_out(
                ' [{}]'.format(doc_extension[1:] if len(doc_extension) > 1
                               else 'NOEXT'),
                'tag')
        tags = '' if len(p.tags) == 0 else '| {}'.format(
            ','.join(color.dye_out(t, 'tag') for t in sorted(p.tags)))
        return '[{citekey}] {descr}\n  {doc} {tags}\n'.format(
            citekey=color.dye_out(p.citekey, 'citekey'),
            descr=bibdesc, tags=tags, doc=doc_str)


