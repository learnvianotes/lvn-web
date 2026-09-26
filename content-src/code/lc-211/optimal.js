class TrieNode {
    constructor() {
        this.children = new Map();
        this.isWord = false;
    }
}

class WordDictionary {
    constructor() {
        this.root = new TrieNode();
    }

    addWord(word) {
        let node = this.root;

        for (const char of word) {
            if (!node.children.has(char)) node.children.set(char, new TrieNode());

            node = node.children.get(char);
        }

        node.isWord = true;
    }

    search(word) {
        const dfs = (index, node) => {
            if (index === word.length) return node.isWord;

            const char = word[index];

            if (char !== ".") {
                if (!node.children.has(char)) return false;

                return dfs(index + 1, node.children.get(char));
            }

            // Wildcard: try all children
            for (const child of node.children.values()) {
                if (dfs(index + 1, child)) return true;
            }

            return false;
        };

        return dfs(0, this.root);
    }
}
