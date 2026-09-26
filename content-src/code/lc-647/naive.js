var countSubstrings = function(s) {
    const isPalindrome = (left, right) => {
        while (left < right) {
            if (s[left] !== s[right]) return false;
            left++;
            right--;
        }
        return true;
    };

    let count = 0;

    for (let i = 0; i < s.length; i++) {
        for (let j = i; j < s.length; j++) {
            if (isPalindrome(i, j)) count++;
        }
    }

    return count;
};
