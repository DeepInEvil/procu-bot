# import numpy as np
import pandas as pd
from rapidfuzz import process, fuzz
import spacy
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
stops = stopwords.words('english')
# nltk.download('punkt') # download puncuation model
nlp = spacy.load('en_core_web_sm')


def create_rdf(db_entry):
    # create rdf triples from db entry
    # print (db_entry)
    # db_entry = db_entry[0]
    rdf = ''
    entity_name = db_entry[-1]  # entity name
    commodity_code = db_entry[-2]  # get commodity code
    class_name = db_entry[-3]
    class_code = db_entry[-4]
    family_name = db_entry[-5]
    family_code = db_entry[-5]
    rdf += entity_name + ' commodity-code ' + str(commodity_code) + ' \n'
    rdf += entity_name + ' class-name ' + class_name + ' \n'
    rdf += entity_name + ' class-code ' + str(class_code) + ' \n'
    rdf += entity_name + ' family-name ' + family_name + ' \n'
    rdf += entity_name + ' family-code ' + str(family_code)

    return entity_name, rdf


def get_unspc(db_f):
    # create rdf triples from database
    unspc_rdf = []
    entities = []
    unspc_db = pd.read_csv(db_f, encoding="ISO-8859-1")
    # unspc_db_0 = unspc_db.head(1).values.tolist()
    # print (create_rdf(unspc_db_0))
    for j, r in unspc_db.iterrows():
        # print (r.values.tolist())
        ent, rdf = create_rdf(r.values.tolist())
        entities.append(ent.lower())
        unspc_rdf.append(rdf)
    return unspc_rdf, entities


def search_entity(entity_name, entity_list, threshold):
    similar_ents = process.extract(entity_name, entity_list, scorer=fuzz.token_ratio, limit=2)
    # print(similar_ents)
    similar_ents = [(e, j) for e, s, j in similar_ents if s >= threshold]
    return similar_ents


def get_ent(query, entity_list, threshold=100):
    # search for an entity in the rdf given a query
    query_ents = []
    doc = nlp(query)
    for np in doc.noun_chunks:
        # print (np.text)
        if np.text not in stops: # skip for stop words like i, we
            sim_ent = search_entity(np.text, entity_list, threshold)
            if sim_ent:
                for ent in sim_ent:
                    query_ents.append([np.text, ent])
    return query_ents


def get_kg_triple(query, entity_list, unspc_rdf):
    query_ents = get_ent(query, entity_list)
    # print(query_ents)
    kg_ = []
    for e, (ent, j) in query_ents:
        kg_.append(unspc_rdf[j])
    return '\n'.join(k for k in kg_)


if __name__ == '__main__':
    urdf, ents = get_unspc('data/data-unspsc-codes.csv')
    query = 'I need help with the unspc for safety shoes'
    # query = truecase.get_true_case(query)
    rdf_kg = get_kg_triple(query, ents, urdf)
    print(rdf_kg)



