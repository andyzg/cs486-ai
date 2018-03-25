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
f0 = to_structured_array(np.array([['absent',.5],
                                  ['mild',.25],
                                  ['severe',.25]]), 'dunnetts,val')

# Pr(Trimono)
f1 = to_structured_array(np.array([[0,.9], [1,.1]]), 'trimono,val')

# Pr(foriennditis|dunnetts)
f2 = to_structured_array(np.array([['absent',0,.99],
                                   ['absent',1,.01],
                                   ['mild',0,.7],
                                   ['mild',1,.3],
                                   ['severe',0,.2],
                                   ['severe',1,.8]]),
                         'dunnetts,foriennditis,val')

# Pr(foriennditis|dunnetts)
f3 = to_structured_array(np.array([['absent',0,.99],
                                   ['absent',1,.01],
                                   ['mild',0,.3],
                                   ['mild',1,.8],
                                   ['severe',0,.7],
                                   ['severe',1,.3]]),
                         'dunnetts,degar,val')

# Pr(foriennditis|dunnetts)
f4 = to_structured_array(np.array([['absent',0,0,.99],
                                   ['absent',0,1,.01],
                                   ['absent',1,0,.999],
                                   ['absent',1,1,.001],
                                   ['mild',0,0,.5],
                                   ['mild',0,1,.5],
                                   ['mild',1,0,.95],
                                   ['mild',1,1,.05],
                                   ['severe',0,0,.5],
                                   ['severe',0,1,.5],
                                   ['severe',1,0,.95],
                                   ['severe',1,1,.05]]),
                         'dunnetts,trimono,sloepnea,val')


# Pr(Fraud|Trav)
f5 = to_structured_array(np.array([[1,0,.99], [1,1,.01], [0,1,.004], [0,0,.996]]), 'Trav,Fraud,val')

# Pr(Fraud|Trav)
f6 = to_structured_array(np.array([[1,0,.99], [1,1,.01], [0,1,.004], [0,0,.996]]), 'Trav,Fraud,val')

if __name__ == '__main__':
    main()
