class WordDictionary {
    private List<String> words;

    public WordDictionary() {
        words = new ArrayList<>();
    }

    public void addWord(String word) {
        words.add(word);
    }

    public boolean search(String word) {
        for (String candidate : words) {
            if (candidate.length() != word.length()) continue;

            boolean match = true;

            for (int i = 0; i < word.length(); i++) {
                if (word.charAt(i) != '.' && word.charAt(i) != candidate.charAt(i)) {
                    match = false;
                    break;
                }
            }

            if (match) return true;
        }

        return false;
    }
}
