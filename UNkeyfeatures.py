import userNetworkFunction as un
from collections import deque
import numpy as np
'''Comparing two opposing subreddits'''
subs = ['liberal', 'conservative']
#users = [None] * len(subs)
#i=0
'''In fact we only ever compare two subreddits I guess so all these loops are not 
really needed like this but now I already made them so I'll just let them be'''
# for sub in subs:
#     users[i] = un.createUN(sub) #dictionary with user id as key
#     i+=1
    
def compareScores(users):   
    try:
        del users[0]['[deleted]'] # we don't want this stuff
        del users[1]['[deleted]']
    except Exception:
        print(Exception)
    activeInOneSub = [None]*len(subs)
    
    for i in range(len(subs)):
        activeInOneSub[i] = set(users[i]).difference(set(users[(i+1)%len(subs)])) # solely active in one sub
        
    activeInBoth = set(users[0]).intersection(set(users[1]))
    
    
    postScoresOneSub = [None]*len(subs) #solely active in sub 1 or 2
    commentScoresOneSub = [None]*len(subs) #solely active in sub 1 or 2
    
    postScoresBothSubs = [None]*len(subs) #active in both subs, score aggregrate for both subs separately!
    commentScoresBothSubs = [None]*len(subs)
    
    for i in range(len(subs)):
        postScoresOneSub[i] = deque()
        commentScoresOneSub[i] = deque()
        postScoresBothSubs[i] = deque()
        commentScoresBothSubs[i] = deque()
        for user in activeInOneSub[i]:
            postScoresOneSub[i].append(users[i][user].postScore)
            commentScoresOneSub[i].append(users[i][user].commentScore)
        for user in activeInBoth:
            postScoresBothSubs[i].append(users[i][user].postScore)
            commentScoresBothSubs[i].append(users[i][user].commentScore)
    
    print(f"Post scores mean and CI for inside subs: \n {np.mean(postScoresOneSub[0])}, \
          {1.96*np.std(postScoresOneSub[0])/np.sqrt(len(postScoresOneSub[0]))} and \n {np.mean(postScoresOneSub[1])}, \
           {1.96*np.std(postScoresOneSub[1])/np.sqrt(len(postScoresOneSub[1]))}  for intersection: \n {np.mean(postScoresBothSubs[0])}, \
        {1.96*np.std(postScoresBothSubs[0])/np.sqrt(len(postScoresBothSubs[0]))} and \n {np.mean(postScoresBothSubs[1])}, \
        {1.96*np.std(postScoresBothSubs[1])/np.sqrt(len(postScoresBothSubs[1]))}")
    print(f"Comment scores mean and CI for inside subs: \n {np.mean(commentScoresOneSub[0])}, \
          {1.96*np.std(commentScoresOneSub[0])/np.sqrt(len(commentScoresOneSub[0]))} and \n {np.mean(commentScoresOneSub[1])}, \
           {1.96*np.std(commentScoresOneSub[1])/np.sqrt(len(commentScoresOneSub[1]))} for intersection: \n {np.mean(commentScoresBothSubs[0])}, \
        {1.96*np.std(commentScoresBothSubs[0])/np.sqrt(len(commentScoresBothSubs[0]))} and \n {np.mean(commentScoresBothSubs[1])}, \
        {1.96*np.std(commentScoresBothSubs[1])/np.sqrt(len(commentScoresBothSubs[1]))}")
    print(f"Post and comment scores over entire subreddits: \n \
          {np.mean(postScoresOneSub[0]+postScoresBothSubs[0])}, {1.96*np.std(postScoresOneSub[0]+postScoresBothSubs[0])/np.sqrt(len(postScoresOneSub[0]+postScoresBothSubs[0]))}, \n \
           {np.mean(postScoresOneSub[1]+postScoresBothSubs[1])}, {1.96*np.std(postScoresOneSub[1]+postScoresBothSubs[1])/np.sqrt(len(postScoresOneSub[1]+postScoresBothSubs[1]))}, \n \
           {np.mean(commentScoresOneSub[0]+commentScoresBothSubs[0])}, {1.96*np.std(commentScoresOneSub[0]+commentScoresBothSubs[0])/np.sqrt(len(commentScoresOneSub[0]+commentScoresBothSubs[0]))} \n \
           {np.mean(commentScoresOneSub[1]+commentScoresBothSubs[1])}, {1.96*np.std(commentScoresOneSub[1]+commentScoresBothSubs[1])/np.sqrt(len(commentScoresOneSub[1]+commentScoresBothSubs[1]))} \n \
               ")                 
