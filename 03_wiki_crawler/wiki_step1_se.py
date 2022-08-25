import pickle
import json
import concurrent.futures
import requests
import traceback

EN_WIKI = "https://en.wikipedia.org/w/api.php?"
FA_WIKI = "https://fa.wikipedia.org/w/api.php?"

WORD_LIST_BATCH_SIZE = 10
WORKERS = 8
LOG_INTERVAL = 100

def bathify_list(input_list, batch_size):
    l = len(input_list)
    return [input_list[i:min(i+batch_size, l)] for i in range(0, l, batch_size)]

def get_word_list(en_words, batch_size, idx):
    pairs = []
    orphans = []
    batches = bathify_list(en_words, batch_size)
    session = requests.Session()
    l = len(batches)
    for i, batch in enumerate(batches):
        if i % LOG_INTERVAL == 0:
            print(f'Thread {idx}: {i}/{l}')
        titles = '|'.join(batch)
        params = f"action=query&prop=langlinks&titles={titles}&format=json&lllang=fa&redirects"
        params = params.replace('#', '')
        
        response = session.request("GET", f'{EN_WIKI}{params}')
        try:
            res_json = response.json()
        except Exception as ex:
            print(params)
            raise ex
        
        for row in res_json['query']['pages'].values():
            if 'pageid' in row:
                en_word = row['title']
                if 'langlinks' in row:
                    fa_word = row['langlinks'][0]['*']
                    pairs.append((en_word, fa_word))
                else:
                    orphans.append(en_word)

    return pairs, orphans

def threaded_function(args):
    try:
        idx, _input_list, return_value = args
        word_pairs, orphans = get_word_list(_input_list, WORD_LIST_BATCH_SIZE, idx)
        return_value['pairs'] = word_pairs
        return_value['orphans'] = orphans
    except Exception as ex:
        print(f'_______THREAD ERROR IN {idx}_______')
        print(ex)
        traceback.print_exc()

with open('./outputs/searched_title.json', 'r') as f:
    INPUT_LIST = list(set(json.load(f)))

bath_size = len(INPUT_LIST) // (WORKERS)
thread_args = [(idx, batch, {})for idx, batch in enumerate(bathify_list(INPUT_LIST, bath_size))]
    
with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
    executor.map(threaded_function, thread_args)

all_pairs = []
all_orphans = []
for _, _, return_dict in thread_args:
    all_pairs += return_dict['pairs']
    all_orphans += return_dict['orphans']   
    
with open('./outputs/pairs_searched.json', 'w') as f:
    json.dump(all_pairs, f)
    
with open('./outputs/orphans_searched.json', 'w') as f:
    json.dump(all_orphans, f)