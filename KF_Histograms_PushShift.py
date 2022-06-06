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



# Path to key features
subreddits_PushShift = ["CMV", "News", "The_Donald"]

resultsPath = f"Results/Pushshift/"
# PushShift
with open(resultsPath + f'KFs_PCN_GroundTruth.pickle', 'rb') as f:
    PushShift_PCN_KF = pickle.load(f)

    # for KF, val in data.items():

    #     # KF are subreddit specific
    #     if type(val) == dict:
    #         for subreddit in val.keys():
    #             KF_PCN_PushShift[subreddit][KF] = val[subreddit]

# sub = subreddits_PushShift[2]




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
        "sandwichesValues": "Sandwiches",
        "tree depth": "Tree depth"
    }

for KF1, KF2 in combinations(keyToTitleHeat.keys(), 2):
    print(KF1, KF2)
    for shareAxes in (True, False):
        fig, axs = plt.subplots(ncols=3, sharey=shareAxes, sharex = shareAxes, figsize=(20, 10))

        for i in range(len(subreddits_PushShift)):
            sub = subreddits_PushShift[i]

            xvalues = PushShift_PCN_KF[KF1][sub]
            yvalues = PushShift_PCN_KF[KF2][sub]

            x = []
            y = []

            for post in xvalues.keys():
                xval = xvalues[post]
                yval = yvalues[post]


                if xval != 0 and yval != 0 and xval != None and yval != None:
                    x.append(xval)
                    y.append(yval)


            x_perc_val = np.percentile(x, percentile)
            y_perc_val = np.percentile(y, percentile)

            res = list(filter(lambda e: e[0] < x_perc_val and e[1] < y_perc_val, list(zip(x,y))))
            x = [e[0] for e in res]
            y = [e[1] for e in res]

            # Works only for integer values
            xbins = max(x) - min(x)
            ybins = max(y) - min(y)
            # if type(xbins) == int and type(ybins) == float:
            #     ybins = xbins
            # elif type(xbins) == float and type(ybins) == int:
            #     xbins = ybins
            # elif type(xbins) == float and type(ybins) == float:
            #     xbins = 10
            #     ybins = 10
            if type(xbins) == float:
                xbins = 20
            if type(ybins) == float:
                ybins = 20
            h = axs[i].hist2d(x, y, bins = (xbins, ybins), cmap = "inferno", norm=mcolors.PowerNorm(0.2))
            fig.colorbar(h[3], ax=axs[i])
            axs[i].set_title(sub)
            axs[i].set_xlabel(keyToTitleHeat[KF1])
            axs[i].set_ylabel(keyToTitleHeat[KF2])
            title = keyToTitleHeat[KF2] + " against " + keyToTitleHeat[KF1]
            fig.suptitle(title)

            fig.savefig(heatFolder + title.replace(" ", "_") + "_sharedAxes=" + str(shareAxes) + ".png", bbox_inches="tight")


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


