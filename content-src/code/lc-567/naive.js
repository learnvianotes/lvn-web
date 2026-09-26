var checkInclusion = function(s1, s2) {
    const target = new Set();
    const permute = (prefix, rest) => {
        if (!rest) { target.add(prefix); return; }
        for (let i = 0; i < rest.length; i++)
            permute(prefix + rest[i], rest.slice(0, i) + rest.slice(i + 1));
    };
    permute("", s1);
    const length = s1.length;
    for (let i = 0; i + length <= s2.length; i++)
        if (target.has(s2.slice(i, i + length))) return true;
    return false;
};
