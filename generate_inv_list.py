import re
import csv

def append_dict_list(d:dict, key:str, value:int):
    if (key not in d):
        d[key] = []
    d[key].append(value)

def process_words(d:dict, words:list[str], doc_id:int):
    for word in words:
        append_dict_list(d, word, doc_id)
    return d

def tokenize(text:str):
    #TODO: Implementar
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def create_inverted_index(docs:list[str]):
    inverted_index = {}
    for doc_id, text in docs.items():
        tokens = tokenize(text)
        inverted_index = process_words(inverted_index, tokens, doc_id)    
    return inverted_index

def save_inv_list_csv(d: dict, path:str):
     with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key, value in d.items():
                writer.writerow([key.upper(), str(value)])

def inv_list(docs, path):
    #TODO: Add Log
    inverted_index = create_inverted_index(docs)
    save_inv_list_csv(inverted_index, path)
    return inverted_index


#TODO: apagar os testes
# Dicionário simulando os documentos
docs = {
    1: "Apple and apple are not the same in Apple.",
    2: "Bananas are great, bananas are fantastic.",
    3: "Carrots are not like apples or bananas."
}
path= './data/inv_list.csv'

# Criar a lista invertida
inverted_index = create_inverted_index(docs)
for term, postings in inverted_index.items():
    print(f"Term: {term}, Documents: {postings}")
save_inv_list_csv(inverted_index, path)