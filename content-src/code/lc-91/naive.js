var numDecodings = function(s) {
    const dfs = (i) => {
        if (i === s.length) return 1;
        if (s[i] === "0") return 0;

        let result = dfs(i + 1);

        if (i + 1 < s.length) {
            const twoDigit = Number(s.slice(i, i + 2));
            if (twoDigit >= 10 && twoDigit <= 26) {
                result += dfs(i + 2);
            }
        }

        return result;
    };

    return dfs(0);
};
