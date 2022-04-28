from userNetworkFunction import *
from OpenNetwork import *


subreddits = ['christianity',
        'atheism',
        'conservative',
        'conspiracy',
        'exchristian',
        'flatearth',
        'liberal',
        'lockdownskepticism',
        'news',
        'politics',
        'science']

timeSlices = list(range(11))

# for num in timeSlices:
#     for subreddit in subreddits:
#         print(f"Subreddit: {subreddit} at time {getTime(num)}")
#         createUN(subreddit, num)
        
for num in timeSlices:
    for subreddit in subreddits:
        print(f"Subreddit: {subreddit} at time {getTime(num)}")
        computeKeyFeaturesUN(subreddit, num, True)