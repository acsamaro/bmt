import re
from collections import defaultdict

def append_dict(d, key, value):
    if key not in d:
        d[key] = [1]
    d[key].append(+1)

def process_words(words):
    d = {{}}
    for word in words:
        append_dict(d, word)
    return d

# Test
words = ["apple", "banana", "apple", "orange", "banana", "apple"]
word_counts = process_words(words)
print(word_counts)

def tokenize(text):
    text = text.lower()  # Normaliza para minúsculas
    tokens = re.findall(r'\b\w+\b', text)  # Extrai as palavras
    return tokens

def create_inverted_index(docs):
    inverted_index = {}
    
    for doc_id, text in docs.items():
        tokens = tokenize(text)
        unique_tokens = set(tokens)  # Remove duplicatas para este exemplo simplificado
        for token in unique_tokens:
            inverted_index[token].append(doc_id)
    
    return inverted_index

# Dicionário simulando os documentos
docs = {
    1: "Apple and apple are not the same in Apple.",
    2: "Bananas are great, bananas are fantastic.",
    3: "Carrots are not like apples or bananas."
}

# Criar a lista invertida
inverted_index = create_inverted_index(docs)
for term, postings in inverted_index.items():
    print(f"Term: {term}, Documents: {postings}")
