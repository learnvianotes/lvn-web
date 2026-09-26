var longestPalindrome = function(s) {
    let start = 0, end = 0;

    const expand = (left, right) => {
        while (left >= 0 && right < s.length && s[left] === s[right]) {
            left--;
            right++;
        }
        return [left + 1, right - 1];
    };

    for (let i = 0; i < s.length; i++) {
        const [left1, right1] = expand(i, i);
        const [left2, right2] = expand(i, i + 1);

        if (right1 - left1 > end - start) {
            [start, end] = [left1, right1];
        }

        if (right2 - left2 > end - start) {
            [start, end] = [left2, right2];
        }
    }

    return s.slice(start, end + 1);
};
