var isValid = function(s) {
    let changed = true;
    while (changed) {
        changed = false;
        for (const pair of ["()", "[]", "{}"]) {
            if (s.includes(pair)) {
                s = s.split(pair).join("");
                changed = true;
            }
        }
    }
    return s.length === 0;
};
