var partition = function(s) {
    const n = s.length;

    const palindrome = Array.from({ length: n }, () => new Array(n).fill(false));

    for (let i = 0; i < n; i++) palindrome[i][i] = true;

    for (let length = 2; length <= n; length++) {
        for (let left = 0; left <= n - length; left++) {
            const right = left + length - 1;

            if (s[left] === s[right]) {
                if (length === 2 || palindrome[left + 1][right - 1]) {
                    palindrome[left][right] = true;
                }
            }
        }
    }

    const result = [];

    const backtrack = (start, current) => {
        if (start === n) {
            result.push([...current]);
            return;
        }

        for (let end = start; end < n; end++) {
            if (palindrome[start][end]) {
                current.push(s.slice(start, end + 1));
                backtrack(end + 1, current);
                current.pop();
            }
        }
    };

    backtrack(0, []);
    return result;
};
