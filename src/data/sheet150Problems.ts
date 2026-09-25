import type { Sheet150QuestionDoc } from '@/lib/firestoreService'

export const SHEET_150_CORE_PROBLEMS: Sheet150QuestionDoc[] = [
  {
    id: 'lc-217',
    slug: 'contains-duplicate',
    lcNumber: 217,
    title: 'Contains Duplicate',
    difficulty: 'Easy',
    topic: 'Arrays & Hashing',
    category: 'arrays-hashing',
    order: 1,
    tags: ['Array', 'Hash Table'],
    moduleNumber: 1,
    leetcodeUrl: 'https://leetcode.com/problems/contains-duplicate/',
    problemStatement: 'Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.',
    inputOutput: {
      input: 'nums: int[]',
      output: 'boolean — true if duplicate exists, false otherwise',
      examples: [
        { in: 'nums = [1,2,3,1]', out: 'true', comment: '1 appears at index 0 and 3' },
        { in: 'nums = [1,2,3,4]', out: 'false' },
        { in: 'nums = [1,1,1,3,3,4,3,2,4,2]', out: 'true' }
      ]
    },
    constraints: [
      '1 <= nums.length <= 10^5',
      '-10^9 <= nums[i] <= 10^9'
    ],
    keyInsight: 'Brute force compares every pair — O(n²). Key insight: we only need to know "have I seen this before?" → Hash Set gives O(1) lookup, making one linear pass sufficient.',
    naiveSolution: {
      title: 'Naive Solution — O(n²) Brute Force',
      complexityTime: 'O(n²)',
      complexitySpace: 'O(1)',
      code: {
        py: `class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] == nums[j]:
                    return True
        return False`,
        cpp: `class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {
        for (int i = 0; i < nums.size(); ++i)
            for (int j = i+1; j < nums.size(); ++j)
                if (nums[i] == nums[j]) return true;
        return false;
    }
};`,
        java: `class Solution {
    public boolean containsDuplicate(int[] nums) {
        for (int i = 0; i < nums.length; ++i)
            for (int j = i+1; j < nums.length; ++j)
                if (nums[i] == nums[j]) return true;
        return false;
    }
}`,
        js: `var containsDuplicate = function(nums) {
    for (let i = 0; i < nums.length; i++)
        for (let j = i+1; j < nums.length; j++)
            if (nums[i] === nums[j]) return true;
    return false;
};`
      }
    },
    optimalSolution: {
      title: 'Optimized Code — Hash Set O(n)',
      complexityTime: 'O(n)',
      complexitySpace: 'O(n)',
      approach: [
        'Initialize empty set seen.',
        'For each num: if num in seen -> return True.',
        'Else add num to seen.',
        'End of loop -> return False.'
      ],
      code: {
        py: `class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        seen = set()
        for num in nums:
            if num in seen:
                return True
            seen.add(num)
        return False`,
        cpp: `class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {
        unordered_set<int> seen;
        for (int n : nums) {
            if (seen.count(n)) return true;
            seen.insert(n);
        }
        return false;
    }
};`,
        java: `class Solution {
    public boolean containsDuplicate(int[] nums) {
        HashSet<Integer> seen = new HashSet<>();
        for (int n : nums) {
            if (seen.contains(n)) return true;
            seen.add(n);
        }
        return false;
    }
}`,
        js: `var containsDuplicate = function(nums) {
    const seen = new Set();
    for (const num of nums) {
        if (seen.has(num)) return true;
        seen.add(num);
    }
    return false;
};`
      }
    },
    similarQuestions: [
      { slug: 'valid-anagram', title: 'Valid Anagram', lc: 242, difficulty: 'Easy' },
      { slug: 'two-sum', title: 'Two Sum', lc: 1, difficulty: 'Easy' },
      { title: 'Find All Duplicates in an Array', lc: 442, difficulty: 'Medium' }
    ]
  },
  {
    id: 'lc-242',
    slug: 'valid-anagram',
    lcNumber: 242,
    title: 'Valid Anagram',
    difficulty: 'Easy',
    topic: 'Arrays & Hashing',
    category: 'arrays-hashing',
    order: 2,
    tags: ['String', 'Hash Table', 'Sorting'],
    moduleNumber: 1,
    leetcodeUrl: 'https://leetcode.com/problems/valid-anagram/',
    problemStatement: 'Given two strings s and t, return true if t is an anagram of s, and false otherwise.',
    inputOutput: {
      input: 's: string, t: string',
      output: 'boolean — true if anagram, false otherwise',
      examples: [
        { in: 's = "anagram", t = "nagaram"', out: 'true' },
        { in: 's = "rat", t = "car"', out: 'false' }
      ]
    },
    constraints: ['1 <= s.length, t.length <= 5 * 10^4', 's and t consist of lowercase English letters.'],
    keyInsight: 'Anagrams contain identical character frequencies. Instead of sorting (O(n log n)), count characters in an array of size 26 in O(n) time and O(1) extra space.',
    naiveSolution: {
      title: 'Naive Solution — Sorting O(n log n)',
      complexityTime: 'O(n log n)',
      complexitySpace: 'O(1)',
      code: {
        py: `class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        return sorted(s) == sorted(t)`,
        cpp: `class Solution {
public:
    bool isAnagram(string s, string t) {
        if (s.length() != t.length()) return false;
        sort(s.begin(), s.end());
        sort(t.begin(), t.end());
        return s == t;
    }
};`,
        java: `class Solution {
    public boolean isAnagram(String s, String t) {
        char[] sArr = s.toCharArray();
        char[] tArr = t.toCharArray();
        Arrays.sort(sArr);
        Arrays.sort(tArr);
        return Arrays.equals(sArr, tArr);
    }
}`,
        js: `var isAnagram = function(s, t) {
    if (s.length !== t.length) return false;
    return s.split('').sort().join('') === t.split('').sort().join('');
};`
      }
    },
    optimalSolution: {
      title: 'Optimized Code — Fixed 26-Array Frequency Counter O(n)',
      complexityTime: 'O(n)',
      complexitySpace: 'O(1)',
      approach: [
        'If len(s) != len(t), return False immediately.',
        'Initialize count array of length 26 to 0.',
        'Increment count for each char in s, decrement for each char in t.',
        'If any count is non-zero, return False. Otherwise True.'
      ],
      code: {
        py: `class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        count = [0] * 26
        for c1, c2 in zip(s, t):
            count[ord(c1) - ord('a')] += 1
            count[ord(c2) - ord('a')] -= 1
        return all(x == 0 for x in count)`,
        cpp: `class Solution {
public:
    bool isAnagram(string s, string t) {
        if (s.length() != t.length()) return false;
        int count[26] = {0};
        for (int i = 0; i < s.length(); ++i) {
            count[s[i] - 'a']++;
            count[t[i] - 'a']--;
        }
        for (int i = 0; i < 26; ++i) {
            if (count[i] != 0) return false;
        }
        return true;
    }
};`,
        java: `class Solution {
    public boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) return false;
        int[] count = new int[26];
        for (int i = 0; i < s.length(); i++) {
            count[s.charAt(i) - 'a']++;
            count[t.charAt(i) - 'a']--;
        }
        for (int c : count) if (c != 0) return false;
        return true;
    }
}`,
        js: `var isAnagram = function(s, t) {
    if (s.length !== t.length) return false;
    const count = new Array(26).fill(0);
    const codeA = 'a'.charCodeAt(0);
    for (let i = 0; i < s.length; i++) {
        count[s.charCodeAt(i) - codeA]++;
        count[t.charCodeAt(i) - codeA]--;
    }
    return count.every(x => x === 0);
};`
      }
    },
    similarQuestions: [
      { slug: 'group-anagrams', title: 'Group Anagrams', lc: 49, difficulty: 'Medium' },
      { slug: 'contains-duplicate', title: 'Contains Duplicate', lc: 217, difficulty: 'Easy' },
      { title: 'Find All Anagrams in a String', lc: 438, difficulty: 'Medium' }
    ]
  },
  {
    id: 'lc-1',
    slug: 'two-sum',
    lcNumber: 1,
    title: 'Two Sum',
    difficulty: 'Easy',
    topic: 'Arrays & Hashing',
    category: 'arrays-hashing',
    order: 3,
    tags: ['Array', 'Hash Table'],
    moduleNumber: 1,
    leetcodeUrl: 'https://leetcode.com/problems/two-sum/',
    problemStatement: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. Each input would have exactly one solution, and you may not use the same element twice.',
    inputOutput: {
      input: 'nums: int[], target: int',
      output: 'int[] — indices of the two numbers',
      examples: [
        { in: 'nums = [2,7,11,15], target = 9', out: '[0,1]', comment: 'nums[0] + nums[1] == 9, return [0, 1]' },
        { in: 'nums = [3,2,4], target = 6', out: '[1,2]' },
        { in: 'nums = [3,3], target = 6', out: '[0,1]' }
      ]
    },
    constraints: ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', 'Exactly one valid answer exists.'],
    keyInsight: 'For each number x, the required complement is target - x. A Hash Map allows checking if the complement has been encountered in O(1) time.',
    naiveSolution: {
      title: 'Naive Solution — Nested Loops O(n²)',
      complexityTime: 'O(n²)',
      complexitySpace: 'O(1)',
      code: {
        py: `class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []`,
        cpp: `class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        for (int i = 0; i < nums.size(); ++i)
            for (int j = i+1; j < nums.size(); ++j)
                if (nums[i] + nums[j] == target) return {i, j};
        return {};
    }
};`,
        java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; ++i)
            for (int j = i+1; j < nums.length; ++j)
                if (nums[i] + nums[j] == target) return new int[]{i, j};
        return new int[]{};
    }
}`,
        js: `var twoSum = function(nums, target) {
    for (let i = 0; i < nums.length; i++)
        for (let j = i + 1; j < nums.length; j++)
            if (nums[i] + nums[j] === target) return [i, j];
    return [];
};`
      }
    },
    optimalSolution: {
      title: 'Optimized Code — One-Pass Hash Map O(n)',
      complexityTime: 'O(n)',
      complexitySpace: 'O(n)',
      approach: [
        'Initialize map seen = {} (mapping value -> index).',
        'Iterate through nums with index i and value n.',
        'Calculate complement = target - n.',
        'If complement is in seen, return [seen[complement], i].',
        'Otherwise store seen[n] = i.'
      ],
      code: {
        py: `class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}
        for i, n in enumerate(nums):
            complement = target - n
            if complement in seen:
                return [seen[complement], i]
            seen[n] = i
        return []`,
        cpp: `class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;
        for (int i = 0; i < nums.size(); ++i) {
            int comp = target - nums[i];
            if (seen.count(comp)) return {seen[comp], i};
            seen[nums[i]] = i;
        }
        return {};
    }
};`,
        java: `class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int comp = target - nums[i];
            if (seen.containsKey(comp)) return new int[]{seen.get(comp), i};
            seen.put(nums[i], i);
        }
        return new int[]{};
    }
}`,
        js: `var twoSum = function(nums, target) {
    const seen = new Map();
    for (let i = 0; i < nums.length; i++) {
        const comp = target - nums[i];
        if (seen.has(comp)) return [seen.get(comp), i];
        seen.set(nums[i], i);
    }
    return [];
};`
      }
    },
    similarQuestions: [
      { slug: 'contains-duplicate', title: 'Contains Duplicate', lc: 217, difficulty: 'Easy' },
      { slug: 'group-anagrams', title: 'Group Anagrams', lc: 49, difficulty: 'Medium' },
      { title: '3Sum', lc: 15, difficulty: 'Medium' }
    ]
  },
  {
    id: 'lc-49',
    slug: 'group-anagrams',
    lcNumber: 49,
    title: 'Group Anagrams',
    difficulty: 'Medium',
    topic: 'Arrays & Hashing',
    category: 'arrays-hashing',
    order: 4,
    tags: ['Array', 'Hash Table', 'Sorting'],
    moduleNumber: 1,
    leetcodeUrl: 'https://leetcode.com/problems/group-anagrams/',
    problemStatement: 'Given an array of strings strs, group the anagrams together. You can return the answer in any order.',
    inputOutput: {
      input: 'strs: string[]',
      output: 'string[][] — grouped anagram lists',
      examples: [
        { in: 'strs = ["eat","tea","tan","ate","nat","bat"]', out: '[["bat"],["nat","tan"],["ate","eat","tea"]]' },
        { in: 'strs = [""]', out: '[[""]]' },
        { in: 'strs = ["a"]', out: '[["a"]]' }
      ]
    },
    constraints: ['1 <= strs.length <= 10^4', '0 <= strs[i].length <= 100', 'strs[i] consists of lowercase English letters.'],
    keyInsight: 'All anagrams produce the same canonical key when sorted or character-counted. Using a tuple of 26 character counts as the dictionary key yields O(N * K) time complexity where K is max string length.',
    naiveSolution: {
      title: 'Sort-Based Map — O(N * K log K)',
      complexityTime: 'O(N * K log K)',
      complexitySpace: 'O(N * K)',
      code: {
        py: `class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        ans = collections.defaultdict(list)
        for s in strs:
            ans[tuple(sorted(s))].append(s)
        return list(ans.values())`,
        cpp: `class Solution {
public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {
        unordered_map<string, vector<string>> mp;
        for (string s : strs) {
            string t = s;
            sort(t.begin(), t.end());
            mp[t].push_back(s);
        }
        vector<vector<string>> res;
        for (auto p : mp) res.push_back(p.second);
        return res;
    }
};`,
        java: `class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> map = new HashMap<>();
        for (String s : strs) {
            char[] ca = s.toCharArray();
            Arrays.sort(ca);
            String keyStr = String.valueOf(ca);
            if (!map.containsKey(keyStr)) map.put(keyStr, new ArrayList<>());
            map.get(keyStr).add(s);
        }
        return new ArrayList<>(map.values());
    }
}`,
        js: `var groupAnagrams = function(strs) {
    const map = {};
    for (const s of strs) {
        const key = s.split('').sort().join('');
        if (!map[key]) map[key] = [];
        map[key].push(s);
    }
    return Object.values(map);
};`
      }
    },
    optimalSolution: {
      title: 'Count-Array Hash Key — O(N * K)',
      complexityTime: 'O(N * K)',
      complexitySpace: 'O(N * K)',
      approach: [
        'Create a defaultdict(list) where key is a 26-tuple of character frequencies.',
        'For each string, compute its 26-length frequency tuple.',
        'Append the string to dict[tuple].',
        'Return list(dict.values()).'
      ],
      code: {
        py: `class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        res = collections.defaultdict(list)
        for s in strs:
            count = [0] * 26
            for c in s:
                count[ord(c) - ord('a')] += 1
            res[tuple(count)].append(s)
        return list(res.values())`,
        cpp: `class Solution {
public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {
        map<vector<int>, vector<string>> mp;
        for (string& s : strs) {
            vector<int> count(26, 0);
            for (char c : s) count[c - 'a']++;
            mp[count].push_back(s);
        }
        vector<vector<string>> res;
        for (auto& p : mp) res.push_back(p.second);
        return res;
    }
};`,
        java: `class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> map = new HashMap<>();
        for (String s : strs) {
            int[] count = new int[26];
            for (char c : s.toCharArray()) count[c - 'a']++;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 26; i++) {
                sb.append('#').append(count[i]);
            }
            String key = sb.toString();
            map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }
        return new ArrayList<>(map.values());
    }
}`,
        js: `var groupAnagrams = function(strs) {
    const map = new Map();
    for (const s of strs) {
        const count = new Array(26).fill(0);
        for (let i = 0; i < s.length; i++) {
            count[s.charCodeAt(i) - 97]++;
        }
        const key = count.join('#');
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(s);
    }
    return Array.from(map.values());
};`
      }
    },
    similarQuestions: [
      { slug: 'valid-anagram', title: 'Valid Anagram', lc: 242, difficulty: 'Easy' },
      { slug: 'two-sum', title: 'Two Sum', lc: 1, difficulty: 'Easy' }
    ]
  },
  {
    id: 'lc-704',
    slug: 'binary-search',
    lcNumber: 704,
    title: 'Binary Search',
    difficulty: 'Easy',
    topic: 'Searching & Sorting',
    category: 'binary-search',
    order: 1,
    tags: ['Array', 'Binary Search'],
    moduleNumber: 7,
    leetcodeUrl: 'https://leetcode.com/problems/binary-search/',
    problemStatement: 'Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1. You must write an algorithm with O(log n) runtime complexity.',
    inputOutput: {
      input: 'nums: int[], target: int',
      output: 'int — index of target or -1',
      examples: [
        { in: 'nums = [-1,0,3,5,9,12], target = 9', out: '4', comment: '9 exists in nums and its index is 4' },
        { in: 'nums = [-1,0,3,5,9,12], target = 2', out: '-1', comment: '2 does not exist in nums so return -1' }
      ]
    },
    constraints: ['1 <= nums.length <= 10^4', '-10^4 < nums[i], target < 10^4', 'All integers in nums are unique.', 'nums is sorted in ascending order.'],
    keyInsight: 'Because nums is sorted, each comparison at the midpoint halves the search space. Use mid = left + (right - left) // 2 to prevent integer overflow in C++/Java.',
    naiveSolution: {
      title: 'Linear Scan — O(n)',
      complexityTime: 'O(n)',
      complexitySpace: 'O(1)',
      code: {
        py: `class Solution:
    def search(self, nums: list[int], target: int) -> int:
        for i, val in enumerate(nums):
            if val == target:
                return i
        return -1`,
        cpp: `class Solution {
public:
    int search(vector<int>& nums, int target) {
        for (int i = 0; i < nums.size(); ++i)
            if (nums[i] == target) return i;
        return -1;
    }
};`,
        java: `class Solution {
    public int search(int[] nums, int target) {
        for (int i = 0; i < nums.length; ++i)
            if (nums[i] == target) return i;
        return -1;
    }
}`,
        js: `var search = function(nums, target) {
    for (let i = 0; i < nums.length; i++)
        if (nums[i] === target) return i;
    return -1;
};`
      }
    },
    optimalSolution: {
      title: 'Binary Search — O(log n)',
      complexityTime: 'O(log n)',
      complexitySpace: 'O(1)',
      approach: [
        'Set left = 0, right = len(nums) - 1.',
        'While left <= right:',
        '  mid = left + (right - left) // 2',
        '  if nums[mid] == target: return mid',
        '  if nums[mid] < target: left = mid + 1',
        '  else: right = mid - 1',
        'Return -1 if not found.'
      ],
      code: {
        py: `class Solution:
    def search(self, nums: list[int], target: int) -> int:
        l, r = 0, len(nums) - 1
        while l <= r:
            mid = l + (r - l) // 2
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                l = mid + 1
            else:
                r = mid - 1
        return -1`,
        cpp: `class Solution {
public:
    int search(vector<int>& nums, int target) {
        int l = 0, r = nums.size() - 1;
        while (l <= r) {
            int mid = l + (r - l) / 2;
            if (nums[mid] == target) return mid;
            else if (nums[mid] < target) l = mid + 1;
            else r = mid - 1;
        }
        return -1;
    }
};`,
        java: `class Solution {
    public int search(int[] nums, int target) {
        int l = 0, r = nums.length - 1;
        while (l <= r) {
            int mid = l + (r - l) / 2;
            if (nums[mid] == target) return mid;
            else if (nums[mid] < target) l = mid + 1;
            else r = mid - 1;
        }
        return -1;
    }
}`,
        js: `var search = function(nums, target) {
    let l = 0, r = nums.length - 1;
    while (l <= r) {
        const mid = l + Math.floor((r - l) / 2);
        if (nums[mid] === target) return mid;
        else if (nums[mid] < target) l = mid + 1;
        else r = mid - 1;
    }
    return -1;
};`
      }
    },
    similarQuestions: [
      { title: 'Search in Rotated Sorted Array', lc: 33, difficulty: 'medium' },
      { title: 'Search a 2D Matrix', lc: 74, difficulty: 'medium' }
    ]
  }
]
