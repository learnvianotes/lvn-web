var ladderLength = function(beginWord, endWord, wordList) {
    if (!wordList.includes(endWord)) return 0;

    const words = [...wordList, beginWord];
    const n = words.length;

    const oneApart = (a, b) => {
        let diff = 0;
        for (let i = 0; i < a.length && diff <= 1; i++)
            if (a[i] !== b[i]) diff++;
        return diff === 1;
    };

    // Compare every pair of words to build the graph
    const graph = Array.from({ length: n }, () => []);
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            if (oneApart(words[i], words[j])) {
                graph[i].push(j);
                graph[j].push(i);
            }
        }
    }

    const visited = new Array(n).fill(false);
    const queue = [[n - 1, 1]];
    visited[n - 1] = true;

    for (let head = 0; head < queue.length; head++) {
        const [i, distance] = queue[head];

        if (words[i] === endWord) return distance;

        for (const j of graph[i]) {
            if (!visited[j]) {
                visited[j] = true;
                queue.push([j, distance + 1]);
            }
        }
    }

    return 0;
};
