
# NOTE: using non-plural library

from random import randrange
source = open('data/data_no_plurals.txt')
library = source.readlines()

wordSet = []
while len(wordSet) < 1000:
    word = library[randrange(len(library))]
    word = word.replace('\n', '')
    if word not in wordSet:
        wordSet.append(word)
open('data/word_set.txt', 'w').write('\n'.join(wordSet))

#no_repeat = [x for x in library if all([x.count(l) == 1 for l in x])]
#print("No repeat", len(no_repeat))
#open('data/data_no_plurals_no_repeat.txt', 'w').write(''.join(no_repeat))

wordCount = len(library)
letterCount = wordCount * 5
dict = [{'letter':chr(i+97), 'count':0, 'index':[0,0,0,0,0]} for i in range(26)]

def toPercent(x):
    return str(round(x * 1000) / 10) + '%'

def profile(letter):
    words = 0
    total = 0
    index = [0] * 5
    for word in library:
        if not letter in word:
            continue
        words += 1
        for i in range(5):
            if word[i] == letter:
                total += 1
                index[i] += 1

    out1 = '| ' + letter.upper()
    out2 = '| {:>4} {:>5}'.format(total, toPercent(total/letterCount))
    out3 = '| {:>4} {:>5}'.format(words, toPercent(words/wordCount))
    p = [toPercent(x/wordCount) for x in index]
    out4 = '| {:>5} {:>5} {:>5} {:>5} {:>5}'.format(p[0], p[1], p[2], p[3], p[4])
    print(out1, out2, out3, out4)
    return [letter, words, total, index]

out1 = '   ';
out2 = '   OCCURENCES';
out3 = '    IN WORDS';
out4 = '     1     2     3     4     5'
print()
print(out1, out2, out3, out4)
print('-' * 61)

profiles = []
for i in range(26):
    letter = chr(97 + i)
    profiles.append(profile(letter))

print()
profiles.sort(key=lambda e:e[2])
print('MOST COMMON:  ', ''.join([ x[0] for x in profiles[::-1] ]))
profiles.sort(key=lambda e:e[1])
print('IN MOST WORDS:', ''.join([ x[0] for x in profiles[::-1] ]))
profiles.sort(key=lambda e:e[3][0])
print('AT POSITION 1:', ''.join([ x[0] for x in profiles[::-1] ]))
profiles.sort(key=lambda e:e[3][1])
print('AT POSITION 2:', ''.join([ x[0] for x in profiles[::-1] ]))
profiles.sort(key=lambda e:e[3][2])
print('AT POSITION 3:', ''.join([ x[0] for x in profiles[::-1] ]))
profiles.sort(key=lambda e:e[3][3])
print('AT POSITION 4:', ''.join([ x[0] for x in profiles[::-1] ]))
profiles.sort(key=lambda e:e[3][4])
print('AT POSITION 5:', ''.join([ x[0] for x in profiles[::-1] ]))

print()
