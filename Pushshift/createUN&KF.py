from userNetworkFunction import *
from OpenNetwork import *
import os

subreddits = ['The_Donald', 'News', 'CMV']
# subreddits = ['christianity',
#         'atheism',
#         'conservative',
#         'conspiracy',
#         'exchristian',
#         'flatearth',
#         'liberal',
#         'lockdownskepticism',
#         'news',
#         'politics',
#         'science']

timeSlices = list(range(11))

# script_dir = os.path.dirname(__file__)
# figs_dir = os.path.join(script_dir, 'Figures/12/abc')
# createDirectory(figs_dir)
# print(figs_dir)

# for num in timeSlices:
#     for subreddit in subreddits:
#         print(f"Subreddit: {subreddit} at time {getTime(num)}")
#         createUN(subreddit, num)
        
# for num in timeSlices:
#     for subreddit in subreddits:
#         print(f"Subreddit: {subreddit} at time {getTime(num)}")
#         computeKeyFeaturesUN(subreddit, num, True)

path = "Forests//PushShift//forest_new" + ".pickle"
# read the file
pfile = open(path, 'rb')

# unpickle the file
f = pickle.load(pfile)

# close the file
pfile.close()

for subreddit in subreddits:
    print(f"Subreddit: {subreddit} of PushShift")
    createUN(subreddit, 0, True, f)

for subreddit in subreddits:
    print(f"Subreddit: {subreddit} of PushShift")
    computeKeyFeaturesUN(subreddit, 0, True, True)