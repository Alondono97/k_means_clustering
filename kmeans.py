
import math 
import os
import random 

def get_data(fileName):
    '''
    open filename file
    read lines to list
    clean out '\n', '\t'
    clean out any empty string lines 
    '''

    with open(fileName,'r', encoding='utf8', errors='ignore') as dataFile:
        lines = dataFile.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.replace('\n', '')
        lines[i] = lines[i].replace('\t','')
        lines[i] = lines[i].replace('-','')
        lines[i] = lines[i].replace('_','')
        
    for i, line in enumerate(lines):
        if lines[i] == '':
            lines.pop(i)

    return lines

def bag_of_words(doc_text_list):
    '''
    take as input a list representation of a single document
    split each line by whitespace, parsing out individual words
    iterate through words and push occurrences into a dictionary
    (here dictionary represents the document vector because it has O(1) retrieval time)
    doc_vec -> {word: number_of_occurences}

    later this gets normalized
    doc_vec -> {word: frequency in doc}
    '''

    doc_list = []
    doc_vec = {} #vector that will represent doc, maps word->occurences, later maps word->normalized frequency
    for line in doc_text_list:
        doc_list = doc_list + line.split()
    
    #iterate through doc_list, map words to nummber of occurences, save in doc_vec
    for word in doc_list:
        if word in doc_vec.keys():
            doc_vec[word] += 1
        else:
            doc_vec[word] = 1
    
    occurences_list = doc_vec.values()
    occurence_sum = sum(occurences_list)

    #normalize the vector by dividing by occurences sum
    for word in doc_vec:
        doc_vec[word] = doc_vec[word]/occurence_sum

    return doc_vec

def doc_vec_dict():
    '''
    iterates through all the files in the train directory
    calls get_data() on each file to get file contents as a list
    calls bag of words() on document lists to get bag of words vectors for each doc
    puts all bag of words vectors into a dictionary that maps filename->bag_of_words_vector
    '''
    script_dir = os.path.dirname(__file__) #<-- absolute path to dir the script is in 
    rel_path = "data/train"
    abs_dir_path = os.path.join(script_dir, rel_path)

    file_list = os.listdir(abs_dir_path)
  
    docs_dictionary = {} #dict of filenames -> doc vectors; file -> {word: freq}
    for file in file_list:
        
        rel_file_path = rel_path + '/' + file

        abs_file_path = os.path.join(script_dir, rel_file_path)
        file_contents = get_data(abs_file_path) #list of file contents by line
        doc_vector = bag_of_words(file_contents) #bag_of_words vector for document
        docs_dictionary[file] = doc_vector #store vector mapped with filename
    
    
    return docs_dictionary

def eucl_dist(doc_vec, cent_vec):
    vec_sum = 0
    for elem in doc_vec:
        if elem in cent_vec:
            vec_sum += (doc_vec[elem] - cent_vec[elem])**2
        else:
            vec_sum += doc_vec[elem]**2

    for elem in cent_vec:
        if elem not in doc_vec:
            vec_sum += cent_vec[elem]**2
    
    euclid_dist = math.sqrt(vec_sum)
    return euclid_dist

def find_closest_centroid(doc_vec, centroid_vec_list):
    '''
    input is a doc_vec dictionary, and a list of centroid_vectors also dictionary
    a vector is represented by a dictionary type
    '''
    closest_cent = 0
    min_dist = eucl_dist(doc_vec, centroid_vec_list[0])

    for i, centroid in enumerate(centroid_vec_list):
        dist = eucl_dist(doc_vec, centroid)
        if dist < min_dist:
            min_dist = dist
            closest_cent = i
        # if dist == 0:
        #     print('centroid: ', i, 'dist:', dist, 'min_dist:', min_dist)

    return closest_cent

def vec_sum(vec_1, vec_2):
    '''
    input: two dictionaries representing vectors
    '''
    # print('vec_1 type: ', type(vec_1))
    sum_vec = {}
    for elem in vec_1:
        # print('2:', elem, 'type:', type(elem), 'vec type: ')
        if elem in vec_2:
            sum_vec[elem] = vec_1[elem] + vec_2[elem]
        else:
            sum_vec[elem] = vec_1[elem]
    
    for elem in vec_2:
        if elem not in vec_1:
            sum_vec[elem] = vec_2[elem]

    return sum_vec


def redefine_centroid(cent_vec, cluster_list):
    '''
    input: a centroid vector, a cluster list that holds doc vectors
    '''
    # print(cluster_list)
    cluster_sum_vec = cluster_list[0]
    cluster_size = len(cluster_list)
    new_centroid = {}
    for elem in cluster_list[1:cluster_size]:
        # print('1: ', elem, 'type: ', type(elem))
        cluster_sum_vec = vec_sum(cluster_sum_vec, elem)
    
    for elem in cluster_sum_vec:
        
        new_centroid[elem] = cluster_sum_vec[elem]/cluster_size
      
    return new_centroid

def find_e(new_clust_list, old_clust_list, e):
    # print('meme')
    diff = 0
    if old_clust_list:
        for i, cluster in enumerate(new_clust_list):
            old_clust = old_clust_list[i]
            old_len = len(old_clust)
            sim = 0
            for new_vec in cluster:
                for old_vec in old_clust:
                    if new_vec == old_vec:
                        sim+=1
            diff += abs(old_len - sim)
    else:
        return e
    return diff/2

def write_to_file(results, filename):
    with open(filename,'w+') as output_file:
        for i, clust in enumerate(results):
            for doc in clust:
                out_str = str(doc) + ' ' + str(i)+'\n'
                output_file.write(out_str)

def kmeans(doc_vec_dict, k):
    '''
    input: doc_vec_dict <- dictionary of document vectors and k (the number of clusters)
    '''
    doc_name_list = list(doc_vec_dict.keys())
    number_of_docs = len(doc_name_list)
    
    random_docs = random.sample(doc_name_list, k)
    cluster_list = []
    cluster_list_docid = []
    old_cluster = []
    centroids_list = [] #empty list, will hold centroid vectors (dictionaries)
    e = 20

    for doc in random_docs:
        #push centroid vectors into the centroid list
        centroids_list.append(doc_vec_dict[doc]) 
    n = 0
    while( e >= 5 ):
    # for j in range(1):
        n += 1
        old_cluster = cluster_list
        cluster_list = []
        cluster_list_docid = []
        for i in range(k):
            cluster_list.append([]) #initialize clusters as empty sets
            cluster_list_docid.append([])
        
        # for i in range(k):
        for doc in doc_vec_dict:
            #assign eac document to nearest cluster centroid
            nearest_cent = find_closest_centroid(doc_vec_dict[doc], centroids_list)
            cluster_list[nearest_cent].append(doc_vec_dict[doc])
            cluster_list_docid[nearest_cent].append(doc)

        for i, cent in enumerate(centroids_list):
            centroids_list[i] = redefine_centroid(cent, cluster_list[i])

        e = find_e(cluster_list, old_cluster, e)
        # print(e)
        
    write_to_file(cluster_list_docid, 'results.txt')
    write_to_file(cluster_list_docid, 'pred.txt')
    print('it: ',n)
    # print(cluster_list_docid)
    


# script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
# rel_path = "data/train/105219"
# abs_file_path = os.path.join(script_dir, rel_path)

# doc1 = get_data(abs_file_path)
# print(bag_of_words(doc1))

docs = doc_vec_dict()
kmeans(docs, 10)