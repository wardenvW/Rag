from rag_wv import Embedder

a = Embedder()
text = ["text txt tmp"]
res = a.embed(text)

#print(res['dense_vecs'])
print(res['lexical_weights'][0])

data = res['lexical_weights'][0]

print(data.keys())
for k, v in data.values():
    print(k, float(v))