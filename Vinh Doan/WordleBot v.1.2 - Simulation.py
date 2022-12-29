# %% [markdown]
# <h1 style="font-size:3rem;color:orange;">WordleBot v.1.2 - Normal mode - Gameplay simulation</h1>

# %% [markdown]
# #### > Log Nov 24, 10.30 a.m. : In this version, we change the code for it to play on Normal Mode. The main difference lies in the fact that though entropy is still computed based on the reduced guess space, it is computed for all allowed words (~13000)
# 
# ##### >> Changed argument "allowed_words" in (1) pattern_probability_distribution(allowed_words, guess), (2) compute_entropy(allowed_words, guess), (3) compute_actual_entropy(allowed_words,guess, real_feedback), (4) reduce_allowed_words(allowed_words,guess,real_feedback), (5) get_ranker(allowed_words), (6) display_ranker(allowed_words) into "still_valid_words" to indicate the list of words still possible as an answer. "allowed_words" is now exclusively used to indicate the list of ~13000 allowed guesses
# 
# ##### >> get_ranker, display_ranker: Modified to take both "still_valid_words" and "allowed_words" as arguments (previously these functions only take the list of words still possible as an answer as an argument)
# 
# ##### >> wordlebot_interface: Added minor changes so that expected entropy and actual entropy still get printed out for the final guess.
# 
# ##### >> wordlebot_interface: After the aforementioned changes, suggestions about new guesses definitely change, compared with WordleBot v.1.1, a minor problem is that with the ranker showing all ~13000 words and their entropies, user cannot see the actual still_valid_words
# 
# ##### >> wordlebot_interface: Added minor changes to tackle previous issue. The interface will print out the answer when there is only one word left in still_valid_words. This is also the only situation when the previous issue can be a nuisance
# 
# ##### >> wordlebot_play: Changed so that for the final guess (when len(still_valid_words) == 1), the ranker is not computed, and the guess is automatically the only possible answer left
# 
# #### > Log Nov 26, 0.30 a.m. : test_for_performance is modified so that while running, user gets update on the number of word parsed through, and each word's computation time. Also included the detailed distribution of guesses needed
# 
# #### > Log Nov 27, 0.30 a.m. : final test performance result : Average number of guesses needed: 4.113902122130793
# ##### Detailed distribution of number of guesses needed:
# ##### 2 guess(es): 4
# ##### 3 guess(es): 316
# ##### 4 guess(es): 1436
# ##### 5 guess(es): 519
# ##### 6 guess(es): 34

# %% [markdown]
# ## Preliminaries

# %%
import matplotlib.pyplot as plt
from math import log
import time
import csv

# %% [markdown]
# ## Mathematics

# %%
def logBase2(n,l = log(2)):
    """


    Parameters
    ----------
    n : int
        A number.

    Returns
    -------
    int
        Log base 2 of said number.

    """
    return log(n)/l

# %%
def convert_ternary(t):
    """


    Parameters
    ----------
    t : list
        Contains 05 elements, which can be 0, 1, or 2, denoting a feedback pattern.

    Returns
    -------
    int
        Base 10 representation of pattern.

    """
    return sum([t[i]*3**(4-i) for i in range(5)])

# %% [markdown]
# ## Game mechanics

# %%
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

# %% [markdown]
# ## Entropy computation

# %%
def pattern_probability_distribution(still_valid_words,guess):
    """
    

    Parameters
    ----------
    still_valid_words : list
        Contains words still possible as an answer.
    guess : str
        Five-letter guess.

    Returns
    -------
    pd : dict
        Contains the base 10 representation of a feedback pattern as the key.
        Corresponding value is its probability of appearing in the guess space.

    """
    total = len(still_valid_words)
    pd = dict()
    for word in still_valid_words:
        feedback = get_feedback(guess,word)
        feedback_enumerated = convert_ternary(feedback)
        pd[feedback_enumerated] = pd.get(feedback_enumerated,0) + 1/total
    return pd

# %%
def compute_entropy(still_valid_words,guess):
    """
    

    Parameters
    ----------
    still_valid_words : list
        Contains words still possible as an answer.
    guess : str
        Five-letter guess.

    Returns
    -------
    res : float
        Expected entropy value of a guess, computed based on 
        pattern_probability_distribution.

    """
    pd = pattern_probability_distribution(still_valid_words,guess)
    res = 0
    for p in pd.values():
        res += -p*logBase2(p)
    return round(res,2)

# %%
def compute_actual_entropy(still_valid_words,guess,real_feedback):
    """
    

    Parameters
    ----------
    still_valid_words : list
        Contains words still possible as an answer.
    guess : str
        Five-letter guess.
    real_feedback : list
        Contains 05 elements, which can be 0, 1, or 2, denoting a feedback pattern.

    Returns
    -------
    updated_allowed_words : list
        Updates allowed_words by retaining only words fitting the actual feedback.

    """
    pd = pattern_probability_distribution(still_valid_words,guess)
    p = pd[convert_ternary(real_feedback)]
    return round(-logBase2(p),2)

# %% [markdown]
# ## WordleBot mechanics

# %% [markdown]
# ### Reduce guess space

# %%
def reduce_allowed_words(still_valid_words,guess,real_feedback):
    """
    

    Parameters
    ----------
    still_valid_words : list
        Contains words still possible as an answer.
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
    for word in still_valid_words:
        feedback_enumerated = convert_ternary(get_feedback(guess,word))
        if feedback_enumerated == real_feedback_enumerated:
            updated_allowed_words.append(word)
    
    return updated_allowed_words

# %% [markdown]
# ### Entropy ranker

# %%
def get_ranker(still_valid_words,allowed_words):
    """
    

    Parameters
    ----------
    still_valid_words : list
        Contains words still possible as an answer.
    allowed_words: list
        Contains ~13000 allowed guesses.

    Returns
    -------
    ranker : list
        Contains ~13000 tuples, whose first element is a guess, and
        second element is the entropy of that guess.

    """
    ranker = list()
    for word in allowed_words:
        ranker.append((word,compute_entropy(still_valid_words,word)))
    ranker.sort(key = lambda t: t[1], reverse = True)
    
    return ranker

# %% [markdown]
# ### Interface

# %%
def display_ranker(still_valid_words,allowed_words,initial_ranker=None,simulation=False):
    """
    

    Parameters
    ----------
    still_valid_words : list
        Contains words still possible as an answer.
    allowed_words: list
        Contains ~13000 allowed guesses.

    Returns
    -------
    None.
    Prints the ranker.

    """
    if initial_ranker == None:
        ranker = get_ranker(still_valid_words,allowed_words)
    else:
        ranker = initial_ranker
    print('{0:<10}{1:<10}'.format('Word','Expected entropy'))
    for (word,entropy) in ranker[:10]: #print only top ten words with highest entropy
        print('{0:<10}{1:<10.2f}'.format(word,entropy))
    
    if simulation == True:
        return ranker

# %%
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

# %%
def wordlebot_interface(allowed_words):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains ~13000 allowed guesses.

    Returns
    -------
    None.
    Prints the interactive program for user to play Wordle and input real feedback.

    """
    win = False
    still_valid_words = allowed_words[:]
    i = 0
    while not win:
        print("Guess #" + str(i+1))
        
        if i == 0:
            # open pre-computed initial_ranker
            with open("initial_ranker.csv","r") as f:
                INITIAL_RANKER = list()
                for row in csv.reader(f):
                    INITIAL_RANKER.append((row[0],float(row[1])))
            
            display_ranker(still_valid_words,allowed_words,INITIAL_RANKER)
        
        else:
            display_ranker(still_valid_words,allowed_words)
        
        guess = input('> Enter your guess: ')
        real_feedback = list(map(int,input('>> Enter the feedback: ').split(' ')))
        
        print(">>> Expected entropy: " + str(compute_entropy(still_valid_words,guess)))
        print("    Actual entropy: " + str(compute_actual_entropy(still_valid_words,guess,real_feedback)))
        
        if check_win(real_feedback) == True:
            print(">>>> Complete!")
            break
        
        temp = reduce_allowed_words(still_valid_words,guess,real_feedback)
        still_valid_words = temp
        if len(still_valid_words) == 1:
            print(">>>> The answer is:",still_valid_words[0] + "\n")
        else:
            print(">>>> Remaining possibilities: " + str(len(still_valid_words)) + "\n")
        
        i += 1

# %% [markdown]
# ## Performance testing

# %%
def wordlebot_play(allowed_words,answer):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains ~13000 allowed guesses.
    answer : str
        Five-letter actual answer.

    Returns
    -------
    guess_count : int
        Number of guesses needed to reach the actual answer.

    """
    still_valid_words = allowed_words[:]
    i = 0
    guess_count = 0
    
    while True:
        
        final_guess_check = len(still_valid_words) == 1 #True or False
        
        if i == 0: 
            pass #skip entropy computation for first guess - dev purpose
        elif final_guess_check == True:
            pass #skip entropy computation when there's only one possible answer left
        else:
            ranker = get_ranker(still_valid_words,allowed_words)
        
        if final_guess_check == True:
            guess = still_valid_words[0]
        else:
            guess = ranker[0][0]
            
        guess_count += 1
        
        real_feedback = get_feedback(guess,answer)
        
        if check_win(real_feedback) == True:
            break
        
        temp = reduce_allowed_words(still_valid_words,guess,real_feedback)
        still_valid_words = temp
        i += 1
    
    return guess_count

# %%
def test_for_performance(allowed_words,possible_answers,n="all"):
    """
    

    Parameters
    ----------
    possible_answers : list
        Contains ~2300 human-curated possible answers.
    n : int
        Default to "all" - if n is not given, test on all possible answers.
        If n is given, test on first n answers of all possible answers.

    Returns
    -------
    None.
    Prints bar plot showing frequency of number of guesses needed.

    """
    #initialize
    total = len(possible_answers)
    performance_count = dict()
    
    #gameplay for ~2300 words in POSSIBLE_ANSWERS
    count = 1
    if n == "all":
        for word in possible_answers:
            start = time.time()
            guess_count = wordlebot_play(allowed_words,word)
            end = time.time()

            performance_count[guess_count] = performance_count.get(guess_count,0) + 1
            print("Word " + str(count) + "/" + str(total) + ": " + word + " - Time taken: " + str(end-start))
            count += 1
            
    else:
        for word in possible_answers[:n]:
            start = time.time()
            guess_count = wordlebot_play(allowed_words,word)
            end = time.time()

            performance_count[guess_count] = performance_count.get(guess_count,0) + 1
            print("Word " + str(count) + "/" + str(n) + ": " + word + " - Time taken: " + str(end-start))
            count += 1
    
    #visualize
    x = list(range(1,max(performance_count.keys())+1))
    y = [performance_count.get(i,0) for i in x]
    plt.bar(x,y,color='royalblue',alpha=0.7)
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)
    plt.title('WordleBot - Test performance')
    plt.xlabel('Number of guesses needed')
    plt.ylabel('Frequency')
    plt.show()
        
    #average number of guesses needed
    average = 0
    for (guess_count,frequency) in performance_count.items():
        average += guess_count * frequency
    if n == "all":
        average = average/len(possible_answers)
    else:
        average = average/n
    print("> Average number of guesses needed:",average)

    #detailed distribution
    print("> Detailed distribution of number of guesses needed:")
    for guess_count in sorted(performance_count):
        print("- " + str(guess_count) + " guess(es): " + str(performance_count[guess_count]))

# %%
def test_for_time_complexity(allowed_words):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains valid guesses.

    Returns
    -------
    None.
    Prints line graph showing time complexity based on the number of words whose
    entropy is to be calculated and ranked.

    """

    #initialize
    time_complexities = list()
    interval = [10,30,100,300,1000,3000]
    
    for n in interval:
        ranker = list()
        start = time.time()
        for word in allowed_words[:n]:
            ranker.append((word,compute_entropy(allowed_words,word)))
        ranker.sort(key = lambda t: t[1], reverse = True)
        end = time.time()
        time_complexities.append(end-start)
    
    #visualize    
    plt.plot(interval,time_complexities)
    plt.title('WordleBot - Time complexities')
    plt.xlabel('Number of considered words')
    plt.ylabel('Time (s)')
    plt.show()

# %% [markdown]
# # Simulation

# %%
def print_guess_board(guess_board):
    print(' ___________')
    for i in range(6):
        print('|',end=' ')
        for j in range(5):
            print(guess_board[i][j],end=' ')
        print('|')
    print('|___________|\n')

# %%
def wordlebot_simulation(allowed_words):
    """
    

    Parameters
    ----------
    allowed_words : list
        Contains ~13000 allowed guesses.

    Returns
    -------
    None.
    Prints the interactive program for user to play Wordle and input real feedback.

    """
    answer = input('Enter a word for the WordleBot to guess: ')
    still_valid_words = allowed_words[:]
    guess_board = [["_"]*5 for i in range(6)]
    attempt_number = 0
    incorrect_list = list()
    
    while attempt_number <= 5:

        #print guess_board
        print_guess_board(guess_board)
        input('')

        print("Guess #" + str(attempt_number+1))
        
        #display ranker
        if attempt_number == 0:
            # open pre-computed initial_ranker
            with open("initial_ranker.csv","r") as f:
                INITIAL_RANKER = list()
                for row in csv.reader(f):
                    INITIAL_RANKER.append((row[0],float(row[1])))
            
            ranker = display_ranker(still_valid_words,allowed_words,initial_ranker=INITIAL_RANKER,simulation=True)
        
        else:
            ranker = display_ranker(still_valid_words,allowed_words,simulation=True)
        
        #display guess
        print('> Enter your guess: ',end='')
        if len(still_valid_words) == 1:
            guess = still_valid_words[0]
        else:
            guess = ranker[0][0]
        print(guess)
        
        #update feedback into guess_board
        real_feedback = get_feedback(guess,answer)

        for j in range(5):
            if real_feedback[j] == 0:
                incorrect_list.append(guess[j])
            elif real_feedback[j] == 1:
                guess_board[attempt_number][j] = guess[j].lower()
            else:
                guess_board[attempt_number][j] = guess[j].upper()
        
        print(">> Expected entropy: " + str(compute_entropy(still_valid_words,guess)))
        print("   Actual entropy: " + str(compute_actual_entropy(still_valid_words,guess,real_feedback)))
        
        if check_win(real_feedback) == True:
            print(">>> Complete!")
            break
        
        temp = reduce_allowed_words(still_valid_words,guess,real_feedback)
        still_valid_words = temp
        if len(still_valid_words) == 1:
            print(">>> The answer is:",still_valid_words[0])
        else:
            print(">>> Remaining possibilities: " + str(len(still_valid_words)))

        #print incorrect_list
        print('>>>> Incorrect:',sorted(set(incorrect_list)))
        print()    
        
        attempt_number += 1
    print_guess_board(guess_board)

# %% [markdown]
# # Running

# %%
def main():
    with open("allowed_words.txt","r") as f:
        ALLOWED_WORDS = list()
        for line in f:
            line = line.rstrip()
            ALLOWED_WORDS.append(line)
    
    
    with open("possible_answers.txt","r") as f:
        POSSIBLE_ANSWERS = list()
        for line in f:
            line = line.rstrip()
            POSSIBLE_ANSWERS.append(line)

    wordlebot_simulation(ALLOWED_WORDS)

# %%
if __name__ == "__main__":
    main()


