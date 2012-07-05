"""

   Simple Descriptive Statistics
   
      No outside libraries are needed.
   
      All take one parameter - a list of numbers
   
"""

from math import sqrt

# median of list X
def median(X):
    S = sorted(X)
    if len(S) % 2 == 1:
        return S[(len(S)+1)/2-1]
    
    l = S[len(S)/2-1]
    u = S[len(S)/2]
    return (float(l + u)) / 2  
  
# mean of list X
def mean(X):
    n = float(len(X))
    avg = sum(X)/n
    return avg 

# standard deviation of list X
def stddev(X):
    Y = []
    mx = mean(X)
    for x in X:
        y = (x - mx) ** 2
        Y.append(y)
        
    my = mean(Y)
    return sqrt(my)

# mode of list X
def mode(X):
    m = X[0]
    d = {}
    for y in X:
        if d.has_key(y):
            d[y] += 1
        else:
            d[y] = 1
            
        if d[y] > d[m]:
            m = y

    return m
