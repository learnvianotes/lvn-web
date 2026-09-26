class TrieNode {
    constructor() {
        this.children = new Map();
        this.isWord = false;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }

    insert(word) {
        let node = this.root;

        for (const char of word) {
            if (!node.children.has(char)) node.children.set(char, new TrieNode());

            node = node.children.get(char);
        }

        node.isWord = true;
    }

    search(word) {
        let node = this.root;

        for (const char of word) {
            if (!node.children.has(char)) return false;

            node = node.children.get(char);
        }

        return node.isWord;
    }

    startsWith(prefix) {
        let node = this.root;

        for (const char of prefix) {
            if (!node.children.has(char)) return false;

            node = node.children.get(char);
        }

        return true;
    }
}
