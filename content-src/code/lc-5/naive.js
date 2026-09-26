var longestPalindrome = function(s) {
    const isPalindrome = (left, right) => {
        while (left < right) {
            if (s[left] !== s[right]) return false;
            left++;
            right--;
        }
        return true;
    };

    let longest = "";

    for (let i = 0; i < s.length; i++) {
        for (let j = i; j < s.length; j++) {
            if (isPalindrome(i, j) && j - i + 1 > longest.length) {
                longest = s.slice(i, j + 1);
            }
        }
    }

    return longest;
};
