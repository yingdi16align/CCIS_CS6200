import re
import json
from collections import Counter
from math import log10, sqrt
from UseIndex import UseIndex

def extract_terms_from_query(query):
    query = re.sub('([^\w\d])', ' ', query)
    terms = query.split(' ')
    return [term.lower() for term in terms if term]


class RankedRetrieval(object):
    def __init__(self, index_folder_name, content_folder):
        term_id_path, doc_id_path, inverted_index_path = \
            ["{}/{}".format(index_folder_name, file_name)
             for file_name in ['TermIDFile.txt', 'DocumentIDFile.txt', 'InvertedIndex.json']]

        self.inverted_index = UseIndex(term_id_path, doc_id_path, inverted_index_path)
        self.content_folder = content_folder
        self.N = len(self.inverted_index.doc_id_dict)

    # Given a query string, returns a normalized, weighted tf-idf query vector
    def tf_idf_query(self, query):
        terms = extract_terms_from_query(query)
        term_counts = dict(Counter(terms))
        tf_idf = {}

        for term, term_freq in term_counts.items():
            tf = 1 + log10(term_freq)
            df = int(self.inverted_index.get_term_doc_freq(term))
            idf = log10(self.N/df) if df != 0 else 0
            tf_idf[term] = tf * idf

        return normalize_vector(tf_idf)

    # Given a query string and a doc_id, returns a normalized, weighted tf-idf document vector
    def tf_idf_doc(self, query, doc_id):
        terms = extract_terms_from_query(query)
        tf_idf = {}

        for term in terms:
            idf = 1
            doc_freq = self.inverted_index.get_term_freq_in_doc(term, doc_id)
            tf_idf[term] = 0 if doc_freq == 0 else (1 + log10(doc_freq)) * idf

        return normalize_vector(tf_idf)

    def get_top_k_docs(self, query, k):
        doc_id_to_doc_info = {}

        vector_query = self.tf_idf_query(query)
        for doc_id in self.inverted_index.doc_id_dict:
            vector_doc = self.tf_idf_doc(query, doc_id)
            score, contribution_dict = cosine_similarity(vector_query, vector_doc)

            doc_id_to_doc_info[doc_id] = [score, contribution_dict]

        sorted_dict = sorted(doc_id_to_doc_info.items(), key=lambda kv_pair: kv_pair[1][0], reverse=True)
        top_k_entries = {doc_id: doc_info for (doc_id, doc_info) in sorted_dict[:k]}

        # {doc_id => [score, contribution_dict, doc_name, doc_snippet]}
        for doc_id, doc_info in top_k_entries.items():
            top_k_entries[doc_id].append(self.inverted_index.get_doc_name_from_id(doc_id))
            top_k_entries[doc_id].append(self.get_doc_snippet(doc_id, self.content_folder))

        return top_k_entries

    # Given the path to crawled html files and a doc_id, returns a snippet of the html content
    def get_doc_snippet(self, doc_id, html_path):
        noises_regex = ['(<script.*?>[\s\S]*?</script>)',
                        '(<style.*?>[\s\S]*?</style>)',
                        '(<.+?>)|(</[\s\S]*?>)',
                        '(<!--[\s\S]*?-->)',
                        ]
        doc_name = self.inverted_index.get_doc_name_from_id(doc_id)
        content = open('{}/{}'.format(html_path, doc_name), 'r').read()
        content = re.compile('(<div id="mw-content-text" [\s\S]*)</div>',).findall(content)[0]
        for regexp in noises_regex:
            content = re.sub(regexp, '', content)

        return content[:200]


# Given two vectors, returns the cosine similarity score between them and
# a dict containing contribution of score each term to the cosine score
def cosine_similarity(vector_dict1, vector_dict2):
    score = 0
    contribution_dict = {}

    for term, val in vector_dict1.items():
        score += val * vector_dict2[term]
        contribution_dict[term] = val

    return score, contribution_dict


def normalize_vector(dict_vector):
    size = sqrt(sum([val*val for term, val in dict_vector.items()]))
    return {term: val/size for term, val in dict_vector.items()} if size != 0 else dict_vector

#main function
def run_ranked_retrieval(index_folder_name, content_folder_name, queries_file, k):
    rr = RankedRetrieval(index_folder_name, content_folder_name)
    raw_queries = open(queries_file, 'r').read().split('\n')

    # output = { raw_query => [trans_query, top_k_entries] }
    # top_k_entries = { doc_id => [score, contribution_dict, doc_name, doc_snippet] }
    output = {}
    for raw_query in raw_queries:
        terms = extract_terms_from_query(raw_query)
        query = ' '.join(terms)
        output[raw_query] = [query, rr.get_top_k_docs(raw_query, k)]

    with open('Output.json', 'w') as output_file:
        output_file.write(json.dumps(output, indent=2))

run_ranked_retrieval('IndexFolderName', 'ContentFolderName', 'Queries.txt', 5)