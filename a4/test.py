from bn import *

# Pr(Dunnetts)
f0 = to_structured_array(np.array([[0,0.4832218],
                                  [1,0.17406296],
                                  [2,0.34271524]]), 'dunnetts,val')

# Pr(Trimono)
f1 = to_structured_array(np.array([[0,0.83827392], [1,0.16172608]]), 'trimono,val')

# Pr(foriennditis|dunnetts)
f2 = to_structured_array(np.array([[0,0,9.99159045e-01],
                                   [0,1,8.40955034e-04],
                                   [1,0,8.29237585e-01],
                                   [1,1,1.70762415e-01],
                                   [2,0,9.93489667e-01],
                                   [2,1,6.51033303e-03]]),
                         'dunnetts,foriennditis,val')

# Pr(foriennditis|dunnetts)
f3 = to_structured_array(np.array([[0,0,0.9989564],
                                   [0,1,0.0010436],
                                   [1,0,0.99287719],
                                   [1,1,0.00712281],
                                   [2,0,0.66015769],
                                   [2,1,0.33984231]]),
                         'dunnetts,degar,val')

# Pr(sloepnea|dunnetts, trimono)
f4 = to_structured_array(np.array([[0,0,0,9.99673034e-01],
                                   [0,0,1,3.26966356e-04],
                                   [0,1,0,9.99999999e-01],
                                   [0,1,1,1.17813133e-09],
                                   [1,0,0,6.52635461e-01],
                                   [1,0,1,3.47364539e-01],
                                   [1,1,0,9.99999892e-01],
                                   [1,1,1,1.08335547e-07],
                                   [2,0,0,2.97571153e-01],
                                   [2,0,1,7.02428847e-01],
                                   [2,1,0,9.99999995e-01],
                                   [2,1,1,4.94930316e-09]]),
                         'dunnetts,trimono,sloepnea,val')

print(inference([f0, f1, f2, f3, f4], 'sloepnea', [], {
    'dunnetts': 1,
    'foriennditis': 1,
    'trimono': 1,
    'degar': 1,
    }))
