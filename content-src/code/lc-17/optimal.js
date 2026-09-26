var letterCombinations = function(digits) {
    if (!digits) return [];

    const phone = [
        "",
        "",
        "abc",
        "def",
        "ghi",
        "jkl",
        "mno",
        "pqrs",
        "tuv",
        "wxyz"
    ];

    const result = [];

    const backtrack = (index, current) => {
        if (index === digits.length) {
            result.push(current.join(''));
            return;
        }

        const letters = phone[digits.charCodeAt(index) - 48];  // '0' is char code 48

        for (const ch of letters) {
            current.push(ch);
            backtrack(index + 1, current);
            current.pop();
        }
    };

    backtrack(0, []);
    return result;
};
