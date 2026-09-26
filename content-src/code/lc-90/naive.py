class Solution:
    def subsetsWithDup(self, nums):
        nums.sort()
        result = set()

        def backtrack(index, current):
            if index == len(nums):
                result.add(tuple(current))
                return

            # Don't take
            backtrack(index + 1, current)

            # Take
            current.append(nums[index])
            backtrack(index + 1, current)
            current.pop()

        backtrack(0, [])
        return [list(x) for x in result]