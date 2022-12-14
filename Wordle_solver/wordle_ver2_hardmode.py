import math
import json
import numpy as np

#open files to get data        
with open(r'C:\Users\Admin\wordle-project\Wordle_solver\possible_answers.txt','r') as f:
    POSSIBLE_ANSWERS=list()
    for line in f:
        line=line.rstrip()
        POSSIBLE_ANSWERS.append(line)
        
with open(r'C:\Users\Admin\wordle-project\Wordle_solver\word_freq.txt','r') as f:
    data=f.read()
    WORD_FREQ=json.loads(data)

ALLOWED_WORDS=WORD_FREQ.keys()

#some math functions that we need to use 
def log2(x):
    if x>0:
        return math.log2(x)
    else:
        return 0

def sigmoid(x):
    return 1/(1+math.exp(-x))

def get_frequency(words_freq, n_common=3000, width_under_sigmoid=10):
    x_width = width_under_sigmoid
    c = x_width * (-0.5 + n_common/len(words_freq))
    xs = np.linspace(c - x_width/2, c + x_width/2, len(words_freq))
    words_freq = {k:v for k,v in sorted(words_freq.items(), key=lambda x:x[1])}
    priors=dict()
    for (word,j) in zip(words_freq.keys(),xs):
        priors[word]=sigmoid(j)
    return priors

def get_common_word_probability(space):
    freq_map=get_frequency(WORD_FREQ)
    dt = {k:freq_map[k] for k in space}
    dt = {k:v/sum(dt.values()) for k,v in dt.items()}
    return dt

def convert_ternary(t):
    return sum([t[i]*3**(4-i) for i in range(5)])

def get_feedback(guess,answer):
    """
    

    Parameters
    ----------
    guess : str
        Five-letter guess.
    answer : str
        Five-letter correct answer.

    Returns
    -------
    feedback : list
        Contains 05 elements, which can be 0, 1, or 2, denoting a feedback pattern.

    """
    #convert string to list
    temp = list(answer)
    answer = temp
    temp = list(guess)
    guess = temp
    
    #initialize
    feedback = ['']*5
    
    #isolate correctly placed letters
    for i in range(5):
        if guess[i] == answer[i]:
            feedback[i] = 2
            answer[i] = ''
            guess[i] = ''
    
    #isolate wrongly placed letters
    for i in range(5):
        if guess[i] == '': continue
        elif guess[i] in answer:
            feedback[i] = 1
            answer[answer.index(guess[i])] = ''
            guess[i] = ''
        else:
            feedback[i] = 0
    
    return feedback

def pattern_probability_distribution(allowed_words,guess):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains allowed guesses.
    guess : str
        Five-letter guess.

    Returns
    -------
    pd : dict
        Contains the base 10 representation of a feedback pattern as the key.
        Corresponding value is its probability of appearing in the guess space.

    """

    frequency=get_frequency(WORD_FREQ)
    pd = dict()
    for word in allowed_words:
        feedback = get_feedback(guess,word)
        feedback_enumerated = convert_ternary(feedback)
        pd[feedback_enumerated] = pd.get(feedback_enumerated,0) + frequency[word]
    pd = {k:v/sum(pd.values()) for k,v in pd.items()}
    return pd

def entropy(word,allowed_words):
    distribution = pattern_probability_distribution(allowed_words,word)
    res=0
    for i in distribution.values():
        res+= -i*log2(i)
    return float(round(res,2))

def entropy_of_space(space,word_freq=WORD_FREQ):
    freq=get_frequency(word_freq)
    distribution = {k:freq[k] for k in space}
    dt = {k:v/sum(distribution.values()) for k,v in distribution.items()}
    res=0
    for i in dt.values():
        res += -i*log2(i)
    return float(round(res,2))

def entropy_ranker(allowed_words):
    res=dict()
    for word in allowed_words:
        res[word]=entropy(word,allowed_words)
    res={k:v for k,v in sorted(res.items(),key=lambda x:x[1],reverse=True)}
    return res

def reduce_allowed_words(allowed_words,guess,real_feedback):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains allowed guesses.
    guess : str
        Five-letter guess.
    real_feedback : list
        Contains 05 elements, which can be 0, 1, or 2, denoting a feedback pattern.

    Returns
    -------
    updated_allowed_words : list
        Updates allowed_words by retaining only words fitting the actual feedback.

    """
    real_feedback_enumerated = convert_ternary(real_feedback)
    updated_allowed_words = list()
    for word in allowed_words:
        feedback_enumerated = convert_ternary(get_feedback(guess,word))
        if feedback_enumerated == real_feedback_enumerated:
            updated_allowed_words.append(word)
    
    return updated_allowed_words

def display_ranker(allowed_words):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains allowed guesses.

    Returns
    -------
    None.
    Prints the ranker.

    """
    ranker = tuple(entropy_ranker(allowed_words).items())
    print('{0:<10}{1:<10}'.format('Word','Expected entropy'))
    for (word,entropy) in ranker[:10]: #print only top ten words with highest entropy
        print('{0:<10}{1:<10.2f}'.format(word,entropy))

def compute_actual_entropy(allowed_words,guess,real_feedback):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains allowed guesses.
    guess : str
        Five-letter guess.
    real_feedback : list
        Contains 05 elements, which can be 0, 1, or 2, denoting a feedback pattern.

    Returns
    -------
    updated_allowed_words : list
        Updates allowed_words by retaining only words fitting the actual feedback.

    """
    pd = pattern_probability_distribution(allowed_words,guess)
    p = pd[convert_ternary(real_feedback)]
    return float(round(log2(1/p),2))

def check_win(feedback):
    """
    

    Parameters
    ----------
    feedback : list
        Contains 05 elements, which can be 0, 1, or 2.

    Returns
    -------
    win : bool
        Becomes True when feedback is a list of 05 2's.

    """
    win = True
    for i in range(5):
        if feedback[i] != 2: 
            win = False
            break
    return win


#Upgraded version using score function
INITIAL=entropy_of_space(ALLOWED_WORDS)

def collect_data_of_a_game(allowed_words,answer):
    history=list()
    win=False
    valid_words=allowed_words
    i=0
    guess_count=0
    while not win:
        if i==0:
            guess='tares'
            history.append(['tares',INITIAL])
        else:
            ranker = entropy_ranker(valid_words)
            guess = list(ranker.keys())[0]
            history.append([guess,entropy_of_space(valid_words)])
        guess_count+=1
        real_fb=get_feedback(guess,answer)
        if check_win(real_fb)==True:
            break
        valid_words=reduce_allowed_words(valid_words,guess,real_fb)
        i+=1
    return history

def collect_data(allowed_words,possible_words):
    res=list()
    for answer in possible_words:
        res.append(collect_data_of_a_game(allowed_words,answer))
    return res

# collect data code 
#with open(r'C:\Users\Admin\wordle-project\Wordle_solver\data.txt','a') as f:
    for game in collect_data(ALLOWED_WORDS,POSSIBLE_ANSWERS[401:]):
        f.write(str(game)+'\n')

def f(x):
    (w,b)=(0.2458,1.4614)
    return w*x+b

def score(allowed_words,guess,word,actual_fb,num_of_guesses):
    H0 = entropy_of_space(allowed_words)
    H1 = compute_actual_entropy(allowed_words,guess,actual_fb)
    dt = get_common_word_probability(reduce_allowed_words(allowed_words,guess,actual_fb))
    p = dt[word]
    return p*num_of_guesses + (1-p)*(num_of_guesses + f(H0-H1))

def score_ranker(allowed_words,actual_fb,guess,num_of_guesses):
    space=reduce_allowed_words(allowed_words,guess,actual_fb)
    res=dict()
    for word in space:
        res[word]=score(space,guess,word,actual_fb,num_of_guesses)
    res = {k:v for k,v in sorted(res.items(),key=lambda x:x[1])}
    return res

def wordlebot_score_play(allowed_words,answer):
    valid_words=allowed_words
    win=False
    i=guess_count=0
    while not win:
        if i==0:
            guess='tares'
            guess_count+=1
        else:
            fb = get_feedback(guess,answer)
            ranker=score_ranker(valid_words,fb,guess, guess_count+1)
            guess=list(ranker.keys())[0]
            guess_count+=1
        real_fb=get_feedback(guess,answer)
        if check_win(real_fb)==True:
            break
        valid_words=reduce_allowed_words(valid_words,guess,real_fb)
        i+=1
    return guess_count

def display_score_ranker(allowed_words,actual_fb,guess,num_of_guesses):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains allowed guesses.

    Returns
    -------
    None.
    Prints the ranker.

    """
    ranker = tuple(score_ranker(allowed_words,actual_fb,guess,num_of_guesses).items())
    print('{0:<10}{1:<10}'.format('Word','Expected score'))
    for (word,score) in ranker[:10]: #print only top ten words with highest entropy
        print('{0:<10}{1}'.format(word,score))

def wordlebot_byscore_interface(allowed_words):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains allowed guesses.

    Returns
    -------
    None.
    Prints the interactive program for user to play Wordle and input real feedback.

    """
    win = False
    valid_words = allowed_words
    i = 0
    
    while not win:
        print("Guess #" + str(i+1))
        guess = input('> Enter your guess: ')
        real_feedback = list(map(int,input('>> Enter the feedback: ').split(' ')))
        
        if check_win(real_feedback) == True:
            print(">>> Complete!")
            break
        
        print(">>> Expected entropy: " + str(entropy(guess,valid_words)))
        print("    Actual entropy: " + str(compute_actual_entropy(valid_words,guess,real_feedback)))
        valid_words = reduce_allowed_words(valid_words,guess,real_feedback)
        display_score_ranker(valid_words,real_feedback,guess,i+1)
        print(">>>> Remaining possibilities: " + str(len(valid_words)) + "\n")
        
        i += 1

def TestModel(solution,allowed_words,test_list:list,RANDOM=False) -> tuple:
    '''
    Parameter
    ----------
    solution: The function return the number of step to guess a specific answer \n
    test_list: The list of answers for testing
    RANDOM: False, answer is chosen randomly and True, answer is chosen sequentially from the test_list
    ----------
    Return: The bar chart with x(number of guesses needed) and y (number of plays having x guesses) \n
                  The tupple of winrate and average score'''
    import random
    import time
    t1=time.time()
    #Compute some vital factor: number of plays having x guesses, win rate, average score of 2,3k plays   
    xMax=20 # may be posituve infinity number
    yMax=0
    lst=[0]*xMax
    N=len(test_list)# list contains number of plays having x guesses
    for word in test_list:
        if not RANDOM:
            answer=word
        elif RANDOM:
            answer=random.choice(test_list)
        NumberOfGuessesNeeded=solution(allowed_words, answer) 
        lst[NumberOfGuessesNeeded]=lst[NumberOfGuessesNeeded]+1
    winrate=sum(lst[1:7])/N*100
    average=sum([i*lst[i] for i in range(1,xMax)]) / N

    #VISUALIZATION
    import matplotlib.pyplot as plt
    for i in range(1,xMax):
        if lst[i] >=yMax: # because yMax always in (1,6)
            yMax=lst[i]
        if lst[i]==0 and i>6:
            xMax=i
            break
    yMax=(yMax//100+2)*100
    x=[str(i) for i in range(1,xMax)]
    y=[i for i in lst[1:xMax]]
    plt.ylim(0,yMax)
    plt.grid(axis='y',linestyle='--')
    plt.xlabel('Number of guesses needed')
    plt.ylabel('Number of plays having x guesses')
    plt.title('TEST PERFORMANCE')
    plt.bar(x,y, fc="#CCD6A6", ec="black")
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha="center", va="bottom")
    t2=time.time()
    time=t2-t1
    plt.text(xMax,yMax/2, f'Win Rate: {winrate:.3f}%\nAverage Score: {average:.3f}\nTime: {time:.3f}s', fontsize = 20,
		bbox = dict(facecolor = '#CCD6A6', alpha = 0.7))
    plt.show()
    return winrate,average

#TestModel(wordlebot_score_play,ALLOWED_WORDS,POSSIBLE_ANSWERS)
       
