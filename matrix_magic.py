
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np
from utils import load_csv_files_from_folder



def pairwise_sparse_jaccard_distance(X, Y=None):
    """
    Computes the Jaccard distance between two sparse matrices or between all pairs in
    one sparse matrix.

    Args:
        X (scipy.sparse.csr_matrix): A sparse matrix.
        Y (scipy.sparse.csr_matrix, optional): A sparse matrix.

    Returns:
        numpy.ndarray: A similarity matrix.
    """

    if Y is None:
        Y = X

    assert X.shape[1] == Y.shape[1]

    X = X.astype(bool).astype(int)
    Y = Y.astype(bool).astype(int)

    intersect = X.dot(Y.T)

    x_sum = X.sum(axis=1).A1
    y_sum = Y.sum(axis=1).A1
    xx, yy = np.meshgrid(x_sum, y_sum)
    union = ((xx + yy).T - intersect)

    return (intersect / union).A


def pairwise_sparse_jaccard_distance_modified(X, Y=None):
    """
    Based on Jaccard distance, dividing by first group magnitude 

    Not conmutative
    
    sim(your commander, sol ring) =sim(sol ring, your commander):
    using jaccard:
    100/(100000)
    100 commander decks using your commander include the sol ring
    100000 decks include the sol ring (the union)

    Using this version:

    sim(your commander, sol ring) = 100/100 = 100%
    sim(sol ring, your commander) = 100/100000 =1%



    Args:
        X (scipy.sparse.csr_matrix): A sparse matrix.
        Y (scipy.sparse.csr_matrix, optional): A sparse matrix.

    Returns:
        numpy.ndarray: A similarity matrix.
    """

    if Y is None:
        Y = X

    assert X.shape[1] == Y.shape[1]

    X = X.astype(bool).astype(int)
    Y = Y.astype(bool).astype(int)

    intersect = X.dot(Y.T)

    x_sum = X.sum(axis=1).A1
    y_sum = Y.sum(axis=1).A1
    xx, yy = np.meshgrid(x_sum, y_sum)
    union = ((xx).T)

    return (intersect / union).A


def get_similarity_matrix(data, use_idf = True):

    # Step 1: Create a document-term matrix

    doc_token_map = data.groupby(['doc_id', 'token']).size().unstack(fill_value=0)



    # Step 2: Use TfidfTransformer on the document-term matrix

    transformer = TfidfTransformer(use_idf=use_idf)

    tfidf_matrix = transformer.fit_transform(doc_token_map)



    # Step 3: Convert the TF-IDF matrix to CSR format (optional as it's already sparse)

    csr_tfidf_matrix = csr_matrix(tfidf_matrix)



    # Step 4: Get the tokens (features)

    tokens = doc_token_map.columns



    # Step 5: Calculate cosine similarity between columns (tokens) in the sparse matrix
    
    if use_idf:
        token_similarity_matrix = cosine_similarity(csr_tfidf_matrix.T, dense_output=False)
    else:
        token_similarity_matrix = csr_matrix(pairwise_sparse_jaccard_distance_modified(csr_tfidf_matrix.T) )
    



    # Step 6: Create a DataFrame from the sparse similarity matrix

    token_similarity_df = pd.DataFrame.sparse.from_spmatrix(

        token_similarity_matrix, index=tokens, columns=tokens)



    # Step 7: Melt the DataFrame to long format

    #similarity_melt = token_similarity_df.reset_index().melt(id_vars='index', var_name='token_2', value_name='similarity')

    #similarity_melt.rename(columns={'index': 'token_1'}, inplace=True)


    similarity_melt = token_similarity_df.reset_index().melt(id_vars='token', var_name='token_2', value_name='similarity')

    similarity_melt.rename(columns={'index': 'token_1'}, inplace=True)



    # Step 8: Filter out rows where similarity is zero

    filtered_similarity_melt = similarity_melt[similarity_melt['similarity'] != 0]
    
    return filtered_similarity_melt



def get_double_matrix(cards):

    dfs = load_csv_files_from_folder('decks/')
    df = pd.concat(dfs)
    data = df[['card','deck_id']]
    data.columns = ['token','doc_id']


    decks = data[data.token.isin(cards)].doc_id.unique()

    data = data[data.doc_id.isin(decks)]

    print('loaded data')
    filtered_similarity_melt = get_similarity_matrix(data, use_idf = True)
    print('IDF OK')
    prob_card_A_given_card_B = get_similarity_matrix(data, use_idf = False)
    print('join prob OK')


    #filtered_similarity_melt.to_csv('tdidf.csv')
    #prob_card_A_given_card_B.to_csv('cond_prob.csv')

    return filtered_similarity_melt,prob_card_A_given_card_B


