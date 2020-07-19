from pybtex.database import BibliographyData, parse_string
# bib_data = BibliographyData({
#     'article-minimal': Entry('article', [
#         ('author', 'L[eslie] B. Lamport'),
#         ('title', 'The Gnats and Gnus Document Preparation System'),
#         ('journal', "G-Animal's Journal"),
#         ('year', '1986'),
#     ]),
# })

# noinspection SpellCheckingInspection

bib_data: BibliographyData = parse_string(
    """
    @inproceedings{carvalho2002,
      title={Development of a Matlab software for analysis of heart rate variability},
      author={De Carvalho, João LA and Da Rocha, Adson F and de Oliveira Nascimento, Francisco Assis and Neto, J Souza and Junqueira, Luiz F},
      booktitle={6th International Conference on Signal Processing, 2002.},
      volume={2},
      year={2002},
      organization={IEEE},
      pages={1488--1491},
      doi          = {10.1109/ICOSP.2002.1180076},
      publisher = {IEEE},
      url          = {https://github.com/perakakis/HEPLAB/blob/master/Documentation/Articles/icsp2002_ecglab.pdf}
    },
      murl = {https://u.nu/qy-4k}
    }
    
    @software{perakakis2019,
      author       = {Pandelis Perakakis},
      title        = {HEPLAB: a Matlab graphical interface for the 
                       preprocessing of the heartbeat-evoked potential},
      month        = apr,
      year         = 2019,
      publisher    = {Zenodo},
      version      = {v1.0.0},
      doi          = {10.5281/zenodo.2649943},
      url          = {https://doi.org/10.5281/zenodo.2649943}
    },
      murl = {https://u.nu/-r1x7}
     """,
    'bibtex'
)

# things that didnt work:
# (de2002development) pages={1488--1491}, #page number is not parsing correctly
# (pandelis_perakakis_2019_2649943) couldnt use software type

