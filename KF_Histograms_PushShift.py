from configparser import Interpolation
import pickle
from keyfeatures_2_riccardo import getTime
from statistics import mean, stdev
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os
from keyfeatures_2_riccardo import *
from userNetworkFunction import createDirectory
import seaborn as sns
import matplotlib.pyplot as plt
from OpenNetwork import getBins
import numpy as np
from scipy.stats import gaussian_kde
from matplotlib.colors import LogNorm
import matplotlib.colors as mcolors
from itertools import combinations
from math import sqrt, ceil, floor


plt.rcParams.update({'font.size': 20})


# Path to key features
# subreddits_PushShift = ["CMV", "The_Donald"]
# subreddits_PushShift = ['Changemyview', 'News', 'The_Donald', 'AMA', 'conspiracy', 'askscience', 'enoughtrumpspam',  'fuckthealtright', 'explainlikeimfive', 'incels', 'politicaldiscussion']

ground_truth = ['Changemyview', 'News', 'The_Donald']
echo_chamber_subreddits = ['conspiracy', 'enoughtrumpspam',  'fuckthealtright', 'incels']
anti_echo_chamber_subreddits = ['AMA', 'askscience', 'explainlikeimfive', 'politicaldiscussion']

subreddits_PushShift = ground_truth

resultsPath = f"Results/Pushshift/"

# fileName = 'KFs_PCN_GroundTruth.pickle'
fileName = 'KFs_PCN_NEW_all_subs.pickle'

# PushShift
with open(resultsPath + fileName, 'rb') as f:
    PushShift_PCN_KF = pickle.load(f)

    # for KF, val in data.items():

    #     # KF are subreddit specific
    #     if type(val) == dict:
    #         for subreddit in val.keys():
    #             KF_PCN_PushShift[subreddit][KF] = val[subreddit]

# sub = subreddits_PushShift[2]

KFs = ["final avg comment controversiality", "final avg comment score"]

try:
    for KF in KFs:
        PushShift_PCN_KF[KF + " val"] = {s: dict() for s in subreddits_PushShift}
        for sub in subreddits_PushShift:
            PushShift_PCN_KF[KF + " val"][sub] = {postID: PushShift_PCN_KF[KF][sub][postID][0] for postID in PushShift_PCN_KF[KF][sub].keys()}
except:
    pass


print(list(PushShift_PCN_KF['tree depth dist'].keys()))

percentile = 99

heatFolder = "HeatMaps/"

keyToTitle = \
    {
        'replies between users': "'Replies between users",
        'postControversiality, commentControversiality': "Comment controversiality",
        "tree width dist": "Tree width",
        "tree depth dist": "Tree depth",
        "postCommentRatio": "Post-comment ratio",
        "nr levels in post trees between users' replies": "Reply distance",
        'most active users per subreddit': "User activity"
    }

keyToTitleHeat = \
    {
        "tree width": "Tree width",
        # "final avg comment controversiality val": "Average comment controversiality",
        # "final avg comment score val": "Average comment score",
        "sandwichesValues": "Sandwiches",
        "tree depth": "Tree depth"
    }

# combs = combinations(keyToTitleHeat.keys(), 2)

combs = [("tree width", "sandwichesValues"), ("tree depth", "sandwichesValues")]

for KF1, KF2 in combs:
    print(KF1, KF2)
    for shareAxes in [False]:
        n = len(subreddits_PushShift)
        cols = ceil(sqrt(n))
        rows = ceil(sqrt(n))
        cols, rows = 3, 1
        fig, axsMult = plt.subplots(ncols= cols, nrows = rows, sharey=shareAxes, sharex = shareAxes, figsize=(7 * cols, 7 * rows))

        try:
            axs = []
            for xi in range(cols):
                for yi in range(rows):
                    # make sure that a plot is present
                    if xi + yi * rows < n:
                        axs.append(axsMult[yi][xi])
        except Exception as e:
            axs = axsMult

        if n == 1:
            axs = [axs]

        xmax = 0
        ymax = 0

        xmin = 0
        ymin = 0

        xbins = []
        ybins = []

        xlist = []
        ylist = []

        for i in range(n):
            sub = subreddits_PushShift[i]

            xvalues = PushShift_PCN_KF[KF1][sub]
            yvalues = PushShift_PCN_KF[KF2][sub]

            x = []
            y = []
            
            for post in xvalues.keys():
                try:
                    xval = xvalues[post]
                    yval = yvalues[post]


                    if xval != 0 and yval != 0 and xval != None and yval != None:
                        x.append(xval)
                        y.append(yval)
                except Exception as e:
                    pass

            x_perc_val = np.percentile(x, percentile)
            y_perc_val = np.percentile(y, percentile)

            res = list(filter(lambda e: e[0] < x_perc_val and e[1] < y_perc_val, list(zip(x,y))))
            x = [e[0] for e in res]
            y = [e[1] for e in res]

            xmax = max(xmax, max(x))
            ymax = max(ymax, max(y))

            xmin = min(xmin, min(x))
            ymin = min(ymin, min(y))

            # Works only for integer values
            xbinsval = max(x) - min(x)
            ybinsval = max(y) - min(y)
            # if type(xbins) == int and type(ybins) == float:
            #     ybins = xbins
            # elif type(xbins) == float and type(ybins) == int:
            #     xbins = ybins
            # elif type(xbins) == float and type(ybins) == float:
            #     xbins = 10
            #     ybins = 10
            if type(xbinsval) == float:
                xbinsval = 20
            if type(ybinsval) == float:
                ybinsval = 20
                
            xlist.append(x)
            ylist.append(y)
        
            xbins.append(xbinsval)
            ybins.append(ybinsval)

        xbinsval = max(xbins)
        ybinsval = max(ybins)

        folder = heatFolder + "subs=" + "-".join(subreddits_PushShift) + "/"
        createDirectory(folder)

        for i in range(len(subreddits_PushShift)):

            x = xlist[i]
            y = ylist[i]
            
            sub = subreddits_PushShift[i]
            
            h = axs[i].hist2d(x, y, bins = (20, 20), cmap = "inferno", range = [[xmin, xmax], [ymin, ymax]], norm=mcolors.PowerNorm(0.3))
            fig.colorbar(h[3], ax=axs[i])
            axs[i].set_title(sub)
            axs[i].set_xlabel(keyToTitleHeat[KF1])
            axs[i].set_ylabel(keyToTitleHeat[KF2])
            title = keyToTitleHeat[KF2] + " against " + keyToTitleHeat[KF1]
            fig.suptitle(title)

            # Save figure
            fig.tight_layout()
            
            
            fig.savefig(folder + title.replace(" ", "_") + "_sharedAxes=" + str(shareAxes) + ".png")









# plt.show()


# nbins = 3000
# k = gaussian_kde([x,y])
# xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]

# zi = k(np.vstack([xi.flatten(), yi.flatten()]))
# plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading = "auto")
# plt.colorbar()
# plt.show()





# saveFolder = "KeyFeaturePlots/"
# def saveHistogram(data, plotTitle, lowerLimit = False):
#     # data[sub] = list()

#     # Create subplots for visualisations of weights and scores
#     fig, axs = plt.subplots(ncols=1, nrows=len(subreddits_PushShift), figsize=(20,9))

#     for i in range(len(subreddits_PushShift)):
#         sub = subreddits_PushShift[i]
#         plotData = data[sub].values()
#         if type(lowerLimit) == int:
#             plotData = list(filter(lambda x: x > lowerLimit, plotData))
#         sns.histplot(data= plotData,  bins = getBins(plotData), ax=axs[i], stat = "percent", log_scale=useLogScale)
#         axs[i].set_title(f"{plotTitle} for {sub}")
#     plt.tight_layout()
#     fig.savefig(saveFolder + plotTitle + ".png", bbox_inches="tight")
    



# print(set(PushShift_PCN_KF['most active users per subreddit']["CMV"].values()))

# for sub in subreddits_PushShift:
#     print(sub)
#     print(len(PushShift_PCN_KF['replies between users'][sub].keys()))

# specialCases = ['average post/comment score', 'average post/comment score',"nr levels in post trees between users' replies","tree width dist","in-degree", 'out-degree', 'replies between users', "tree width", "tree depth", 'nrPosts, nrComments, totalScorePosts, totalScoreComments', "avgScorePosts, avgScoreComments", 'postControversiality, commentControversiality']

# useLogScale = False
# for KF, data in PushShift_PCN_KF.items():
#     print(KF)
#     lowerLim = 0
#     if KF not in specialCases:
#         saveHistogram(data, f"logScale={useLogScale}_" + keyToTitle[KF])
#         if KF == 'most active users per subreddit':
#             lowerLim = 1000
#         elif KF == "postCommentRatio":
#             lowerLim = 3
#         elif KF == "tree depth dist":
#             lowerLim = 30000
#         saveHistogram(data, f"lowerLim={lowerLim}_logScale={useLogScale}_" +keyToTitle[KF], lowerLim)
#     elif KF == 'postControversiality, commentControversiality':
#         saveHistogram(data[1], keyToTitle[KF])
#         saveHistogram(data[1], f"lowerLim={lowerLim}_logScale={useLogScale}_" +keyToTitle[KF], lowerLim)
#     elif KF == 'tree width dist':
#         lowerLim = 12000
#         dataOverLayers = {sub: {} for sub in subreddits_PushShift}
#         for sub, layerDict in data.items():
#             for layer, widthDict in layerDict.items():
#                 for w, n in widthDict.items():
#                     if w in dataOverLayers[sub].keys():
#                         dataOverLayers[sub][w] += n
#                     else:
#                         dataOverLayers[sub][w] = n

#         saveHistogram(dataOverLayers, "logScale={useLogScale}_Width")
#         saveHistogram(dataOverLayers, f"lowerLim={lowerLim}_WidthlogScale={useLogScale}_", lowerLim)

    


# # kfDict['replies between users'] = replies
# # kfDict['in-degree'] = in_degree
# # kfDict['out-degree'] = out_degree
# # kfDict['nrPosts, nrComments, totalScorePosts, totalScoreComments'] = n_posts, n_comments, t_score_posts, t_score_comments
# # kfDict['avgScorePosts, avgScoreComments'] = a_score_posts, a_score_comments
# # kfDict['postControversiality, commentControversiality'] = p_con, c_con
# # kfDict['tree depth'] = depths
# # kfDict['tree width'] = widths
# # kfDict['postCommentRatio'] = p_c_ratio
# # kfDict["nr levels in post trees between users' replies"] = nodes
# # kfDict['average post/comment score'] = averagescore
# # kfDict['most active users per subreddit'] = aclist


