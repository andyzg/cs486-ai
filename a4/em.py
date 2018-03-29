from bn import *
import json
import random

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

DEBUG = True


def rand(delta):
    return random.random() * delta

def debug(*args):
    if DEBUG:
        print(*args)


class Case:

    def __init__(self, sloe, fori, dega, trimo, dunn):
        self.sloepnea = sloe
        self.foriennditis = fori
        self.degar_spots = dega
        self.trimono = trimo
        self.dunn = dunn

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
        return self.dunn


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
                            val.pop(node)
                            factorList = [f0.copy(), f1.copy(), f2.copy(),
                                    f3.copy(), f4.copy()]
                            table = inference(factorList, node, [], val)
                            # print(table)
                            # for col in val:
                            #     table = restrict(table, col, val[col])
                            if node == 'foriennditis':
                                temp[node] = table[f]
                            elif node == 'dunnetts':
                                temp[node] = table[dunn]
                            elif node == 'sloepnea':
                                temp[node] = table[s]
                            elif node == 'degar':
                                temp[node] = table[d]
                            elif node == 'trimono':
                                temp[node] = table[t]
                            # temp[node] = table[0][0]
                            # print(temp[node][1])
                            total *= temp[node][1]
                        temp['val'] = total
                        if temp['val'] < 0:
                            print('WTF', temp['val'], f, d, s, t, dunn)
                        # print(f0.copy(), f1.copy(), f2.copy(), f3.copy(), f4.copy())
                        v[f][d][s][t][dunn] = temp
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
                count += 1
            elif prob[2] >= prob[0] and prob[2] >= prob[1]:
                count2 += 1
            else:
                pass
            s += total
        else:
            for val in o:
                prob[val] = 0
            for val in o:
                prob[d.dunnetts] += o[val]['val']
            s += prob[d.dunnetts]
        outcomes.append(prob)
    # debug('ABSENT: ', len(data) - count - count2, ' / ', len(data))
    # debug('MILD: ', count, ' / ', len(data))
    # debug('SEVERE: ', count2, ' / ', len(data))

    return s, outcomes


def maximization(data, outcomes, delta):
    length = len(outcomes) * 1.0
    total = len(outcomes) * 1.0
    # total = 0

    absent = 0.0
    mild = 0.0
    severe = 0.0
    # Set up Dunnetts table
    for row in outcomes:
        absent += row.get(0, 0)
        mild += row.get(1, 0)
        severe += row.get(2, 0)
    total = (absent + mild + severe)

    absent *= length / total
    mild *= length / total
    severe *= length / total

    absent += rand(delta)
    mild += rand(delta)
    severe += rand(delta)
    # dunn_total = absent + mild + severe
    dunn_total = length


    cpts['dunnetts']['val'][0] = absent / dunn_total
    cpts['dunnetts']['val'][1] = mild / dunn_total
    cpts['dunnetts']['val'][2] = severe / dunn_total

    trimono = 0.0
    # Set up trimono table
    for i, row in enumerate(outcomes):
        if data[i].t == 1:
            trimono += 1.0 # (row.get(0, 0) + row.get(1, 0) + row.get(2, 0))
    trimono *= length / total
    t_s = 1 - trimono / length + rand(delta)
    t_t = rand(delta) + trimono / length

    cpts['trimono']['val'][0] = t_s / (t_t + t_s)
    cpts['trimono']['val'][1] = t_t / (t_t + t_s)

    absent = 0.0
    mild = 0.0
    severe = 0.0
    # Setup foriennditis table
    for i, row in enumerate(outcomes):
        if data[i].f == 1:
            absent += row.get(0, 0)
            mild += row.get(1, 0)
            severe += row.get(2, 0)

    absent *= length / total
    mild *= length / total
    severe *= length / total

    a_s = 1 - absent / length + rand(delta)
    a_a = absent / length + rand(delta)
    m_s = 1 - mild / length + rand(delta)
    m_a = mild / length + rand(delta)
    s_s = 1 - severe / length + rand(delta)
    s_a = severe / length + rand(delta)

    cpts['foriennditis']['val'][0] = a_s / (a_s + a_a)
    cpts['foriennditis']['val'][1] = a_a / (a_s + a_a)
    cpts['foriennditis']['val'][2] = m_s / (m_s + m_a)
    cpts['foriennditis']['val'][3] = m_a / (m_s + m_a)
    cpts['foriennditis']['val'][4] = s_s / (s_s + s_a)
    cpts['foriennditis']['val'][5] = s_a / (s_s + s_a)

    absent = 0.0
    mild = 0.0
    severe = 0.0
    # Setup degar table
    for i, row in enumerate(outcomes):
        if data[i].d == 1:
            absent += row.get(0, 0)
            mild += row.get(1, 0)
            severe += row.get(2, 0)

    absent *= length / total
    mild *= length / total
    severe *= length / total

    a_s = 1 - absent / length + rand(delta)
    a_a = absent / length + rand(delta)
    m_s = 1 - mild / length + rand(delta)
    m_a = mild / length + rand(delta)
    s_s = 1 - severe / length + rand(delta)
    s_a = severe / length + rand(delta)
    cpts['degar']['val'][0] = a_s / (a_s + a_a)
    cpts['degar']['val'][1] = a_a / (a_s + a_a)
    cpts['degar']['val'][2] = m_s / (m_s + m_a)
    cpts['degar']['val'][3] = m_a / (m_s + m_a)
    cpts['degar']['val'][4] = s_s / (s_s + s_a)
    cpts['degar']['val'][5] = s_a / (s_s + s_a)

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
        total += (row.get(0, 0) + row.get(1, 0) + row.get(2, 0))

    absent_0 *= length / total
    mild_0 *= length / total
    severe_0 *= length / total

    absent_0 *= length / total
    mild_0 *= length / total
    severe_0 *= length / total
    print(severe_0, total)

    a_s0 = 1 - absent_0 / length + rand(delta)
    a_a0 = absent_0 / length + rand(delta)
    m_s0 = 1 - mild_0 / length + rand(delta)
    m_a0 = mild_0 / length + rand(delta)
    s_s0 = 1 - severe_0 / length + rand(delta)
    s_a0 = severe_0 / length + rand(delta)

    a_s1 = 1 - absent_1 / length + rand(delta)
    a_a1 = absent_1 / length + rand(delta)
    m_s1 = 1 - mild_1 / length + rand(delta)
    m_a1 = mild_1 / length + rand(delta)
    s_s1 = 1 - severe_1 / length + rand(delta)
    s_a1 = severe_1 / length + rand(delta)

    print('OMG', s_s0, s_a0, severe_0, length)
    cpts['sloepnea']['val'][0] = a_s0 / (a_s0 + a_a0)
    cpts['sloepnea']['val'][1] = a_a0 / (a_s0 + a_a0)
    cpts['sloepnea']['val'][2] = a_s1 / (a_s1 + a_a1)
    cpts['sloepnea']['val'][3] = a_a1 / (a_s1 + a_a1)
    cpts['sloepnea']['val'][4] = m_s0 / (m_s0 + m_a0)
    cpts['sloepnea']['val'][5] = m_a0 / (m_s0 + m_a0)
    cpts['sloepnea']['val'][6] = m_s1 / (m_s1 + m_a1)
    cpts['sloepnea']['val'][7] = m_a1 / (m_s1 + m_a1)
    cpts['sloepnea']['val'][8] = s_s0 / (s_s0 + s_a0)
    cpts['sloepnea']['val'][9] = s_a0 / (s_s0 + s_a0)
    cpts['sloepnea']['val'][10] = s_s1 / (s_s1 + s_a1)
    cpts['sloepnea']['val'][11] = s_a1 / (s_s1 + s_a1)
    print(cpts)


def calc(delta):
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
        maximization(data, outcomes, delta)
        if abs(next_s - s) < 0.1:
            break
        s = next_s
        print(s)
        print('')
        # print(cpts['dunnetts']['val'])
        # print(cpts['trimono']['val'])
        # print(cpts['foriennditis']['val'])
        # print(cpts['degar']['val'])
        # print(cpts['sloepnea']['val'])


def test(o, delta):
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
            # print 'Correct', d.f, d.d, d.s, d.t, maximum
            correct += 1
        else:
            # debug('Incorrect', d.f, d.d, d.s, d.t, maximum, ' | actual: ', d.dunnetts)
            pass
    debug(correct, '/', len(data))
    return correct
    # debug(json.dumps(pt[0][0][1][0], indent=4, sort_keys=True))


def main():
    # o = calc(0)
    # success = test(o, 0)
    # print(success)
    # return
    results = {}
    for i in range(0, 20):
        results[i] = []
        for j in range(0, 5):
            cpts = {
                'dunnetts': f0.copy(),
                'trimono': f1.copy(),
                'foriennditis': f2.copy(),
                'degar': f3.copy(),
                'sloepnea': f4.copy()
            }
            delta = 4.0 / 20 * i
            debug('Delta:', delta)
            o = calc(delta)
            success = test(o, delta)
            results[i].append(success)
            print('')
    with open('results.txt', 'w') as f:
        f.write(json.dumps(results, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
    # debug(prob_tree())
