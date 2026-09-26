var isMatch = function(s, p) {
    const memo = new Map();

    const dfs = (i, j) => {
        const key = `${i},${j}`;
        if (memo.has(key)) return memo.get(key);

        if (j === p.length) return i === s.length;

        const firstMatch = i < s.length && (p[j] === s[i] || p[j] === ".");
        let answer;

        if (j + 1 < p.length && p[j + 1] === "*") {
            answer = dfs(i, j + 2) || (firstMatch && dfs(i + 1, j));
        } else {
            answer = firstMatch && dfs(i + 1, j + 1);
        }

        memo.set(key, answer);
        return answer;
    };

    return dfs(0, 0);
};
