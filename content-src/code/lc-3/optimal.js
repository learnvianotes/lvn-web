var lengthOfLongestSubstring = function(s) {
    const seen = new Set();
    let left = 0, answer = 0;
    for (let right = 0; right < s.length; right++) {
        while (seen.has(s[right])) {
            seen.delete(s[left]);
            left++;
        }
        seen.add(s[right]);
        answer = Math.max(answer, right - left + 1);
    }
    return answer;
};
