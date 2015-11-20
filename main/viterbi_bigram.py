import math


class Token:
    """Class to represent a root or IG token."""

    def __init__(self, word):
        """
        Constructor.
        :rtype : Token
        :type word: str
        """
        self.token = word
        self.probabilities = {}

    def prob_given(self, word):
        """
        Return Pr(self.token | word).
        :rtype : float
        :param word:
        :type word: str
        """
        try:
            return self.probabilities[word]
        except KeyError:
            return 0.0

    def set_prob(self, word, p):
        """
        Set Pr(self.token | word) = p.
        :type p: float
        :type word: str
        """
        self.probabilities[word] = p

    def __str__(self):
        return 'TOKEN: %s, PROBS: %s' % (self.token, str(self.probabilities))


class Tag:
    """Class to represent a tag with root word and IG list."""

    def __init__(self, root, ig_list):
        """
        Constructor.
        :param root: str
        :param ig_list: list of lists, e.g. [[ig1, ig2], [ig3], ...]
        """
        assert isinstance(root, str)
        self.root = root
        assert isinstance(ig_list, list)
        self.igs = ig_list

    def __str__(self):
        return 'ROOT:%s, IGs:%s' % (self.root, str(self.igs))

    @property
    def last_ig(self):
        """
        Return the last IG in IG list.
        :rtype : str
        :type self: Tag
        """
        return self.igs[-1]

    def get_ig(self, k):
        """
        Return the IG at the position k in the IG list.
        :rtype : str
        :type k: int
        """
        return self.igs[k]

    @property
    def num_ig(self):
        """
        Return the number of IGs.
        :rtype : int
        :type self: object
        """
        return len(self.igs)

    def __hash__(self):
        return hash((self.root, ) + tuple(self.igs))

    def __eq__(self, other):
        return self.root == other.root and any(map(lambda v: v in self.igs, other.igs))

    def __repr__(self):
        return '%s+%s ' % (self.root, '+'.join(self.igs))


class BaselineModel:
    """Class to represent bi-gram baseline model."""

    def __init__(self, root_list, root_counts, ig_list, ig_counts, is_prob_calculated=False):
        """
        Constructor.
        :type root_list: list of root strings
        :type ig_list: list of IG strings
        :type root_counts: dictionary of dictionary, e.g. {root1: {root1: count, root2: count, ...}, ...}
        :type ig_counts: dictionary of dictionary, e.g. {ig1: {ig1: count, ig2: count, ...}, ...}
        """
        assert isinstance(root_list, list)
        self.roots = root_list
        assert isinstance(ig_list, list)
        self.igs = ig_list
        assert isinstance(root_counts, dict)
        self.root_tokens = BaselineModel._build_tokens(root_list, root_counts, is_prob_calculated)
        assert isinstance(ig_counts, dict)
        self.ig_tokens = BaselineModel._build_tokens(ig_list, ig_counts, is_prob_calculated)

    @staticmethod
    def _build_tokens(token_list, token_counts, is_prob_calculated):
        """
        Create and return a list of Token objects.
        :param token_list: list of strings, e.g. roots or IGs
        :param token_counts: dictionary of dictionary with token counts,
        :return: list of Token objects.
        """
        ret_list = []
        assert isinstance(token_list, list)
        for token1 in token_list:
            root = Token(token1)
            for token2 in token_list:
                assert isinstance(token_counts, dict)
                try:
                    if not is_prob_calculated:
                        prob = -math.log(float(token_counts[token2][token1]) / float(sum(token_counts[token2].values())))
                    elif is_prob_calculated:
                        prob = token_counts[token2][token1]
                    root.set_prob(token2, prob)
                    # print('-ln[Pr(%s | %s)] = %s' % (token1, token2, root.prob_given(token2)))
                except KeyError:
                    pass
            ret_list.append(root)
        return ret_list

    def _get_token(self, tag, is_root=True, pos=0):
        """
        Return token at position that corresponds to tag.
        :param tag: Tag object
        :param is_root: boolean
        :param pos: int, position
        :return: Token or None
        """
        tokens = self.root_tokens if is_root else self.ig_tokens
        for token in tokens:
            if is_root and token.token == tag.root:
                return token
            elif not is_root and token.token == tag.get_ig(pos):
                return token
        return None

    def baseline_model(self, tag1, tag2):
        """
        Return Pr(tag2 | tag1) according to a baseline bi-gram model.
        :type tag1: Tag
        :type tag2: Tag
        """
        root_token = self._get_token(tag2)
        root_prob, ig_prob = 0.0, 1.0
        if root_token:
            root_prob = root_token.prob_given(tag1.root)
        for k in range(tag2.num_ig):
            ig_token = self._get_token(tag2, is_root=False, pos=k)
            if ig_token:
                ig_prob += ig_token.prob_given(tag1.last_ig)
                # print("Baseline: Pr[%s | %s] = %f" % (tag2, tag1, ig_prob))
        return root_prob + ig_prob

    def log_prob(self, word_seq, root_seq, ig_seq):
        """
        Return log_prob for a given sentence.
        :rtype : float
        :param word_seq: list of words (word is a string).
        """
        log_probability = 0
        assert isinstance(word_seq, list)
        assert isinstance(root_seq, list)
        assert isinstance(ig_seq, list)
        for index in range(1, len(word_seq)):
            tag1 = Tag(root_seq[index - 1], ig_seq[index - 1])
            tag2 = Tag(root_seq[index], ig_seq[index])
            log_probability += self.baseline_model(tag1, tag2)
        return log_probability


def print_analysis():
    analyzed = ''
    for i in range(len(ig_sequence)):
        analyzed += '%s+%s ' % (root_sequence[i], '+'.join(ig_sequence[i]))
    print('-ln[Pr(%s | %s)] = %f' % (analyzed, ' '.join(word_sequence), log_prob))


class Viterbi:
    def __init__(self, ambiguous_seq, word_seq):
        self.ambiguous_seq = ambiguous_seq
        self.word_seq = word_seq

        # Init data structures
        self.delta = [{}]
        self._sentence_tag = Tag('.', ['sent'])
        self.delta[0][self._sentence_tag] = 0.0
        self.psi = [{}]
        self.viterbi_path = [None] * len(self.ambiguous_seq)
        self.viterbi_path[-1] = self._sentence_tag
        self.viterbi_path[0] = self._sentence_tag

    def train(self, model):
        """
        :type model:BaselineModel
        """
        for pos in range(1, len(self.ambiguous_seq)):
            self.delta.append({})
            self.psi.append({})
            for tag in self.ambiguous_seq[pos]:
                max_delta = 0.0
                max_tag = self.ambiguous_seq[pos][0]
                for prev_tag in self.ambiguous_seq[pos - 1]:
                    cur_delta = self.delta[pos - 1][prev_tag] + model.baseline_model(tag, prev_tag)
                    if cur_delta > max_delta:
                        max_delta = cur_delta
                        max_tag = prev_tag
                self.delta[pos][tag] = max_delta
                self.psi[pos][tag] = max_tag

    @property
    def path(self):
        for j in range(len(self.word_seq) - 2, 0, -1):
            # try:
            tag = self.psi[j + 1][self.viterbi_path[j + 1]]
            self.viterbi_path[j] = tag
            # except KeyError:
            #     pass
        return self.viterbi_path

    @property
    def probability(self):
        return self.delta[-1][self._sentence_tag]


if __name__ == "__main__":
    from main.viterbi_bigram_data import roots, root_counts, igs, ig_counts
    from main.viterbi_bigram_data import word_sequence, root_sequence, ig_sequence
    from main.viterbi_bigram_data import amb_sequence

    # Build bigram model
    bigram_model = BaselineModel(roots, root_counts, igs, ig_counts)
    log_prob = bigram_model.log_prob(word_sequence, root_sequence, ig_sequence)

    print_analysis()

    # Build Viterbi tagger
    viterbi = Viterbi(amb_sequence, word_sequence)
    viterbi.train(model=bigram_model)
    print('Viterbi probability: %f' % viterbi.probability)
    print('Viterbi path: %s' % viterbi.path)