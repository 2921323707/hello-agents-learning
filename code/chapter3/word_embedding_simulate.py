import numpy as np 

embeddings = {
    'king':np.array([0.9,0.9]),
    'queen':np.array([0.9,0.2]),
    'man':np.array([0.7,0.9]),
    'woman':np.array([0.7,0.3])
}

def cosine_similarity(vec1,vec2):
    dot_product = np.dot(vec1,vec2)
    norm1 = np.linalg.norm(vec1) 
    norm2 = np.linalg.norm(vec2) 
    return dot_product / (norm1 * norm2)

result_vec = embeddings['king'] - embeddings['man'] + embeddings['woman']

sim = cosine_similarity(result_vec,embeddings['queen'])
print(f"sim: {sim:.4f}")