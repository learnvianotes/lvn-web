var partition = function(s) {
    const result = [];

    const isPalindrome = (str) => str === [...str].reverse().join('');

    const backtrack = (start, current) => {
        if (start === s.length) {
            result.push([...current]);
            return;
        }

        for (let end = start + 1; end <= s.length; end++) {
            const substring = s.slice(start, end);

            if (isPalindrome(substring)) {
                current.push(substring);
                backtrack(end, current);
                current.pop();
            }
        }
    };

    backtrack(0, []);
    return result;
};
