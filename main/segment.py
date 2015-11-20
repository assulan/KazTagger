# coding=utf-8
__author__ = 'Assulan Nurkas'
import re
import os
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LM_CMD = '/home/aseke/srilm/bin/i686-m64/ngram-count'
# LM_CMD = 'ngram-count'
LM_CORPUS_DIR = os.path.join(BASE_DIR, 'lm_corpus')
SMALL_CORPUS = os.path.join(BASE_DIR, 'small_tagged_corpus')
BIG_CORPUS = os.path.join(BASE_DIR, 'big_tagged_corpus')
root_corpus, ig_corpus = '', ''


class Sentence:
    def __init__(self):
        """
        Sentence consists of list of roots (strings), and list of Inflectional Group objects.
        """
        self.roots = []
        self.igs = []

    def __str__(self):
        return 'Roots: %s\nIGs: %s\n' % (str(self.roots), str(self.igs))

    def add_root(self, root):
        self.roots.append(root)

    def add_ig(self, ig):
        self.igs.append(ig)

    def add_copula_ig(self, ig):
        """
        Add copula like IGs to last IG group.
        :param ig: str
        """
        self.igs[-1].add(ig)


class InflectionalGroup:
    def __init__(self, group):
        """
        Inflectional Group is a list of tags.
        :param group: list of strings.
        """
        assert isinstance(group, list)
        self.group = group

    def add(self, ig):
        assert isinstance(ig, str)
        self.group.append(ig)

    def __str__(self):
        return ' '.join(self.group)

    def __repr__(self):
        return self.__str__()

    @property
    def num(self):
        return len(self.group)

    @property
    def last(self):
        return self.group[-1]


def process_file(fpath, ngram=2):
    """
    Process a file, and extract words, roots, and IGs.
    :param fpath: file path
    :param ngram:
    :return: list of Sentence objects
    """

    class TokenType:
        word = 1
        root = 2
        ig = 3

    def extract(category):
        # Define regex patterns for word, root, and ig
        """
        Extract word, root, or IG from a line in tagged corpus file.
        :param category: TokenType
        :return: tuple (word, None) or (root, IG) or (None, copula IG).
        """
        pattern_word = r'"<(.*)>"'
        pattern_root_ig = r'\t(.*?)(?=\s@)'
        pattern = ''
        if category == TokenType.word:
            pattern = pattern_word
        elif category == TokenType.root or category == TokenType.ig:
            pattern = pattern_root_ig

        match = re.match(pattern, line)
        if match:
            ret_val = match.group()
            if ret_val.count('\t') >= 2:
                # Case '\t\te cop aor p3 sg' or similar, i.e. part of IG
                return None, ret_val.strip('\t').replace('"', '').replace(' ', '$')
            elif ret_val.count('\t') == 1:
                # Case '\tжегіз v tv prc_perf', i.e. root followed by IG
                ret_val = ret_val.strip('\t')
                index = ret_val.rindex('"')
                ret_val = ret_val.replace('"', '')
                root = ret_val[:index].strip().replace(' ', '$')
                ig = ret_val[index:].strip().replace(' ', '$')
                return root, ig
            # Case of just a word
            return ret_val.replace('"', '').replace('<', '').replace('>', ''), None
        return None, None

    def segment(my_ig):
        """
        Segment ig based on segmentation rules.
        :param my_ig: str
        :return: list of strings
        """
        segmentation_rules = ['subst', 'attr', 'advl', 'ger_', 'gpr_', 'gna_', 'prc_']
        ret_val = []
        while my_ig:
            positions = sorted([my_ig.index(rule) for rule in segmentation_rules if rule in my_ig])
            try:
                pos = positions[0] if positions[0] > 0 else positions[1]
            except IndexError:
                # the last IG
                pos = len(my_ig)
            ret_val.append(my_ig[:pos].strip('$'))
            my_ig = my_ig[pos:]
        return ret_val

    COPULA = 'COPULA'
    sentences = []
    last = None
    with open(fpath, 'r', encoding='utf-8') as f:
        words, roots, igs = [], [], []
        for line in f:
            # process line
            word, _ = extract(TokenType.word)
            root, ig = extract(TokenType.root)
            if word:
                words.append(word)
                last = TokenType.word
            if root:
                roots.append(root)
                last = TokenType.root
            if ig:
                if last == TokenType.ig:
                    # the case of 'e cop ...' and the like
                    igs.append('COPULA%s' % ig)
                else:
                    igs.append(ig)
                last = TokenType.ig
            if ig == 'sent':
                # Create a sentence object and segment its IGs
                sentence = Sentence()
                for root in roots:
                    sentence.add_root(root)
                for the_ig in igs:
                    assert isinstance(the_ig, str)
                    if the_ig.startswith(COPULA):
                        # Strip copula marker and append to previous IG
                        the_ig = the_ig.replace(COPULA, '')
                        sentence.add_copula_ig(the_ig)
                    else:
                        ig_group = segment(the_ig)
                        inflectional_group = InflectionalGroup(ig_group)
                        sentence.add_ig(inflectional_group)
                sentences.append(sentence)
                words, roots, igs = [], [], []
    return sentences


def stats(sentences):
    """
    Calculate statistics: dictionary of IG lengths with count of words, and
    list of integers for each sentence.
    Example:
    {1: 100, 2: 50, 3: 145} -> 100 words have 1 IG, 50 words have 2 IGs, etc.
    [[1,1,2,1], ...] -> The first sentence consists of 4 words, and each word has
    1, 1, 2, 1 IGs respectively.
    :param sentences: list of Sentence objects.
    :return: tuple with dict of counts, and list of lists
    """
    ig_counts = {}
    ig_count_sequences = []
    for sent in sentences:
        ig_count_sequences.append([ig.num for ig in sent.igs])
        for ig in sent.igs:
            assert isinstance(ig.group, list)
            num_ig = len(ig.group)
            if num_ig in ig_counts.keys():
                ig_counts[num_ig] += 1
            else:
                ig_counts[num_ig] = 1
    return Counter(ig_counts), ig_count_sequences


def prepare_corpus(is_test=True, ngram=2):
    """
    Go through all files in tagged corpus directory, and extract root and IG corpus, and
    write them to files in LM_CORPUS_DIR. Set global variables root_corpus and ig_corpus.
    Uses small corpus directory if testing.
    :param is_test: boolean
    :param ngram: int
    """
    global root_corpus, ig_corpus
    tagged_corpus_dir = SMALL_CORPUS if is_test else BIG_CORPUS
    num_sent = 0
    all_stats = Counter()
    count_sequences = []
    # Clean the files first
    open(os.path.join(LM_CORPUS_DIR, 'roots.txt'), 'w').close()
    open(os.path.join(LM_CORPUS_DIR, 'igs.txt'), 'w').close()
    fp_root = open(os.path.join(LM_CORPUS_DIR, 'roots.txt'), 'a')
    fp_ig = open(os.path.join(LM_CORPUS_DIR, 'igs.txt'), 'a')
    for file_name in os.listdir(tagged_corpus_dir):
        # For each file do ...
        file_path = os.path.join(tagged_corpus_dir, file_name)
        sentences = process_file(file_path, ngram=ngram)
        num_sent += len(sentences)
        all_igs = []
        for s in sentences:
            root_corpus += '%s ' % ' '.join(s.roots)
            fp_root.write('%s ' % (' '.join(s.roots)))
            for ig in s.igs:
                assert isinstance(ig, InflectionalGroup)
                all_igs.append(ig)
        for i in range(1, len(all_igs) - 1):
            first = all_igs[i - 1]
            second = all_igs[i]
            for ig in second.group:
                fp_ig.write('%s %s\n' % (first.last, ig))
        ig_corpus += '%s ' % ' '.join([str(ig) for ig in all_igs])
        cur_stats, cur_count_sequences = stats(sentences)
        all_stats += cur_stats
        count_sequences += cur_count_sequences
    fp_root.close()
    fp_ig.close()
    print('Total # of sentences: ', num_sent)
    for key, val in all_stats.items():
        print('Words with %d IG(s): %d' % (key, val))
    with open('stats.txt', 'w') as f:
        for counts in count_sequences:
            f.write('%s\n' % ','.join([str(n) for n in counts]))
    print('Created root and IG bigram corpus. Done.')


def language_model(ngram=2):
    """
    Return dictionary with root and IG probabilities.
    Uses SRILM ngram-count to build LM and calculate probabilities.
    :param ngram:
    :return: dict
    """

    def get_ngram_probs():
        """
        Process .arpa file created by SRILM ngram-count and extract bigrams.
        :return:
        """
        # TODO make it work for general case of ngrams. Now works only for bigrams.
        probs = {}
        to_process = False
        with open(fp_arpa, 'r') as f:
            for line in f:
                line = line.strip('\n')
                if ('\%d-grams:' % ngram) in line:
                    # The start of ngrams of interest
                    to_process = True
                    continue
                elif to_process and not line:
                    # finish
                    return probs
                elif to_process and line:
                    line = line.split()
                    # TODO this works only for bigrams now.
                    prob, first_word, second_word = float(line[0]), line[1], line[2]
                    if first_word not in probs.keys():
                        probs[first_word] = {second_word: prob}
                    else:
                        probs[first_word][second_word] = prob
        return probs

    # Run SRILM ngram-count on roots.txt and igs.txt files.
    import subprocess
    file_paths = [os.path.join(LM_CORPUS_DIR, 'roots.txt'), os.path.join(LM_CORPUS_DIR, 'igs.txt')]
    root_probs, ig_probs = {}, {}
    for i, fp in enumerate(file_paths):
        fp_arpa = fp.replace('.txt', '.arpa')
        open(fp_arpa, 'w').close()
        base_cmd = '%s -order %d -no-sos -no-eos -text %s -lm %s 2>/dev/null' % (LM_CMD, ngram, fp, fp_arpa)
        subprocess.Popen([base_cmd], shell=True)
        if i == 0:
            root_probs = get_ngram_probs()
        else:
            ig_probs = get_ngram_probs()
    return root_probs, ig_probs


if __name__ == '__main__':
    from main.viterbi_bigram import BaselineModel, Viterbi
    from main.sentences import ambiguous_sentences
    prepare_corpus(is_test=True, ngram=2)
    root_probs, ig_probs = language_model(ngram=2)

    print('\nBaseline model ... \n')
    # Build baseline model
    bigram_model = BaselineModel(root_corpus.split(), root_probs, ig_corpus.split(), ig_probs, is_prob_calculated=True)

    for amb_seq, word_seq in ambiguous_sentences:
        # Build Viterbi tagger
        viterbi = Viterbi(amb_seq, word_seq.split())
        viterbi.train(model=bigram_model)
        print('Sentence: %s' % word_seq)
        print('Viterbi probability: %f' % viterbi.probability)
        print('Viterbi path: %s' % viterbi.path)
        print('-' * 20)