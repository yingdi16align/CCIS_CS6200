import re
import json
from UseIndex import UseIndex
from math import log10, sqrt

def get_term_from_query(query):
    query = query.lower()
    terms = query.split(' ')
    return terms
    
def normalize_vector(vector):
    total=0
    result={}
    for term, val in vector.items():
        total = total+val*val
    size = sqrt(total)
    if size == 0:
        return vector
    else:
        for term, value in vector.items():
            result[term] = value/size
        return result
    
def get_cosine_similarity(vector1, vector2):
    score = 0
    contributions = {}
    for term, value in vector1.items():
        score += vector2[term]*value
        contributions[term] = value
    return score, contributions

class RankedRetrieval(object):
    def __init__(self, IndexFolderName_path, ContentFolderName_path):
        self.IndexFolderName_path=IndexFolderName_path
        self.use_index = UseIndex(IndexFolderName_path+"/DocumentIDFile.txt", IndexFolderName_path+"/TermIDFile.txt", IndexFolderName_path+"/InvertedIndex.json")
        self.ContentFolderName_path = ContentFolderName_path

    def process_query_normalized_tf_idf_weighted(self, query):
        terms = get_term_from_query(query)
        query_lengths = {}
        term_set=set()
        for term in terms:
            if term in term_set:
                query_lengths[term]+=1
            else:
                query_lengths[term]=1
                term_set.add(term)
        term_vector = {}
        for term, fre in query_lengths.items():
            tf = log10(fre)+1
            df = int(self.use_index.get_term_fre(term))
            if df == 0:
                idf = 0
            else:
                idf = log10((len(self.use_index.file_record))/df)
            term_vector[term] = tf * idf
        return normalize_vector(term_vector)

    def process_file_normalized_tf_idf_weighted(self, query, id_doc):
        terms = get_term_from_query(query)
        file_vector = {}
        for term in terms:
            idf = 1
            fre = self.use_index.get_term_freq_file(term, id_doc)
            if fre == 0:
                file_vector[term] = 0
            else:
                file_vector[term] = idf*(1 + log10(fre))
        return normalize_vector(file_vector)
    
    def generate_snippet(self, id_doc, file_name):
        content = open(file_name, 'r').read()
        # get valid content in valid format
        content = re.compile('(<div id="mw-content-text" [\s\S]*)</div>',).findall(content)[0]
        need_skip = ['(<script.*?>[\s\S]*?</script>)','(<style.*?>[\s\S]*?</style>)','(<.+?>)|(</[\s\S]*?>)',
        '(<!--[\s\S]*?-->)','\n',]
        for skip in need_skip:
            #replace skips
            content = re.sub(skip, '', content)
        return content[:200]

    def top_k_files(self, query, k):
        file_scores= {}
        query_vector = self.process_query_normalized_tf_idf_weighted(query)
        for id_doc in self.use_index.file_record:
            vector_doc = self.process_file_normalized_tf_idf_weighted(query, id_doc)
            score, contributions = get_cosine_similarity(query_vector, vector_doc)
            file_scores[id_doc] = [score, contributions]

        file_scores = sorted(file_scores.items(), key=lambda kv_pair: kv_pair[1][0], reverse=True)
        file_scores=file_scores[:k]
        result={}
        for id_doc, value in file_scores:
            result[id_doc] = value

        for id_doc, value in result.items():
            file_name = self.use_index.get_file_name_by_id(id_doc)
            result[id_doc].append(file_name)
            result[id_doc].append(self.generate_snippet(id_doc, (self.ContentFolderName_path)+"/"+file_name))

        return result

#main function
def run_ranked_retrieval(IndexFolderName_path, ContentFolderName_path, queries_path, k):
    ranked_retrieval = RankedRetrieval(IndexFolderName_path, ContentFolderName_path)
    queries = open(queries_path, 'r').read().split('\n')
    result = {}
    for query in queries:
        terms = get_term_from_query(query)
        top_k=ranked_retrieval.top_k_files(query, k)
        result[query] = [query, top_k]
    out_file_name='Output.txt'
    f = open(out_file_name, "w+")
    f.write(json.dumps(result, indent=2))

run_ranked_retrieval('IndexFolderName', 'ContentFolderName', 'Queries.txt', 5)