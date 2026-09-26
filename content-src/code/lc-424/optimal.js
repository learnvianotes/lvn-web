var characterReplacement = function(s, k) {
    const count = new Map();
    let left = 0, maxFrequency = 0, answer = 0;
    for (let right = 0; right < s.length; right++) {
        count.set(s[right], (count.get(s[right]) || 0) + 1);
        maxFrequency = Math.max(maxFrequency, count.get(s[right]));
        while (right - left + 1 - maxFrequency > k) {
            count.set(s[left], count.get(s[left]) - 1);
            left++;
        }
        answer = Math.max(answer, right - left + 1);
    }
    return answer;
};
