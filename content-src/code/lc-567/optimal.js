var checkInclusion = function(s1, s2) {
    if (s1.length > s2.length) return false;
    const target = new Array(26).fill(0), window = new Array(26).fill(0);
    const idx = c => c.charCodeAt(0) - 97;
    for (const c of s1) target[idx(c)]++;
    for (let i = 0; i < s2.length; i++) {
        window[idx(s2[i])]++;
        if (i >= s1.length) window[idx(s2[i - s1.length])]--;
        if (window.every((v, j) => v === target[j])) return true;
    }
    return false;
};
