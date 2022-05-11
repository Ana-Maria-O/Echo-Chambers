import pickle
from keyfeatures_2_riccardo import getTime
from statistics import mean, stdev
import matplotlib.pyplot as plt
from itertools import product

# Only for one time slice
timeSlice = 0

# Path to key features
path_KF_PushShift = "Results/Pushshift"
subreddits_PushShift = ["CMV", "News", "The_Donald"]

path_KF = f"Results/{getTime(timeSlice)}"
subreddits = ['atheism',
        'christianity',
        'conservative',
        'conspiracy',
        'exchristian',
        'flatearth',
        'liberal',
        'lockdownskepticism',
        'news',
        'politics',
        'science']

# Load key features of UN
KF_UN_PushShift = {}
KF_UN = {}

# PushShift
for subreddit in subreddits_PushShift:
    with open(path_KF_PushShift + f'/{subreddit}_key_features.pickle', 'rb') as f:
        KF_UN_PushShift[subreddit] = pickle.load(f)

# Other
for subreddit in subreddits:
    with open(path_KF + f'/{subreddit}_key_features.pickle', 'rb') as f:
        KF_UN[subreddit] = pickle.load(f)

# Load key features of PCN
KF_PCN_PushShift = {subreddit: dict() for subreddit in subreddits_PushShift}
KF_PCN = {subreddit: dict() for subreddit in subreddits}

# PushShift
with open(path_KF_PushShift + f'/key_features_PCN.pickle', 'rb') as f:
    data = pickle.load(f)

    for KF, val in data.items():

        # KF are subreddit specific
        if type(val) == dict:
            for subreddit in val.keys():
                KF_PCN_PushShift[subreddit][KF] = val[subreddit]

# Other
with open(path_KF + f'/key_features_PCN.pickle', 'rb') as f:
    data = pickle.load(f)

    for KF, val in data.items():

        # KF are subreddit specific
        if type(val) == dict:
            for subreddit in val.keys():
                KF_PCN[subreddit][KF] = val[subreddit]


# Compute key feature statistics

def computeStatistics(dictionary):
    # Output structure
    KF_Stats = {subreddit: dict() for subreddit in dictionary.keys()}

    # Non-numerical KFs
    excluding_KF = ["Communities", "VoteRank"]

    for subreddit in dictionary.keys():
        for key in dictionary[subreddit].keys():
            if key not in excluding_KF:
                data = dictionary[subreddit][key]
                if type(data) == list:
                    KF_Stats[subreddit][key] = [mean(data)] # could add stdev later
                elif type(data) == dict:
                    KF_Stats[subreddit][key] = [mean(data.values())]

    return KF_Stats

## PushShift

# Statistics for UN
KF_UN_PushShift_Stats = computeStatistics(KF_UN_PushShift)

# Statistics for PCN
KF_PCN_PushShift_Stats = computeStatistics(KF_PCN_PushShift)

## Other

# Statistics for UN
KF_UN_Stats = computeStatistics(KF_UN)

# Statistics for PCN
KF_PCN_Stats = computeStatistics(KF_PCN)

# Function to produce a scatter grid
def scatterGrid(dict_x, dict_y, fName):
    # Get the names of the KFs
    KF_List_x = list(dict_x[list(dict_x.keys())[0]].keys())
    KF_List_y = list(dict_y[list(dict_y.keys())[0]].keys())

    n_KF_x = len(KF_List_x)
    n_KF_y = len(KF_List_y)


    fig, axs = plt.subplots(ncols=n_KF_x, nrows=n_KF_y, figsize=(n_KF_x * 5,n_KF_y * 5))

    for i,j in [(i,j) for i in range(n_KF_y) for j in range(n_KF_x)]:
        axs[i][j].scatter(\
            x = [dict_x[subreddit][KF_List_x[j]][0] for subreddit in dict_x.keys()],\
            y = [dict_y[subreddit][KF_List_y[i]][0] for subreddit in dict_y.keys()])

        axs[i][j].set_xlabel(KF_List_x[j])
        axs[i][j].set_ylabel(KF_List_y[i])

    saveFolder = "KeyFeaturePlots/"
    plt.tight_layout()
    fig.savefig(saveFolder + fName + '.png')


## PushShift

# Scatter grid only UN
scatterGrid(KF_UN_PushShift_Stats, KF_UN_PushShift_Stats, "KF_UN_PushShift_UN_PushShift")

# Scatter grid only PCN
scatterGrid(KF_PCN_PushShift_Stats, KF_PCN_PushShift_Stats, "KF_PCN_PushShift_PCN_PushShift")

# Scatter grid both UN and PCN
scatterGrid(KF_UN_PushShift_Stats, KF_PCN_PushShift_Stats, "KF_UN_PushShift_PCN_PushShift")

## Other

# Scatter grid only UN
scatterGrid(KF_UN_Stats, KF_UN_Stats, "KF_UN_UN")

# Scatter grid only PCN
scatterGrid(KF_PCN_Stats, KF_PCN_Stats, "KF_PCN_PCN")

# Scatter grid both UN and PCN
scatterGrid(KF_UN_Stats, KF_PCN_Stats, "KF_UN_PCN")