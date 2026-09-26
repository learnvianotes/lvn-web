var characterReplacement = function(s, k) {
    let answer = 0;
    for (let left = 0; left < s.length; left++) {
        const count = new Map();
        for (let right = left; right < s.length; right++) {
            count.set(s[right], (count.get(s[right]) || 0) + 1);
            const length = right - left + 1;
            const mostFrequent = Math.max(...count.values());
            if (length - mostFrequent <= k) answer = Math.max(answer, length);
        }
    }
    return answer;
};
