import random
import numpy as np
import sys
usepytwo=False
if sys.version_info[0] < 3:
    usepytwo=True


#these are the probability that a car is behind door 1, 2 or 3
#for the symmetric case discussed in Question 2(b)
#door_probs=[0.3333,0.3333,0.3334]
#for the skewed case in Question 2(c)
door_probs=[0.8,0.1,0.1]

#choose an initial door for the car
actual_cd=1+list(np.random.multinomial(1,door_probs)).index(1)

## the simulator function.
## inputs (tuple s and integer a)
##      * state s is a tuple giving the previous door picked by the player (pd) and the hosts choice (hc). Each can take on values 0-3, where 0 denotes no choice has been made (start of a game) and 1-3 denote which door has been chosen.
##      * action a is the action by the player - this must be 1,2, or 3 and denotes which door is chosen
## output (tuple with first element being a tuple sp and second being a reward value)
##      * state sp is a tuple (pdp,hcp) giving the updated state after the action a is taken in state (pd,hc)
##      * reward gathered r by taking a in state (pd,hc) and ending up in (pdp,hcp)
def simulator(s,a):
    # use the global car door variable (this is hidden to the player who sees the simulator as a black box)
    global actual_cd
    pd=s[0]
    hc=s[1]
    
    #new value of picked door based on action
    if pd==0: 
        pdp=a
    else:      #resets every second round
        pdp=0


    #choose a door for the host - based on the actual car door in this game
    if hc==0:
        # the possible choices are a door in 1,2 or 3
        rem_cardoors=[1,2,3]
        # with the actual car door removed,
        rem_cardoors.remove(actual_cd)
        # and the choice of the player removed.
        if a in rem_cardoors:
            rem_cardoors.remove(a)
        # a random choice in the remaining set (which may be a single door)
        hcp=rem_cardoors[random.randint(0,len(rem_cardoors)-1)]
    else:     #resets every second round
        hcp=0

    #reward gathered after the final choice (when hc is non-zero)
    if hc==0 or not a==actual_cd:
        r=0
    else:
        r=1

    #reset actual car door in the second round in preparation for the next game
    if not hc==0:
        actual_cd=1+list(np.random.multinomial(1,door_probs)).index(1)
    #return new state and reward
    return ((pdp,hcp),r)


## a simple test program to show how this works
if __name__ == "__main__":

    #default initial state- must be (0,0)
    s=(0,0)
    a=1
    sumr=0
    while a>0:
        if s[1]==0:
            print("its your first choice of door")
        else:
            print("its your second choice of door. your first choice was "+str(s[0])+" and the host chose door "+str(s[1]))
        ##print("the current state is pd: "+str(s[0])+" hd: "+str(s[1]))
        ### HERE YOU CAN GET YOUR BEST ACTION ACCORDING TO YOUR Q FUNCTION IF YOU LIKE 
        #### print("Q learning advises choice: "+str(my_qlearning_best_next_action))
            
        sa="-1"
        while sa=="-1":
            if usepytwo:
                sa=raw_input("choose door (1,2,3 or 0 to quit):")
            else:
                sa=input("choose door (1,2,3 or 0 to quit):")
            if not (sa=="0" or sa=="1" or sa=="2" or sa=="3"):
                sa="-1"
        a=int(sa)
        if not a==0:
            (sp,r)=simulator(s,a)
            sumr = sumr+r
            if (sp[1]==0):
                if r==0:
                    print("****************** You won a goat :( oh well better luck next time")
                else:
                    print("****************** You won the car!!!!!!! Congratulations!!!")
                print("total number of cars won so far: "+str(sumr))
            ##print("the new state is pd: "+str(sp[0])+" hd: "+str(sp[1])+" and reward achieved was: "+str(r))
        s=sp
    
