import json
import os

tagList = ["Action", "Adventure", "Comedy", "Drama", "Ecchi", "Fantasy", "Horror", "Mahou Shoujo", "Mecha", "Music", "Mystery","Psychological","Romance","Sci-Fi","Slice of Life","Sports","Supernatural","Thriller"]

downloads_path = os.path.expanduser("~/Downloads")
json_files = [f for f in os.listdir(download_dir) if f.startswith("amq_") and f.endswith(".json")]

with open(os.path.join(download_dir, file_name),'r', encoding='utf8') as f:
