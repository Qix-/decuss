import json
import os
from os import path

TOP_LIMIT = 13
SOURCE_WORD_WEIGHT_FACTOR = 4

all_words = dict()

files = [
    'ar-latn',
    'es',
    'fr',
    'it',
    'pt-br',
    'index'
]

LETTERMAP = {
    'o': ('0',),
    'l': ('1',),
    'i': ('1',),
    's': ('5',),
    't': ('7',),
    'b': ('8','i3'),
    'g': ('9',),
    'a': ('4',),
    'for': ('4',),
    'ck': ('q',),
    'e': ('3',)
}

ZEROS = '0' * 100
def generate_alternates(word):
    keys = [k for k in LETTERMAP.keys() if k in word]
    iterations = 2 ** len(keys)

    results = []

    for i in range(1, iterations):
        bs = bin(i)[2:]
        bs = ZEROS[:len(keys) - len(bs)] + bs
        candidates = [word]

        for idx, b in enumerate(bs):
            if b == "1":
                src = keys[idx]
                dests = LETTERMAP[src]
                new_replacements = []
                candidates = [c.replace(src, dest) for c in candidates for dest in dests]

        results += candidates

    for res in set(results):
        yield res

real_count = 0
alternative_count = 0
for fname in files:
    with open(path.join(path.dirname(__file__), "cuss", f"{fname}.json"), 'r') as fd:
        words = json.load(fd)
    for word, threat in words.items():
        real_count += 1
        all_words[word] = max(threat * SOURCE_WORD_WEIGHT_FACTOR, all_words.get(word, 0))

        for alternative in generate_alternates(word):
            all_words[alternative] = max(threat - 1, all_words.get(word, 0))
            alternative_count += 1

print(f"loaded {real_count} words across {len(files)} locales (receiving a weight handicap of {SOURCE_WORD_WEIGHT_FACTOR}x)")
print(f"generated a total of {alternative_count} alternative spellings (receiving a weight penality of -1)")
print(f"{len(all_words)} total words being considered")

max_threat = max(all_words.values())
min_threat = min(all_words.values())
print(f"min threat: {min_threat}")
print(f"max threat: {max_threat}")

threat_range = max_threat - min_threat
all_words = dict(((k, (1 + (v - min_threat) / threat_range)) for (k, v) in all_words.items()))
print("weighted all words")

char_weights = dict()
char_words = dict()

for word, weight in all_words.items():
    chars = set(word)
    for c in chars:
        c = c.lower()
        char_weights[c] = char_weights.get(c, 0) + weight
        if c not in char_words: char_words[c] = set()
        char_words[c].add(word)

sorted_weights = list(sorted(char_weights.items(), key=lambda i: list(i)[1], reverse=True))
top_weights = set(map(lambda i: list(i)[0], sorted_weights[:TOP_LIMIT]))
total_weight = sum(char_weights.values())

print(f"tallied character weights; total weight: {total_weight} across {len(char_weights)} unique characters")

runs = dict()
wruns = dict()
top = list(top_weights)
total_runs = 2 ** (min(TOP_LIMIT, len(top)))
print(f"number of optimization iterations: {total_runs}")
percentages = dict()

for i in range(10):
    import math
    norm = (i + 1) / 10
    percentages[math.ceil(total_runs * norm)] = (i + 1) * 10

zeros = '0' * TOP_LIMIT

for i in range(1, total_runs):
    if i in percentages:
        print(f"{percentages[i]}% ...")

    res = set(all_words.keys())
    tweight = total_weight
    binstr = bin(i)[2:]
    binstr = zeros[:TOP_LIMIT - len(binstr)] + binstr

    removed = []
    for idx,b in enumerate(binstr):
        if b == '1':
            removed.append(top[idx])
            res = res - char_words[top[idx]]
            tweight -= char_weights[top[idx]]

    total_words = len(res)

    key = ''.join(removed)
    runs[key] = total_words
    wruns[key] = tweight

print("done, finding bests...")

best_sizes = dict()
for removed, word_count in runs.items():
    bsi = len(removed)
    if bsi not in best_sizes:
        best_sizes[bsi] = (removed, word_count)
    else:
        (br, bwc) = best_sizes[bsi]
        if word_count < bwc:
            best_sizes[bsi] = (removed, word_count)

best_weights = dict()
for removed, remaining_weight in wruns.items():
    bsi = len(removed)
    if bsi not in best_weights:
        best_weights[bsi] = (removed, remaining_weight)
    else:
        (br, bwc) = best_weights[bsi]
        if remaining_weight < bwc:
            best_weights[bsi] = (removed, remaining_weight)

print("DONE!")
print("\nBest by remaining word count:")
for letters, details in sorted(best_sizes.items(), key=lambda i: list(i)[0]):
    (removed_letters, word_count) = details
    print(f"  - {letters} letters: {removed_letters} ({word_count} words remaining)")
print("\nBest by remaining weight count (lower is better):")
for letters, details in sorted(best_weights.items(), key=lambda i: list(i)[0]):
    (removed_letters, remaining_weight) = details
    percentage = (remaining_weight / total_weight) * 100.0
    print(f"  - {letters} letters: {removed_letters} ({remaining_weight} remaining - {percentage}% of total)")
