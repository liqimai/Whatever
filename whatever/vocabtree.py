class VocabTree(dict):
    def __init__(self, char='', isword=False):
        super(VocabTree, self).__init__()
        self.char = char
        self.isword = isword

    def add_word(self, word):
        if len(word):
            self.setdefault(word[0], VocabTree(word[0], False)).add_word(word[1:])
        else:
            self.isword = True

    def __to_word_list(self, word_list, prefix=''):
        prefix += self.char
        if self.isword:
            word_list.append(prefix)
        for children in self.itervalues():
            children.__to_word_list(word_list, prefix)
        return word_list

    def to_word_list(self, prefix=''):
        return self.__to_word_list([],prefix)

    def find_subtree(self, prefix=''):
        if prefix == '':
            return self
        elif prefix[0] in self:
            return self[prefix[0]].find_subtree(prefix[1:])
        else:
            return VocabTree()
    def find_by_prefix(self, prefix):
        return self.find_subtree(prefix).to_word_list(prefix[:-1])

if __name__ == '__main__':
    vbt = VocabTree()
    vbt.add_word('aa')
    vbt.add_word('ab')
    vbt.add_word('ac')
    vbt.add_word('ba')
    vbt.add_word('bb')
    vbt.add_word('bc')
    vbt.add_word('ca')
    vbt.add_word('cb')
    vbt.add_word('cc')
    print vbt.to_word_list()
    print vbt.find_subtree('a').to_word_list()
    print vbt.find_subtree('b').to_word_list()
    print vbt.find_subtree('cc').to_word_list('c')
    print vbt.find_subtree('d').to_word_list()
    print vbt.find_subtree('ad').to_word_list()
    pass