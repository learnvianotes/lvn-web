var lengthOfLongestSubstring = function(s) {
    let answer = 0;
    for (let i = 0; i < s.length; i++) {
        const seen = new Set();
        for (let j = i; j < s.length; j++) {
            if (seen.has(s[j])) break;
            seen.add(s[j]);
            answer = Math.max(answer, j - i + 1);
        }
    }
    return answer;
};
