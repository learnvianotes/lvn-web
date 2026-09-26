var minWindow = function(s, t) {
    if (!t) return "";
    const countOf = c => t.split(c).length - 1;
    let answer = "";
    for (let left = 0; left < s.length; left++) {
        const count = new Map();
        for (let right = left; right < s.length; right++) {
            count.set(s[right], (count.get(s[right]) || 0) + 1);
            let valid = true;
            for (const c of t)
                if ((count.get(c) || 0) < countOf(c)) {
                    valid = false;
                    break;
                }
            if (valid) {
                const current = s.slice(left, right + 1);
                if (!answer || current.length < answer.length) answer = current;
                break;
            }
        }
    }
    return answer;
};
