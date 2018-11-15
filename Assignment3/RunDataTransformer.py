import re
import os
import operator
import json

# split with all punctuations
pattern = r',| |\n|\r|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）'

term_set = set()
#record the term, term id, and frequency in files
term_record={}
sum_bytes_size=0
# not unique
total_num_terms = 0
#record the file id, file name, and num of terms
file_record={}

def handle_line(line):
    # remove all html tags
    line = re.sub(r'</?\w+[^>]*>','',line)
    # delete any non-English or Unicode characters ---- replace them with a space
    line = re.sub(r'[^\x00-\x7F]+',' ', line)
    # replace ' with a space, so McDonald’s ---> McDonald s
    line = re.sub(r'\'', ' ', line)
    # Convert acronyms like I.B.M. to IBM
    line = re.sub(r'\.', '', line)
    return line

#get all the terms in a file
def get_terms_from_file(file_name):
    result=list()
    with open(file_name) as f:
        for line in f:
            line = handle_line(line)
            for s in re.split(pattern, line):
                s = s.strip()
                global total_num_terms
                total_num_terms += 1
                result.append(s)
    return result
    
def generate_inverted_index(file_terms):
    id_doc=0
    id_term=0
    inverted_index = dict()
    for file_name, terms in file_terms.items():
        file_record[id_doc] = [file_name, len(terms)]
        id_doc += 1
        for term in terms:
            if term not in term_set:
                term_set.add(term)
                id_term += 1
                #id:{xx.txt:1,yy.txt:1}
                inverted_index[id_term] = {id_doc: 1} 
                term_record[term] = [id_term, 1]
            else:
                idd = term_record[term][0]
                if id_doc in inverted_index[idd]:
                    current = inverted_index[idd]
                    fre = current.get(id_doc)
                    fre = fre + 1
                    current[id_doc] = fre
                    term_record[term][1] += 1
                else:
                    inverted_index[idd].update({id_doc: 1})
                    term_record[term][1] += 1
    return inverted_index
  
def write_InvertedIndex(inverted_index):
    new_file_name = "IndexFolderName/InvertedIndex.json"
    f = open(new_file_name, "w+")
    json.dump(inverted_index, f, sort_keys=True)
    #for (key, value) in inverted_index.items():
        #json.dump(inverted_index, file_inverted_index, sort_keys=True)
        #index_str = "" + str(key) + " : " + str(value) + "\n"
        #f.write(index_str)

def write_TermIDFile():
    new_file_name = "IndexFolderName/TermIDFile.txt"
    f = open(new_file_name, "w+")
    for term, value in term_record.items():
        id_term = value[0]
        fre = value[1]
        strstr = ""+ str(id_term) + ","+term + "," + str(fre) + "\n"
        f.write(strstr)
    
def write_DocumentIDFile():
    new_file_name = "IndexFolderName/DocumentIDFile.txt"
    f = open(new_file_name, "w+")
    for id_doc, value in file_record.items():
        file_name= value[0]
        terms_count= value[1]
        strstr = ""+ str(id_doc) + ","+file_name + "," + str(terms_count) + "\n"
        f.write(strstr)
   
def write_to_files(inverted_index):
    write_InvertedIndex(inverted_index)
    write_TermIDFile()
    write_DocumentIDFile()
    
#main function
def handle_files(folder_name,num_files):
    path = folder_name+"/"
    file_terms = {}
    file_names = os.listdir(path)
    file_names.sort()
    for i in range(1, num_files+1):
        file_name = file_names[i]
        with open(path+file_name) as f:
            global sum_bytes_size
            sum_bytes_size =sum_bytes_size+os.path.getsize(path+file_name)
            file_terms[file_name] = get_terms_from_file(path+file_name)
    os.mkdir('IndexFolderName')
    inverted_index = generate_inverted_index(file_terms)
    write_to_files(inverted_index)
    #total_index_size= os.path.getsize("IndexFolderName/TermIDFile.txt") + os.path.getsize("IndexFolderName/DocumentIDFile.txt") + os.path.getsize("IndexFolderName/InvertedIndex.txt")
    #ratio = total_index_size / sum_bytes_size
    #print("The file size of all the input files is :" + str(sum_bytes_size) + "bytes")
    #print("The total number of tokens across all input files :" + str(total_num_terms))
    #print("The total number of unique tokens across all input files :" + str(len(term_set)))
    #print("Total index size, that is total size of the three index files (in bytes): " + str(total_index_size))
    #print("Ratio of the total index size to the total file size: " + str(ratio))
    
handle_files('ContentFolderName',900)