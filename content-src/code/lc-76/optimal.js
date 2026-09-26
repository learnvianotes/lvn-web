var minWindow = function(s, t) {
    if (!t) return "";
    const need = new Map(), have = new Map();
    for (const c of t) need.set(c, (need.get(c) || 0) + 1);
    const required = need.size;
    let formed = 0, left = 0, bestLength = Infinity, bestStart = 0;
    for (let right = 0; right < s.length; right++) {
        const c = s[right];
        have.set(c, (have.get(c) || 0) + 1);
        if (need.has(c) && have.get(c) === need.get(c)) formed++;
        while (formed === required) {
            if (right - left + 1 < bestLength) {
                bestLength = right - left + 1;
                bestStart = left;
            }
            const leftChar = s[left];
            have.set(leftChar, have.get(leftChar) - 1);
            if (need.has(leftChar) && have.get(leftChar) < need.get(leftChar)) formed--;
            left++;
        }
    }
    if (bestLength === Infinity) return "";
    return s.slice(bestStart, bestStart + bestLength);
};
