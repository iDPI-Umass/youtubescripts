import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from youtubetools.config import ROOT_DIR, collection_init


def extract_recs_from_page(file_address):
    assert os.path.isfile(file_address), f"{file_address} not found"
    with open(file_address) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    root = soup.find('ytd-watch-flexy')['video-id']
    recs = [rec['href'].split("?v=")[1][:11] for rec in soup.find_all('a', {'class': 'ytd-compact-video-renderer'})]
    return root, dict.fromkeys(recs, None)


def html_files_to_tree(folder, seed_id):
    assert os.path.exists(os.path.join(os.path.expanduser('~'), folder))
    tree_dict = {}
    html_files = [file for file in os.listdir(os.path.join(os.path.expanduser('~'), folder)) if file.endswith(".html")]
    for html_file in html_files:
        key, value = extract_recs_from_page(os.path.join(os.path.expanduser('~'), folder, html_file))
        tree_dict[key] = value
    first_level_recs = list(tree_dict[seed_id].keys())
    to_delete = [rec_id for rec_id in tree_dict if rec_id not in first_level_recs]
    for rec_id in to_delete:
        del tree_dict[rec_id]
    return {seed_id: tree_dict}


def create_personalized_rec_collection(folder, seed_id):
    collection = f"recs_{seed_id}_2_personal_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    collection_init(collection)
    tree = html_files_to_tree(folder, seed_id)
    with open(os.path.join(ROOT_DIR, "collections", collection, "tree.json"), "w") as file:
        json.dump(tree, file, indent=4)
    return collection
