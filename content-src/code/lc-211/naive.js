class WordDictionary {
    constructor() {
        this.words = [];
    }

    addWord(word) {
        this.words.push(word);
    }

    search(word) {
        for (const candidate of this.words) {
            if (candidate.length !== word.length) continue;

            let match = true;

            for (let i = 0; i < word.length; i++) {
                if (word[i] !== "." && word[i] !== candidate[i]) {
                    match = false;
                    break;
                }
            }

            if (match) return true;
        }

        return false;
    }
}
