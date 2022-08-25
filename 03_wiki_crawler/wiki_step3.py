import pickle
import json
import concurrent.futures
import requests
import traceback

EN_WIKI = "https://en.wikipedia.org/w/api.php?"
FA_WIKI = "https://fa.wikipedia.org/w/api.php?"

WORKERS = 8
LOG_INTERVAL = 20

def bathify_list(input_list, batch_size):
    l = len(input_list)
    return [input_list[i:min(i+batch_size, l)] for i in range(0, l, batch_size)]

class WikipediaConnection:
    def __init__(self, wiki_link):
        self.wiki_link = wiki_link
        self.session = requests.Session()

    def get_text(self, title):
        params = f"action=query&prop=extracts&titles={title}&format=json&explaintext=true"

        response = requests.request("GET", f'{self.wiki_link}{params}')

        res_json = response.json()

        text = next(iter(res_json['query']['pages'].values()))['extract']

        return text

def threaded_function(args):
    try:
        idx, con_url, batch, res = args
        con = WikipediaConnection(con_url)
        l = len(batch)
        for i, word in enumerate(batch):
            if i % LOG_INTERVAL == 0:
                print(f'Thread {idx}: {i}/{l}')
            res[word] = con.get_text(word)
    except Exception as ex:
        print(f'_______THREAD ERROR IN {idx}_______')
        print(ex)
        traceback.print_exc()
        
def parallel_run(word_pairs, orphans):
    en_words, fa_words = tuple(zip(*word_pairs))
    en_words = en_words + tuple(orphans)
    
    
    en_bath_size = len(en_words) // (WORKERS // 2)
    fa_bath_size = len(fa_words) // (WORKERS // 2)
    
    thread_args = []
    thread_args += [(EN_WIKI, batch, {})for batch in bathify_list(en_words, en_bath_size)]
    thread_args += [(FA_WIKI, batch, {})for batch in bathify_list(fa_words, fa_bath_size)]
    thread_args = [(idx,) + old_args for idx, old_args in enumerate(thread_args)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        executor.map(threaded_function, thread_args)
    
    en_all_dict = {}
    fa_all_dict = {}
    for _, wiki_type, _, res in thread_args:
        if wiki_type == EN_WIKI:
            en_all_dict.update(res)
        else:
            fa_all_dict.update(res)
    
    return en_all_dict, fa_all_dict
            

with open('./outputs/pairs_merged.json', 'r') as f:
    pairs = json.load(f)
    
with open('./outputs/orphans_merged.json', 'r') as f:
    orphans = json.load(f)

en_papers, fa_papers = parallel_run(pairs, orphans)

with open('./outputs/en_papers.json', 'w') as f:
    json.dump(en_papers, f)
    
with open('./outputs/fa_papers.json', 'w') as f:
    json.dump(fa_papers, f)