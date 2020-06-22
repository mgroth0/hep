from pybtex.database import BibliographyData, Entry, parse_string
# bib_data = BibliographyData({
#     'article-minimal': Entry('article', [
#         ('author', 'L[eslie] B. Lamport'),
#         ('title', 'The Gnats and Gnus Document Preparation System'),
#         ('journal', "G-Animal's Journal"),
#         ('year', '1986'),
#     ]),
# })

# noinspection SpellCheckingInspection
from pybtex.plugin import find_plugin
bib_data: BibliographyData = parse_string(
    """
    @inproceedings{de2002development,
      title={Development of a Matlab software for analysis of heart rate variability},
      author={De Carvalho, João LA and Da Rocha, Adson F and de Oliveira Nascimento, Francisco Assis and Neto, J Souza and Junqueira, Luiz F},
      booktitle={6th International Conference on Signal Processing, 2002.},
      volume={2},
      year={2002},
      organization={IEEE}
    }
     """,
    # pages={1488--1491}, #page number is not parsing correctly
    'bibtex'
)


APA = find_plugin('pybtex.style.formatting', 'apa')()
HTML = find_plugin('pybtex.backends', 'html')()

def bib2html(bibliography, exclude_fields=None):
    exclude_fields = exclude_fields or []
    if exclude_fields:
        bibliography = parse_string(bibliography.to_string('bibtex'), 'bibtex')
        for entry in bibliography.entries.values():
            for ef in exclude_fields:
                if ef in entry.fields.__dict__['_dict']:
                    del entry.fields.__dict__['_dict'][ef]
    formattedBib = APA.format_bibliography(bibliography)
    return "<br>".join(entry.text.render(HTML) for entry in formattedBib)