# Filter

class Filter:
    def __init__(self):
        self.wordsChecked = []
        self.includesLetters = []
        self.excludesLetters = []
        self.known = [False] * 5
        self.notAt = [[],[],[],[],[]]

    def isChecked(self, word):
        return word in self.wordsChecked

    def getKnownIndices(self):
        return [i for i in range(5) if self.known[i]]

    def getAttempts(self):
        return len(self.wordsChecked)

    def getLastWord(self):
        if len(self.wordsChecked):
            return self.wordsChecked[-1]
        return False

    def process(self, word, score):
        self.wordsChecked.append(word)
        for i in range(5):
            letter = word[i]
            res = score[i]
            if res == 2:
                self.known[i] = letter
                if letter not in self.includesLetters:
                    self.includesLetters.append(letter)
            elif res == 1:
                if letter not in self.includesLetters:
                    self.includesLetters.append(letter)
                if letter not in self.notAt[i]:
                    self.notAt[i].append(letter)
            else:
                if letter not in self.includesLetters and letter not in self.excludesLetters:
                    self.excludesLetters.append(letter)
