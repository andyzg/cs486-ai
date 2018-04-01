from AwesomeBot import AwesomeBot
from AndyDufresne import AndyDufresne

pd_agent = AwesomeBot()
me = AndyDufresne()

done = False

my_scores = []
pd_scores = []

for i in range(0, 10):
    iteration = 1
    agent_score = 0
    client_score = 0
    pd_agent.init()
    me.init()

    for j in range(0, 15):
        agent_action = pd_agent.get_play()
        my_action = me.get_play()

        pd_agent.make_play(my_action)
        me.make_play(agent_action)
        print 'Actions: agent', agent_action, ', I', my_action

        if my_action == "give 2":
            agent_score += 2
        elif my_action == "take 1":
            client_score += 1

        if agent_action == "give 2":
            client_score += 2
        elif agent_action == "take 1":
            agent_score += 1

    print "your score:    ",client_score," -:",client_score*"*"
    print "pd-bots score: ",agent_score," -:",agent_score*"*"
    my_scores.append(client_score)
    pd_scores.append(agent_score)

print 'My mean score: ', sum(my_scores) * 1.0 / len(my_scores)
print 'PD mean score: ', sum(pd_scores) * 1.0 / len(pd_scores)
