var isPalindrome = function(s) {
    let cleaned = "";
    for (const c of s)
        if (/[a-z0-9]/i.test(c)) cleaned += c.toLowerCase();
    return cleaned === cleaned.split("").reverse().join("");
};
