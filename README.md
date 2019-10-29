# Decuss

> **WARNING:** This document might contain potentially offensive language - purely for academic or educational purposes.

This is a small experiment to empirically decide which letters are the "most profane".

Read the background for more information, or jump to [Results](#Results) if you're
only interested in the findings.

## Background and Details

> **NOTE:** "weight", "severity" and "threat" may all appear throughout this repository. They are used interchangeably.

I needed a quick and dirty encoding for IDs that used a very specific set of characters.

I quickly wrote one up and realized that, since it used the full alpha-numeric character range,
certain unlucky inputs could result in profane output. Knowing that I can't _completely_ prevent this
(and it was outside the scope of the encoding algorithm to do so), I decided to see what I could do to minimize
the chance.

My approach was to remove certain letters from the set that could be emitted by the encoding. However,
which letters to remove was not an obvious choice, so I decided to figure it out somewhat more empirically.

I found a neat list of cuss words that included a "severity" score (a quick glance revealed they were,
to me, pretty sane - though I'm not sure how arbitrary) as well as several locales (languages), so
I decided to use that as my source data.

The scoring algorithm is as follows:

1. Prepare the data (read in the files, merge/de-dupe the words taking the highest severity if collision)
2. Inject possible alternative spellings with letters (e.g. `sh1t`/`5hit` from `shit`, etc.), deducting a severity point from the injected alternatives
3. Normalize all weights (in order to keep weights positive)
4. For each word, and for each unique character in that word, I add the word's weight to a dictionary(char=&gt;total weight) and increment a total word count in another dictionary(char=&gt;word count)
5. Now that each character has tallied weights and word counts, I find the top N weights (where N is specified as the maximum number characters I'd ever want to remove - it doesn't affect results but instead runs more combinations at the cost of time) and iterate `2^N-2` times (`-2` in order to skip `0` as well as not overflow the integer to `N+1` bits) starting at `1` instead of `0`.
6. For each `i` in the iteration, I convert `i` to a bit string and iterate the bits with respect to their offset in `i` (there's probably a much more optimal way to do what I did, but the algorithm completed in a short amount of time so there wasn't a point in optimizing). If the bit is `1`, then I use the bit's offset as a list offset for the list of top N weighted characters, and then removed the words with that character from the list of all words. Rinse and repeat for each bit/character/set of words.
7. After the traversal of the bits, the iteration is left with a list of words _without_ any of the 'enabled' bit characters. The iteration is recorded, storing the removed letters and the count of the remaining words.
8. After all iterations, the best (lowest) word counts are chosen among all runs with equivalent amounts of removed letters (e.g. the best among all runs with 1 letter, 2 letters, 3 letters, etc). The results are displayed and the experiment concludes.

The above algorithm performs a search for the best among **remaining word counts** and **remaining word weight (overall)**.

Further, I applied a weight handicap to "source words" (non-alternatives) of **a factor of 10 times**. As mentioned above, alternatives received a penality of **-1**.

## Results

> **DISCLAIMER:** I am not a data scientist by trade, so take these results with a grain of salt. My goal was to be data-guided, not perfectly exact.

Here are the results when **N=13** (meaning we find the best for 1 letter removed, 2 letters, ... up to **N** letters removed). The value of N does not affect per-group results, just how many results we care about (and how long I want to sit and wait for).

Total run time on my MacBook Pro (15-inch, 2017) (3,1 GHz Intel Core i7, 16 GB 2133 MHz LPDDR3) was **3m42s** according to `fish`.

```
loaded 4749 words across 6 locales (receiving a weight handicap of 10x)
generated a total of 103839 alternative spellings (receiving a weight penality of -1)
107939 total words being considered
min threat: 0
max threat: 20
weighted all words
tallied character weights; total weight: 1757527.0 across 60 unique characters
number of optimization iterations: 8192
10% ...
20% ...
30% ...
40% ...
50% ...
60% ...
70% ...
80% ...
90% ...
done, finding bests...
DONE!

Best by remaining word count:
  - 1 letters: r (50968 words remaining)
  - 2 letters: 3e (25263 words remaining)
  - 3 letters: a14 (12929 words remaining)
  - 4 letters: 3ea4 (5455 words remaining)
  - 5 letters: 3ea14 (2843 words remaining)
  - 6 letters: 3iea14 (1199 words remaining)
  - 7 letters: oiua140 (532 words remaining)
  - 8 letters: 3oiea140 (243 words remaining)
  - 9 letters: 3oiuea140 (50 words remaining)
  - 10 letters: 3oisuea140 (43 words remaining)
  - 11 letters: 3oisuea14c0 (37 words remaining)
  - 12 letters: 3oisuea14nc0 (32 words remaining)
  - 13 letters: 3oirsuea14nc0 (31 words remaining)

Best by remaining weight count (lower is better):
  - 1 letters: r (1648425.0 remaining - 93.79230020363842% of total)
  - 2 letters: r1 (1546675.5 remaining - 88.0029439092543% of total)
  - 3 letters: 3r1 (1455223.0 remaining - 82.79946766109425% of total)
  - 4 letters: 3r1n (1364090.0 remaining - 77.61417036551927% of total)
  - 5 letters: 3ir1n (1280806.5 remaining - 72.87549494260969% of total)
  - 6 letters: 3ir14n (1202607.0 remaining - 68.42608961341703% of total)
  - 7 letters: 3ira14n (1124519.0 remaining - 63.98302842573684% of total)
  - 8 letters: 3ira14nc (1047760.0 remaining - 59.615584853034974% of total)
  - 9 letters: 3irea14nc (972798.0 remaining - 55.35038722022478% of total)
  - 10 letters: 3iruea14nc (899250.5 remaining - 51.16567199252131% of total)
  - 11 letters: 3oiruea14nc (833510.0 remaining - 47.425160466951574% of total)
  - 12 letters: 3oiruea14nc0 (767835.0 remaining - 43.68837576890711% of total)
  - 13 letters: 3oirsuea14nc0 (706015.5 remaining - 40.170961811681984% of total)
```

For ViM users, you can get the raw numbers with this subsitition:

```
%s/\v^(\d+) letters\: [^ ]+ \(([0-9.]+).+$/\1\t\2/g
```

Graph of the falloff:

![Graph showing an exponential decline of remaining words, with only 25% remaining at 3 removed letters, 10% at 4, 5% at 5, roughly 1% at 7 and nearly 0 at 9, whereas there is a slight, linear decline for remaining weight, only hitting 50% remaining weight at 11 removed letters](chart.png).

The remaining weight measurements yielded a linear decline result; however, the remaining words count was far more interesting.

The goal of finding the remaining weight was to, at least to _some_ degree, figure out if there were cases where removing a different letter removed more heinous words rather than a larger quantity of words.

However, the findings of the remaining _word_ metrics proved to be good enough, as we can get down to **~25% of the original word list** by just eliminating **three** (3) characters total, dropping down to **just 5%** by removing **five** letters.

By removing **seven** of the letters, you're left with just around **1%** of the total list of words.

## Final Thoughts

I know this seems a bit... well, silly. And it kind of is. I wish we lived in a world where everyone could ignore such things and move on with their respective lives, but unfortunately, it seems like small things like this can result in some backlash - we ran across this at ZEIT with the 2FA email checks, which contained `<adjective> <animal>` pairs - some combinations forming potentially offensive phrases ("Black Monkey" was one that stood out).

The curve doesn't surprise me, though the steepness of it does. I didn't expect to be at the 25% mark at just 3 letters. I'm happy to see the grand majority being wiped out by about 5 letters, which in my case means removing 7 from my encoding algorithm (since letters have an upper and lower case, thus attributing 2).

Further, it's interesting to see when some letters jitter - for example, going from 6 remaining words to 7 removed `3` from the results when `0` began to appear, which indicates that `0` is _more profane_ than `3` given the right circumstances.

# License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Dataset" property="dct:title" rel="dct:type">Decuss</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/qix-/decuss" property="cc:attributionName" rel="cc:attributionURL">Joshua Junon</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
