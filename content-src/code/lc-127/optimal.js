var ladderLength = function(beginWord, endWord, wordList) {
    if (!wordList.includes(endWord)) return 0;

    const patterns = new Map();

    for (const word of wordList) {
        for (let i = 0; i < word.length; i++) {
            const pattern = word.slice(0, i) + "*" + word.slice(i + 1);
            if (!patterns.has(pattern)) patterns.set(pattern, []);
            patterns.get(pattern).push(word);
        }
    }

    const visited = new Set([beginWord]);
    const queue = [[beginWord, 1]];

    for (let head = 0; head < queue.length; head++) {
        const [word, distance] = queue[head];

        if (word === endWord) return distance;

        for (let i = 0; i < word.length; i++) {
            const pattern = word.slice(0, i) + "*" + word.slice(i + 1);

            for (const neighbor of patterns.get(pattern) || []) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push([neighbor, distance + 1]);
                }
            }

            patterns.delete(pattern);
        }
    }

    return 0;
};
