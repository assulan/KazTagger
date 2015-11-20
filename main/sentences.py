from main.viterbi_bigram import Tag

ambiguous_sentences = [
    ([
        [Tag('.', ['sent'])],
        [Tag('Азамат', ['np', 'ant', 'm', 'nom'])],
        [Tag('мен', ['cnjcoo'])],
        [Tag('Айгуль', ['np', 'ant', 'f', 'nom'])],
        [Tag('ойна', ['v', 'tv', 'ger_past', 'acc'])],
        [Tag('жақсы$көр', ['v', 'tv', 'aor', 'p3', 'pl'])],
        [Tag(',', ['cm'])],
        [Tag('олар', ['prn', 'pers', 'p3', 'pl', 'nom'])],
        [Tag('әрдайым', ['adv'])],
        [Tag('үлкен', ['adj'])],
        [Tag('үй', ['n', 'gen'])],
        [Tag('алд', ['n', 'px3sp', 'loc', 'attr'])],
        [Tag('бақша', ['n', 'loc'])],
        [Tag('бірге', ['adv'])],
        [Tag('ойна', ['v', 'tv', 'aor', 'p3', 'pl'])],
        [Tag('.', ['sent'])]
    ], '. Азамат пен Айгүл ойнағанды жақсы$көреді , олар әрдайым үлкен үйдің алдындағы бақшада бірге ойнайды .'),

    ([
        [Tag('.', ['sent'])],
        [Tag("Норвегия", ['np', 'top', 'gen'])],
        [Tag("елорда", ['n', 'px3sp', 'nom']), Tag("е", ['cop', 'aor', 'p3', 'pl'])],
        [Tag("Осло", ['np', 'top', 'attr']), Tag("Осло", ['np', 'top', 'nom'])],
        [Tag("қала", ['n', 'px3sp', 'loc'])],
        [Tag("өт", ['v', 'tv', 'aor', 'p3', 'sg']), Tag("өт", ['v', 'iv', 'aor', 'p3', 'sg'])],
        [Tag('.', ['sent'])]
    ], '. Норвегияның елордасы Осло қаласында өтеді .'),

    ([
        [Tag('.', ['sent'])],
        [Tag('Азамат', ['np', 'ant', 'm', 'nom'])],
        [Tag('мен', ['cnjcoo']), Tag('мен', ['post'])],
        [Tag('Айгуль', ['np', 'ant', 'f', 'nom'])],
        [Tag('ойна', ['v', 'tv', 'ger_past', 'acc']), Tag('ойна', ['v', 'tv', 'gpr_past', 'subst', 'acc'])],
        [Tag('жақсы$көр', ['v', 'tv', 'aor', 'p3', 'pl'])],
        [Tag('.', ['sent'])]
    ], '. Азамат пен Айгүл ойнағанды жақсы$көреді .')

]
