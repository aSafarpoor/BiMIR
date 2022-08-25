import pickle
import json
import concurrent.futures
import requests
import traceback
import urllib.parse

EN_WIKI = "https://en.wikipedia.org/w/api.php?"
FA_WIKI = "https://fa.wikipedia.org/w/api.php?"

WORD_LIST_BATCH_SIZE = 10
WORKERS = 8
LOG_INTERVAL = 100

def bathify_list(input_list, batch_size):
    l = len(input_list)
    return [input_list[i:min(i+batch_size, l)] for i in range(0, l, batch_size)]

def search_word(en_words, idx):
    titles = []
    session = requests.Session()
    l = len(en_words)
    for i, word in enumerate(en_words):
        if i % LOG_INTERVAL == 0:
            print(f'Thread {idx}: {i}/{l}')
        if '#' in word:
            continue
        
        
        word = urllib.parse.quote(word.encode('utf8'))
        params = f"action=query&list=search&srsearch={word}&format=json&srlimit=1&srprop"
        
        response = session.request("GET", f'{EN_WIKI}{params}')
        try:
            res_json = response.json()
        
            for row in res_json['query']['search']:
                titles.append(row['title'])

        except Exception as ex:
            print(params)
            raise ex

    return titles

def threaded_function(args):
    try:
        idx, _input_list, return_value = args
        titles = search_word(_input_list, idx)
        return_value['titles'] = titles
    except Exception as ex:
        print(f'_______THREAD ERROR IN {idx}_______')
        print(ex)
        traceback.print_exc()

with open('./inputs/all_unique_mentions.pickle', 'rb') as f:
    INPUT_LIST = pickle.load(f)

bath_size = len(INPUT_LIST) // (WORKERS)
thread_args = [(idx, batch, {})for idx, batch in enumerate(bathify_list(INPUT_LIST, bath_size))]
    
with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
    executor.map(threaded_function, thread_args)

all_titles = []
for _, _, return_dict in thread_args:
    all_titles += return_dict['titles'] 
    
with open('./outputs/searched_title.json', 'w') as f:
    json.dump(all_titles, f)


