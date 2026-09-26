var letterCombinations = function(digits) {
    if (!digits) return [];

    const phone = {
        '2': 'abc',
        '3': 'def',
        '4': 'ghi',
        '5': 'jkl',
        '6': 'mno',
        '7': 'pqrs',
        '8': 'tuv',
        '9': 'wxyz'
    };

    const result = [];

    const backtrack = (index, current) => {
        if (index === digits.length) {
            result.push(current.join(''));
            return;
        }

        for (const ch of phone[digits[index]]) {
            current.push(ch);
            backtrack(index + 1, current);
            current.pop();
        }
    };

    backtrack(0, []);
    return result;
};
