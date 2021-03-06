import nltk
import sys
import os
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {filename: tokenize(files[filename]) for filename in files}
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory: str) -> dict[str, str]:
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    data = {}
    for file in filter(lambda x: x.endswith(".txt"), os.listdir(directory)):
        with open(os.path.join(directory, file), encoding="utf8") as f:
            data[file] = f.read()
    return data


def tokenize(document: str) -> list[str]:
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    stopwords = set(nltk.corpus.stopwords.words("english"))
    return [
        word.lower()
        for word in nltk.word_tokenize(document)
        if word.isalpha() and word not in stopwords
    ]


def compute_idfs(documents: dict) -> dict[str, float]:
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = set()
    for word_list in documents.values():
        words.update(word_list)
    corpus_length = len(documents)
    idfs = {}
    for word in words:
        f: int = sum(word in documents[file] for file in documents)
        idfs[word] = math.log(corpus_length / f)
    return idfs


def top_files(query, files, idfs, n) -> list[str]:
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = {}
    for file in files:
        sum = 0
        for word in query:
            # Making an exception if word isn't found in corpus and add nothing.
            try:
                sum += files[file].count(word) * idfs[word]
            except KeyError:
                pass
        tfidfs[file] = sum
    return sorted(tfidfs, key=lambda file: tfidfs[file], reverse=True)[:n]


def top_sentences(query: set[str], sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    tfidfs = {}
    for sentence in sentences:
        sum = 0
        for word in query:
            try:
                sum += idfs[word] if word in sentences[sentence] else 0
            except KeyError:
                pass
        tfidfs[sentence] = sum
    return sorted(
        tfidfs,
        key=lambda s: (
            tfidfs[s],
            len(query.intersection(set(sentences[s]))) / len(sentences[s]),
        ),
        reverse=True,
    )[:n]


if __name__ == "__main__":
    main()
