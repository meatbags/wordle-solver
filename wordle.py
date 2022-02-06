# WORDLE SOLVER

from random import randrange
from ruleset import Ruleset
from filter import Filter

class Wordle:
    def __init__(self):
        # settings
        self.maxAttempts = 100
        self.silent = True

        # word lists
        self.words = [w.split(' ')[0] for w in self.load('data/words_ordered.txt')]
        self.wordCount = len(self.words)
        print("Words:", self.wordCount)

        # rules
        self.rules = Ruleset()

        # stats
        split = lambda x: [y for y in x]
        self.vowels_most_common = split('eaoiu')
        self.consonants_most_common = split('rtlsndycphmbgfkwvzxjq')
        self.letter_most_common = split('earoitlsnduycphmbgfkwvzxjq')
        self.letter_most_words = split('earoitlsnduycphmgbkfwvxzjq')
        self.letter_1 = split('scbpatfdmgrlhweonvuikjqyzx')
        self.letter_2 = split('aoeiurlhntpwcmydsbxgvkfqjz')
        self.letter_3 = split('aiorenultsdmpcgbvwykfxzhjq')
        self.letter_4 = split('enaisrltocugmdkpfvbhzwyxjq')
        self.letter_5 = split('yedrtnlhaokpmsgcifxwbuzvjq')

    def load(self, filename):
        words = []
        for word in open(filename).readlines():
            if word[0] == '#':
                continue
            words.append(word.replace('\n', ''))
        return words

    def save(self, filename, data):
        open(filename, 'w').write(data)

    def runWithInput(self):
        words = self.words
        filter = Filter()
        self.suggestWords()
        guess = 1
        while True:
            print('GUESS #' + str(guess) + '\n')
            word = input('word: ').lower()
            score = [int(x) for x in input('result: ')]
            filter.process(word, score)
            words = self.filterCandidates(words, filter)
            remain = len(words)
            if remain > 1:
                print('potential words ({}): {}\n'.format(remain, ' '.join([w.upper() for w in words])))
                self.suggestWords(words)
                guess += 1
            elif remain == 0:
                print('word not found\n')
                break
            else:
                print('solution:', words[0].upper(), '\n')
                break

    def run(self, n, target=False):
        randomTarget = target == False
        record = []
        for i in range(n):
            if randomTarget:
                target = self.words[randrange(self.wordCount)]
            res = self.solve(target)
            record.append(res)
        print('\nRuns=', len(record), 'Average=', sum(record)/len(record), '\n')

    def profileWords(self, set):
        for word in self.words:
            if any(p[0] == word for p in self.wordProfiles):
                continue
            self.profileWord(word, set)

    def profileWord(self, word, set):
        # get average score
        record = []
        for target in set:
            if target == word:
                continue
            res = self.solve(target, word, False)
            record.append(res)
        avg = sum(record)/len(record)
        avg = round(avg * 1000) / 1000
        print('Word:', word.upper(), 'Avg:', avg, 'Samples=', len(record))

        # update profiles and save
        result = [word, avg, len(set)]
        index = -1
        for i in range(len(self.wordProfiles)):
            if self.wordProfiles[i][0] == word:
                index = i
                break
        if index == -1:
            self.wordProfiles.append(result)
        else:
            self.wordProfiles[index] = result
        data = '\n'.join(["{} {} {}".format(p[0], p[1], p[2]) for p in self.wordProfiles])
        self.save('data/word_profiles_set.txt', data)

    def sortByPerformance(self, words):
        items = []
        for word in words:
            item = [word, 10]
            for i in range(len(self.wordProfiles)):
                if self.wordProfiles[i][0] == word:
                    item[1] = self.wordProfiles[i][1]
                    break
            items.append(item)
        items.sort(key=lambda x:x[1])
        return [item[0] for item in items]

    def suggestWords(self, sortedWords=False):
        n = 15
        words = sortedWords
        if not words:
            words = [w for w in self.words]
        filter0 = ['s']
        filter1 = self.letter_most_common[:1] + ['s']
        filter2 = self.letter_most_common[:2] + ['s']
        filter3 = self.letter_most_common[:3] + ['s']
        words0 = self.filterExcludes(words, filter0)
        words1 = self.filterExcludes(words, filter1)
        words2 = self.filterExcludes(words, filter2)
        words3 = self.filterExcludes(words, filter3)
        print('Best brute-force words:', ' '.join([words[i].upper() for i in range(min(n, len(words)))]))
        print('Without {}:'.format(''.join(filter0).upper()), ' '.join([words0[i].upper() for i in range(min(n, len(words0)))]))
        print('Without {}:'.format(''.join(filter1).upper()), ' '.join([words1[i].upper() for i in range(min(n, len(words1)))]))
        print('Without {}:'.format(''.join(filter2).upper()), ' '.join([words2[i].upper() for i in range(min(n, len(words2)))]))
        print('Without {}:'.format(''.join(filter3).upper()), ' '.join([words3[i].upper() for i in range(min(n, len(words3)))]))
        print()

    def selectWord(self, words, filter):
        count = len(words)
        attempts = filter.getAttempts()
        word = filter.getLastWord()

        # first word
        if attempts == 0:
            word = self.words[0]

        # apply decision-making ruleset
        else:
            if count <= self.rules.guess_at_remaining or attempts >= self.rules.guess_at_attempts:
                for w in words:
                    if not filter.isChecked(w):
                        word = w
                        break
            elif self.rules.pick_next_from_candidates:
                for w in words:
                    if not filter.isChecked(w):
                        word = w
                        break
            else:
                # pick completely random word
                while filter.isChecked(word):
                    word = self.words[randrange(len(self.words))]

        return word

    def solve(self, target, word=False, printResult=True):
        candidates = self.words
        filter = Filter()

        if not word:
            word = self.selectWord(self.words, filter)

        while filter.getAttempts() < self.maxAttempts:
            # check next word
            score = self.check(word, target)
            filter.process(word, score)

            # check done
            attempts = filter.getAttempts()
            scorePrintout = ' '.join([word[i] + '=' + str(score[i]) for i in range(5)])
            self.print('\nGUESS #{} {} Score:{}'.format(attempts, word.upper(), scorePrintout))
            if word == target:
                self.print('FOUND: ' + target.upper())
                break

            # filter candidates
            candidates = self.filterCandidates(candidates, filter)
            remaining = len(candidates)
            word = self.selectWord(candidates, filter)

            self.print('Candidates: {}'.format(remaining))
            if filter.isChecked(word):
                print('ERROR -- NO RESULT FOUND')
                break

        attempts = filter.getAttempts()
        if printResult:
            print('->'.join(filter.wordsChecked) + '->' + target, attempts)
        return attempts

    def filterCandidates(self, words, filter):
        # filter by included letters
        words = self.filterIncludes(words, filter.includesLetters)
        self.print('Candidates including ' + ''.join(filter.includesLetters).upper() + ' = ' + str(len(words)))

        # filter by excluded letters
        words = self.filterExcludes(words, filter.excludesLetters)
        self.print('Candidates excluding' + ''.join(filter.excludesLetters).upper() + ' = ' + str(len(words)))

        # filter by letters with known index
        for i in range(5):
            if not filter.known[i]:
                continue
            letter = filter.known[i]
            words = self.filterAtIndex(words, letter, i)
            self.print("Candidates with {} at {} = {}".format(letter.upper(), i+1, len(words)))

        # filter by letters excluding known indices
        known = filter.getKnownIndices()
        blocked = ','.join([str(i+1) for i in known])
        if len(known):
            for letter in filter.includesLetters:
                if letter in filter.known:
                    continue
                words = self.filterIncludesNotAtIndex(words, letter, known)
                self.print('Candidates with {} not at {} = {}'.format(letter.upper(), blocked, len(words)))

        # filter by letters not at index
        for i in range(len(filter.notAt)):
            group = filter.notAt[i]
            for letter in group:
                words = self.filterNotAtIndex(words, letter, i)
                self.print('Candidates with {} not at {} = {}'.format(letter.upper(), i, len(words)))

        return words

    def check(self, word, target):
        res = [0] * 5
        for i in range(len(word)):
            if word[i] == target[i]:
                res[i] = 2
            elif word[i] in target:
                res[i] = 1
        return res

    def filterIncludes(self, words, letters):
        return list(filter(lambda word: all([l in word for l in letters]), words))

    def filterExcludes(self, words, letters):
        return list(filter(lambda word: all(l not in word for l in letters), words))

    def filterAtIndex(self, words, letter, index):
        return list(filter(lambda word: word[index] == letter, words))

    def filterNotAtIndex(self, words, letter, index):
        return list(filter(lambda word: word[index] != letter, words))

    def filterIncludesNotAtIndex(self, words, letter, invalid):
        func1 = lambda word: letter in word
        func2 = lambda word: all(word[i] != letter for i in invalid)
        words = list(filter(func1, words))
        words = list(filter(func2, words))
        return words

    def print(self, msg):
        if not self.silent:
            print(msg)
