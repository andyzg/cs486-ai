from bn import *
import json

NOT_RECORDED = -1
NOT_PRESENT = 0
MILD = 1
SEVERE = 2

# Pr(Dunnetts)
f0 = to_structured_array(np.array([[0,.5],
                                  [1,.25],
                                  [2,.25]]), 'dunnetts,val')

# Pr(Trimono)
f1 = to_structured_array(np.array([[0,.9], [1,.1]]), 'trimono,val')

# Pr(foriennditis|dunnetts)
f2 = to_structured_array(np.array([[0,0,.99],
                                   [0,1,.01],
                                   [1,0,.1],
                                   [1,1,.9],
                                   [2,0,.7],
                                   [2,1,.3]]),
                         'dunnetts,foriennditis,val')

# Pr(foriennditis|dunnetts)
f3 = to_structured_array(np.array([[0,0,.99],
                                   [0,1,.01],
                                   [1,0,.7],
                                   [1,1,.3],
                                   [2,0,.1],
                                   [2,1,.9]]),
                         'dunnetts,degar,val')

# Pr(sloepnea|dunnetts, trimono)
f4 = to_structured_array(np.array([[0,0,0,.99],
                                   [0,0,1,.01],
                                   [0,1,0,.999],
                                   [0,1,1,.001],
                                   [1,0,0,.2],
                                   [1,0,1,.8],
                                   [1,1,0,.95],
                                   [1,1,1,.05],
                                   [2,0,0,.2],
                                   [2,0,1,.8],
                                   [2,1,0,.95],
                                   [2,1,1,.05]]),
                         'dunnetts,trimono,sloepnea,val')


cpts = {
    'dunnetts': f0,
    'trimono': f1,
    'foriennditis': f2,
    'degar': f3,
    'sloepnea': f4
}

values = {
    'foriennditis': [0, 1],
    'degar': [0, 1],
    'sloepnea': [0, 1],
    'trimono': [0, 1],
    'dunnetts': [0, 1, 2]
}


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


class Parameter:

    def __init__(self, p, given):
        self.p = p
        self.given = given
        self.prob = 1

    def set_prob(self, prob):
        self.prob = prob


def load_data(filename):
    data = []
    with open(filename, 'r') as f:
        for l in f.readlines():
            sloe, fori, dega, trimo, dunn = map(int, l.strip().split(' '))
            case = Case(sloe, fori, dega, trimo, dunn)
            data.append(case)

    return data


def update_parameters(cpts, parameters):
    parameters[0].set_prob(cpts['dunnetts']['val'][1])
    parameters[1].set_prob(cpts['dunnetts']['val'][2])
    parameters[2].set_prob(cpts['trimono']['val'][0])
    parameters[3].set_prob(cpts['foriennditis']['val'][1])
    parameters[4].set_prob(cpts['foriennditis']['val'][3])
    parameters[5].set_prob(cpts['foriennditis']['val'][5])
    parameters[6].set_prob(cpts['degar']['val'][1])
    parameters[7].set_prob(cpts['degar']['val'][3])
    parameters[8].set_prob(cpts['degar']['val'][5])
    parameters[9].set_prob(cpts['sloepnea']['val'][1])
    parameters[10].set_prob(cpts['sloepnea']['val'][3])
    parameters[11].set_prob(cpts['sloepnea']['val'][5])
    parameters[12].set_prob(cpts['sloepnea']['val'][7])
    parameters[13].set_prob(cpts['sloepnea']['val'][9])
    parameters[14].set_prob(cpts['sloepnea']['val'][11])


def prob_tree():
    v = {}
    # tables = [f0, f1, f2, f3, f4]
    # Create a tree of all the values
    for f in values['foriennditis']:
        v[f] = {}
        for d in values['degar']:
            v[f][d] = {}
            for s in values['sloepnea']:
                v[f][d][s] = {}
                for t in values['trimono']:
                    v[f][d][s][t] = {}
                    for dunn in values['dunnetts']:
                        temp = {}
                        total = 1
                        for node in cpts:
                            table = cpts[node]
                            val = {
                                'foriennditis': f,
                                'degar': d,
                                'sloepnea': s,
                                'trimono': t,
                                'dunnetts': dunn
                            }
                            for col in val:
                                table = restrict(table, col, val[col])
                            temp[node] = table[0][0]
                            total *= temp[node]
                        temp['val'] = total
                        v[f][d][s][t][dunn] = temp
                    # print 'val', v[f][d][s][t][0]['val'],v[f][d][s][t][1]['val'],v[f][d][s][t][1]['val']
    return v


def expectation(cpts, parameters, data):
    v = prob_tree()

    # Now that we have the non normalized probability at each node, we calculate
    # the probability for each piece of data
    outcomes = []
    s = 0.0
    count = 0
    count2 = 0
    for d in data:
        o = v[d.f][d.d][d.s][d.t]
        prob = {}
        total = 0.0
        if d.dunnetts == -1:
            for val in o:
                prob[val] = o[val]['val']
                total += prob[val]
            # print prob[0], prob[1], prob[2]
            if prob[1] >= prob[0] and prob[1] >= prob[2]:
                print 'Mild', d.f, d.d, d.s, d.t
                count += 1
            elif prob[2] >= prob[0] and prob[2] >= prob[1]:
                print 'Severe', d.f, d.d, d.s, d.t
                count2 += 1
            else:
                print 'Absent', d.f, d.d, d.s, d.t
            s += total
            for val in o:
                prob[val] /= total
        else:
            for val in o:
                prob[val] = 0
            s += o[d.dunnetts]['val']
            prob[d.dunnetts] = 1
        # print prob
        outcomes.append(prob)
    print 'ABSENT: ', len(data) - count - count2, ' / ', len(data)
    print 'MILD: ', count, ' / ', len(data)
    print 'SEVERE: ', count2, ' / ', len(data)

    return s, outcomes


def maximization(data, outcomes):
    total = len(outcomes) * 1.0

    absent = 0.0
    mild = 0.0
    severe = 0.0
    # Set up Dunnetts table
    for row in outcomes:
        absent += row.get(0, 0)
        mild += row.get(1, 0)
        severe += row.get(2, 0)
    print absent, mild, severe
    cpts['dunnetts']['val'][0] = absent / total
    cpts['dunnetts']['val'][1] = mild / total
    cpts['dunnetts']['val'][2] = severe / total

    trimono = 0.0
    # Set up trimono table
    for d in data:
        if d.t == 1:
            trimono += 1.0
    cpts['trimono']['val'][0] = 1 - trimono / total
    cpts['trimono']['val'][1] = trimono / total

    absent = 0.0
    mild = 0.0
    severe = 0.0
    # Setup foriennditis table
    for i, row in enumerate(outcomes):
        if data[i].f == 1:
            absent += row.get(0, 0)
            mild += row.get(1, 0)
            severe += row.get(2, 0)
    cpts['foriennditis']['val'][0] = 1 - absent / total
    cpts['foriennditis']['val'][1] = absent / total
    cpts['foriennditis']['val'][2] = 1 - mild / total
    cpts['foriennditis']['val'][3] = mild / total
    cpts['foriennditis']['val'][4] = 1 - severe / total
    cpts['foriennditis']['val'][5] = severe / total

    absent = 0.0
    mild = 0.0
    severe = 0.0
    # Setup degar table
    for i, row in enumerate(outcomes):
        if data[i].d == 1:
            absent += row.get(0, 0)
            mild += row.get(1, 0)
            severe += row.get(2, 0)
    cpts['degar']['val'][0] = 1 - absent / total
    cpts['degar']['val'][1] = absent / total
    cpts['degar']['val'][2] = 1 - mild / total
    cpts['degar']['val'][3] = mild / total
    cpts['degar']['val'][4] = 1 - severe / total
    cpts['degar']['val'][5] = severe / total

    absent_0 = 0.0
    mild_0 = 0.0
    severe_0 = 0.0
    absent_1 = 0.0
    mild_1 = 0.0
    severe_1 = 0.0
    # Setup degar table
    for i, row in enumerate(outcomes):
        if data[i].s == 1:
            if data[i].t == 1:
                absent_1 += row.get(0, 0)
                mild_1 += row.get(1, 0)
                severe_1 += row.get(2, 0)
            else:
                absent_0 += row.get(0, 0)
                mild_0 += row.get(1, 0)
                severe_0 += row.get(2, 0)

    cpts['sloepnea']['val'][0] = 1 - absent_0 / total
    cpts['sloepnea']['val'][1] = absent_0 / total
    cpts['sloepnea']['val'][2] = 1 - absent_1 / total
    cpts['sloepnea']['val'][3] = absent_1 / total
    cpts['sloepnea']['val'][4] = 1 - mild_0 / total
    cpts['sloepnea']['val'][5] = mild_0 / total
    cpts['sloepnea']['val'][6] = 1 - mild_1 / total
    cpts['sloepnea']['val'][7] = mild_1 / total
    cpts['sloepnea']['val'][8] = 1 - severe_0 / total
    cpts['sloepnea']['val'][9] = severe_0 / total
    cpts['sloepnea']['val'][10] = 1 - severe_1 / total
    cpts['sloepnea']['val'][11] = severe_1 / total


def main():
    data = load_data('traindata.txt')
    parameters = [
        Parameter({'dunnetts': 1}, {}),
        Parameter({'dunnetts': 2}, {}),
        Parameter({'trimono': 1}, {}),
        Parameter({'foriennditis': 1}, {'dunnetts': 0}),
        Parameter({'foriennditis': 1}, {'dunnetts': 1}),
        Parameter({'foriennditis': 1}, {'dunnetts': 2}),
        Parameter({'degar': 1}, {'dunnetts': 0}),
        Parameter({'degar': 1}, {'dunnetts': 1}),
        Parameter({'degar': 1}, {'dunnetts': 2}),
        Parameter({'sloepnea': 1}, {'dunnetts': 0, 'trimono': 0}),
        Parameter({'sloepnea': 1}, {'dunnetts': 1, 'trimono': 0}),
        Parameter({'sloepnea': 1}, {'dunnetts': 2, 'trimono': 0}),
        Parameter({'sloepnea': 1}, {'dunnetts': 0, 'trimono': 1}),
        Parameter({'sloepnea': 1}, {'dunnetts': 1, 'trimono': 1}),
        Parameter({'sloepnea': 1}, {'dunnetts': 2, 'trimono': 1}),
    ]

    s = 9999999
    while True:
        update_parameters(cpts, parameters)
        next_s, outcomes = expectation(cpts, parameters, data)
        print next_s
        print cpts['dunnetts']['val']
        maximization(data, outcomes)
        if abs(next_s - s) < 0.1:
            break
        s = next_s


def test(o):
    pt = prob_tree()
    data = load_data('testdata.txt')
    correct = 0
    for d in data:
        prob = pt[d.f][d.d][d.s][d.t]
        maximum = -1
        val = 0
        for i in prob:
            if prob[i]['val'] > val:
                maximum = i
                val = prob[i]['val']
        if maximum == d.dunnetts:
            correct += 1
    print correct, '/', len(data)
    print json.dumps(pt[1][1][1][0], indent=4, sort_keys=True)


if __name__ == '__main__':
    o = main()
    test(o)
