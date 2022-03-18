# Networked Society Honors Track
## How to import and use the Post-Comment Network
### 1)Importing the Post-Comment Network
In order to be able to use the Post-Comment forest you have to import it into your python file first. Make sure you have the keyFeatures.py and forest_train.p files downloaded into the same folder as the python file you want to import them to. Next, you import keyFeatures and the Node and Tree classes into your program:

```import keyFeatures as kf```

```from keyFeatures import Node``` 

```from keyFeatures import Tree```

When you want to import the actual tree, you use the following code:

``` forest = kf.forestImportTrain()```

Congrats, now the Post-Comment network is stored in the variable forest :)

### 2) How to use the forest
I'll be honest, the forest may be a bit confusing to visualize (oops?). Here's a rundown:
- ```forest``` is a dictionary of dictionaries with a tree per key
- ```forest[sub]``` where ```sub``` is the name of a subreddit (i.e. ```'news```) -> dictionary where the keys are the id's of posts in the subreddit ```sub```
- ```forest[sub][id]``` where ```sub``` is as above and ```id``` is a string with the id of a post in the ```sub``` subreddit (i.e. ```'r23sc56```; not a real id) -> tree which has the post with id ```id``` as its root

A tree is a linked list of nodes. There are several parameters that the node holds. Here they are and how to access them (```node``` is a node object; if referring to the root of a tree, it can be equivalent to ```forest[sub][id]```):
- ```node.id``` -> id of node (string)
- ```node.auth``` -> username of comment's/post's author (string)
- ```node.score``` -> score of the post/comment (float)
- ```node.controversial``` -> 1 if post/comment is controversial, 0 otherwise (float)
- ```node.depth``` -> depth of node in the tree (int)
- ```node.next``` -> direct replies to node (list of nodes)
