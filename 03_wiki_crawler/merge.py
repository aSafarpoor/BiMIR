import json

with open('./outputs/orphans.json', 'r') as f:
    orphans1 = json.load(f)

with open('./outputs/orphans_searched.json', 'r') as f:
    orphans2 = json.load(f)

with open('./outputs/pairs.json', 'r') as f:
    pairs1 = json.load(f)

with open('./outputs/pairs_searched.json', 'r') as f:
    pairs2 = json.load(f)

merged_orphans = list(set(orphans1) | set(orphans2))

merged_pairs_dict = {}
merged_pairs_dict.update({key: val for key, val in pairs1})
merged_pairs_dict.update({key: val for key, val in pairs2})
merged_pairs = list(merged_pairs_dict.items())

with open('./outputs/orphans_merged.json', 'w') as f:
    json.dump(merged_orphans, f)


with open('./outputs/pairs_merged.json', 'w') as f:
    json.dump(merged_pairs, f)