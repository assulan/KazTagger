# Calculate root bigrams
root_counts = {
    'ел': {'ел': 1, 'саяси': 17, 'билік': 19, 'аятолла': 50, 'қол': 45, '.': 19},
    'саяси': {'ел': 32, 'саяси': 1, 'билік': 100, 'аятолла': 18, 'қол': 4, '.': 38},
    'билік': {'ел': 47, 'саяси': 5, 'билік': 1, 'аятолла': 21, 'қол': 53, '.': 23},
    'аятолла': {'ел': 44, 'саяси': 32, 'билік': 4, 'аятолла': 1, 'қол': 73, '.': 17},
    'қол': {'ел': 13, 'саяси': 81, 'билік': 31, 'аятолла': 20, 'қол': 1, '.': 15},
    '.': {'ел': 64, 'саяси': 75, 'билік': 46, 'аятолла': 13, 'қол': 54, '.': 1}
}
roots = ['ел', 'саяси', 'билік', 'аятолла', 'қол', '.']

# Calculate IG bigrams
ig_counts = {
    'n.loc': {'n.loc': 28, 'attr': 36, 'ghi.subst.nom': 10, 'adj': 56, 'n.nom': 95, 'n.attr': 48, 'n.px3sp.loc': 53,
              'e.cop.aor.p3.sg': 77, 'sent': 1},
    'attr': {'n.loc': 91, 'attr': 88, 'ghi.subst.nom': 42, 'adj': 21, 'n.nom': 73, 'n.attr': 74, 'n.px3sp.loc': 82,
             'e.cop.aor.p3.sg': 94, 'sent': 2},
    'ghi.subst.nom': {'n.loc': 59, 'attr': 41, 'ghi.subst.nom': 24, 'adj': 64, 'n.nom': 2, 'n.attr': 67,
                      'n.px3sp.loc': 37, 'e.cop.aor.p3.sg': 29, 'sent': 3},
    'adj': {'n.loc': 66, 'attr': 69, 'ghi.subst.nom': 92, 'adj': 40, 'n.nom': 34, 'n.attr': 50, 'n.px3sp.loc': 75,
            'e.cop.aor.p3.sg': 90, 'sent': 4},
    'n.nom': {'n.loc': 51, 'attr': 46, 'ghi.subst.nom': 12, 'adj': 1, 'n.nom': 33, 'n.attr': 81, 'n.px3sp.loc': 44,
              'e.cop.aor.p3.sg': 71, 'sent': 5},
    'n.attr': {'n.loc': 79, 'attr': 16, 'ghi.subst.nom': 96, 'adj': 11, 'n.nom': 35, 'n.attr': 61,
               'n.px3sp.loc': 70,
               'e.cop.aor.p3.sg': 100, 'sent': 6},
    'n.px3sp.loc': {'n.loc': 85, 'attr': 84, 'ghi.subst.nom': 43, 'adj': 97, 'n.nom': 8, 'n.attr': 5,
                    'n.px3sp.loc': 76,
                    'e.cop.aor.p3.sg': 6, 'sent': 7},
    'e.cop.aor.p3.sg': {'n.loc': 54, 'attr': 76, 'ghi.subst.nom': 51, 'adj': 91, 'n.nom': 17, 'n.attr': 62,
                        'n.px3sp.loc': 21, 'e.cop.aor.p3.sg': 22, 'sent': 8},
    'sent': {'n.loc': 82, 'attr': 63, 'ghi.subst.nom': 11, 'adj': 65, 'n.nom': 59, 'n.attr': 84, 'n.px3sp.loc': 35,
             'e.cop.aor.p3.sg': 77, 'sent': 12}
}
igs = ['n.loc', 'attr', 'ghi.subst.nom', 'adj', 'n.nom', 'n.attr', 'n.px3sp.loc', 'e.cop.aor.p3.sg', 'sent']

# Example sentence with one of the possible analyzes per each word
word_sequence = '. елдегі саяси билік аятолла қолында .'.split(' ')
root_sequence = '. ел саяси билік аятолла қол .'.split(' ')
ig_sequence = [['sent'], ['n.loc', 'ghi.subst.nom'], ['adj'], ['n.nom'], ['n.nom'],
               ['n.px3sp.loc', 'e.cop.aor.p3.sg'],
               ['sent']]

# Our morphologically ambiguous sentence
from main.viterbi_bigram import Tag
amb_sequence = [
    [Tag('.', ['sent'])],
    [Tag('ел', ['n.loc', 'attr']), Tag('ел', ['n.loc', 'ghi.subst.nom'])],
    [Tag('саяси', ['adj'])],
    [Tag('билік', ['n.nom']), Tag('билік', ['n.attr'])],
    [Tag('аятолла', ['n.nom'])],
    [Tag('қол', ['n.px3sp.loc']), Tag('қол', ['n.px3sp.loc', 'e.cop.aor.p3.sg'])],
    [Tag('.', ['sent'])]
]