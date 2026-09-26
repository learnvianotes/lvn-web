var wordBreak = function(s, wordDict) {
    const words = new Set(wordDict);

    const dfs = (start) => {
        if (start === s.length) return true;

        for (let end = start + 1; end <= s.length; end++) {
            if (words.has(s.slice(start, end))) {
                if (dfs(end)) return true;
            }
        }

        return false;
    };

    return dfs(0);
};
