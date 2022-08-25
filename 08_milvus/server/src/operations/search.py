import sys
import numpy as np


sys.path.append("..")
from config import TOP_K, DEFAULT_TABLE
from logs import LOGGER



def search_in_milvus(table_name, query_sentence,model,milvus_cli, mysql_cli, en_mode=False):
    if not table_name:
        table_name = DEFAULT_TABLE
    try:
        if en_mode:
            vectors = [model.encode_en(query_sentence).tolist()]
        else:
            vectors = [model.encode_cross(query_sentence).tolist()]
        LOGGER.info(f"Successfully insert query list {len(vectors[0])}")
        results = milvus_cli.search_vectors(table_name,vectors,TOP_K)
        vids = [str(x.id) for x in results[0]]
        print("-----------------", vids)
        ids,title,text= mysql_cli.search_by_milvus_ids(vids, table_name)
        distances = [x.distance for x in results[0]]
        return ids,title, text, distances
    except Exception as e:
        LOGGER.error(f" Error with search : {e}")
        sys.exit(1)
