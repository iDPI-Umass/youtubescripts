"""
compares two collections of YouTube videos and returns a cosine similarity value for the calculated vectors
"""
import argparse
from youtubetools.analysis import collection_comparison

parser = argparse.ArgumentParser()
parser.add_argument("collection1", type=str)
parser.add_argument("collection2", type=str)

parser.add_argument("--views", action="store_true", help="if true, compares collection on view count")
parser.add_argument("--likes", action="store_true", help="if true, compares collection on like count")
parser.add_argument("--duration", action="store_true", help="if true, compares collection on duration (seconds)")
parser.add_argument("--comments", action="store_true", help="if true, compares collection on comment count")
parser.add_argument("--subscribers", action="store_true", help="if true, compares collection on channel follower count")
parser.add_argument("--year", action="store_true", help="if true, compares collection on upload year")
parser.add_argument("--music", action="store_true", help="if true, compares collection on music")
parser.add_argument("--language", action="store_true", help="if true, compares collection on whisper language")

args = parser.parse_args()

attributes = []
if args.views:
    attributes.append('view_count')
if args.likes:
    attributes.append('like_count')
if args.duration:
    attributes.append('duration')
if args.comments:
    attributes.append('comment_count')
if args.subscribers:
    attributes.append('channel_follower_count')
if args.language:
    attributes.append('whisper_lang')
if args.music:
    attributes.append('accessible_in_youtube_music')
if args.year:
    attributes.append('upload_year')

comparison = collection_comparison(args.collection1, args.collection2, attributes)
print("\ncosine similarity")
print(comparison[0])
print("\ncompared attributes")
print(comparison[1])
print("\nvector bins")
print(comparison[2])
print("\ncollection 1 vectors")
print(comparison[3])
print("\ncollection 2 vectors")
print(comparison[4])
