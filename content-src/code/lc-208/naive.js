class Trie {
    constructor() {
        this.words = [];
    }

    insert(word) {
        if (!this.words.includes(word)) {
            this.words.push(word);
        }
    }

    search(word) {
        return this.words.includes(word);
    }

    startsWith(prefix) {
        for (const word of this.words) {
            if (word.startsWith(prefix)) return true;
        }

        return false;
    }
}
