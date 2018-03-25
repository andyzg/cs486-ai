from bn import *

NOT_RECORDED = -1
NOT_PRESENT = 0
MILD = 1
SEVERE = 2


class Case:

    def __init__(self, sloe, fori, dega, trimo, dunn):
        self.sloepnea = sloe
        self.foriennditis = fori
        self.degar_spots = dega
        self.trimono = trimo
        self.dunnetts = dunn

    @property
    def s(self):
        return self.sloepnea

    @property
    def f(self):
        return self.foriennditis

    @property
    def d(self):
        return self.degar_spots

    @property
    def t(self):
        return self.trimono

    @property
    def dunnetts(self):
        return self.dunnetts


def load_data(filename):
    data = []
    with open(filename, 'r') as f:
        for l in f.readlines():
            sloe, fori, dega, trimo, dunn = l.strip().split(' ')
            case = Case(sloe, fori, dega, trimo, dunn)
            data.append(case)

    return data


def main():
    print load_data('traindata.txt')


# Pr(Dunnetts)
f0 = to_structured_array(np.array([[0,.5],
                                  [1,.25],
                                  [2,.25]]), 'dunnetts,val')

# Pr(Trimono)
f1 = to_structured_array(np.array([[0,.9], [1,.1]]), 'trimono,val')

# Pr(foriennditis|dunnetts)
f2 = to_structured_array(np.array([[0,0,.99],
                                   [0,1,.01],
                                   [1,0,.7],
                                   [1,1,.3],
                                   [2,0,.2],
                                   [2,1,.8]]),
                         'dunnetts,foriennditis,val')

# Pr(foriennditis|dunnetts)
f3 = to_structured_array(np.array([[0,0,.99],
                                   [0,1,.01],
                                   [1,0,.3],
                                   [1,1,.8],
                                   [2,0,.7],
                                   [2,1,.3]]),
                         'dunnetts,degar,val')

# Pr(foriennditis|dunnetts)
f4 = to_structured_array(np.array([[0,0,0,.99],
                                   [0,0,1,.01],
                                   [0,1,0,.999],
                                   [0,1,1,.001],
                                   [1,0,0,.5],
                                   [1,0,1,.5],
                                   [1,1,0,.95],
                                   [1,1,1,.05],
                                   [2,0,0,.5],
                                   [2,0,1,.5],
                                   [2,1,0,.95],
                                   [2,1,1,.05]]),
                         'dunnetts,trimono,sloepnea,val')

if __name__ == '__main__':
    main()
