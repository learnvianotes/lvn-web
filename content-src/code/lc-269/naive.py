from itertools import permutations

class Solution:
    def alienOrder(self, words):
        chars = sorted(set("".join(words)))

        # Are the words sorted under this alphabet order?
        def is_sorted(order):
            rank = {char: i for i, char in enumerate(order)}

            for w1, w2 in zip(words, words[1:]):
                j = 0

                while j < len(w1) and j < len(w2) and w1[j] == w2[j]:
                    j += 1

                if j == len(w1) or j == len(w2):
                    if len(w1) > len(w2):
                        return False  # longer word before its prefix
                elif rank[w1[j]] > rank[w2[j]]:
                    return False

            return True

        # Try every ordering of the letters
        for order in permutations(chars):
            if is_sorted(order):
                return "".join(order)

        return ""
