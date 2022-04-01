def GetSandwiched(test: pd.DataFrame):    

    #given an input dataframe with reddit posts
    #this function returns the number of 'sandwiches' in it

    sand = 0 #sandwich counter! 
    for post in df['post id'].unique(): #iterate over the various post chains
        auths = df[df['post id'] == post]['author']  #and get the authors that posted in said chain 
                                                         #in the order they posted
        auths = auths.reset_index()
        del auths['index']
        auths = auths['author']  
        #ok so these three lines are needed cause when I take the Series above
        #the indexes of things get messed up so I need to reset them
        #and then delete the 'index' column this spawns and just take the authors again

        for k in range(0, len(auths) - 1): #now we iterate over the authors of posts
            auth1 = auths[k] 
            auth2 = auths[k+1]
            try: 
                auth3 = auths[k+2]
            except: 
                auth3 = None 
            #auth1 is the first author, auth2 is the second, and auth3 is the third.
            #such that auth1 -> auth2 -> auth3 at any point in the loop
            #a sandwich is auth1 -> auth2 -> auth1 so auth1 = auth3
            #the try/except is there because if we reach the end of the list there is no more third author
            if auth1 == auth3 and auth1 != auth2:
                sand += 1

    print(sand)