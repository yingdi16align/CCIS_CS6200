import json

class UseIndex(object):
    def __init__(self, DocumentIDFile_path, TermIDFile_path, InvertedIndex_path):
        self.term_record={} 
        self.file_record = {}
        TermIDFile_data = open(TermIDFile_path, 'r').read().split('\n')
        DocumentIDFile_data = open(DocumentIDFile_path, 'r').read().split('\n')
        
        for strstr in TermIDFile_data:
            splitted= strstr.split(',')
            if len(splitted) == 3:
                id_term= splitted[0]
                term = splitted[1]
                fre = splitted[2]
                self.term_record[term] = [id_term, fre]

        for strstr2 in DocumentIDFile_data:
            splitted= strstr2.split(',')
            if len(splitted) == 3:
                id_doc = splitted[0]
                file_name = splitted[1]
                length = splitted[2]
                self.file_record[id_doc] = [file_name, length]            
        
        with open(InvertedIndex_path, 'r') as f:
            self.inverted_index = json.load(f)

#1.takes in a term Term, and return the corresponding TermID
    def get_term_id(self, term):
        term = term.lower()
        if term in self.term_record:
            return self.term_record[term][0]
        else:
            return None

#2.take a TermID and looks up its inverted list iList, 
    def get_inverted_list(self, id_term):
        return self.inverted_index[id_term]

#3.take a term, find the TermID and the corresponding inverted list, and return the DocumentIDs where this term occurs,
    def get_id_doc_by_term(self, term):
        id_term = self.get_term_id(term)
        if not id_term:
            return None
        else:
            inverted_list = self.get_inverted_list(id_term)
            #There shouldn't be any duplicates in the result
            files=set()
            for value in inverted_list.items():
                files.add(value[0])
            return files

#4.take a DocumentID and returns the document name it corresponds to.
    def get_file_name_by_id(self, id_doc):
        return self.file_record[id_doc][0]

# function needed in RunRankedRetrieval   
# get term frequency     
def get_term_fre(self, term):
    if term in self.term_record:
        return self.term_record[term][1]
    else:
        return 0
        
# function needed in RunRankedRetrieval 
# get term frequency in a certain file             
def get_term_freq_file(self, term, id_doc):
    id_term = self.get_term_id(term)
    if id_doc in self.inverted_index[id_term]:
        return self.inverted_index[id_term][id_doc]
    else:
        return 0

if __name__ == '__main__':
    inverted_index = UseIndex("IndexFolderName/DocumentIDFile.txt", "IndexFolderName/TermIDFile.txt", "IndexFolderName/InvertedIndex.json")
    term = 'mungo'
    print('Searching for query: '+term)
    term = term.lower()
    id_docs = inverted_index.get_id_doc_by_term(term)
    if id_docs is not None:
        for id_doc in id_docs:
            print(inverted_index.get_file_name_by_id(id_doc))
    else:
        print("Couldn't find query:" + term)
    