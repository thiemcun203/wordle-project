# Setting randomly a secret_word
import random
with open("possible_words.txt","r") as file:
    possible_lst=[]
    for i in file:
        possible_lst.append(i[:5])
secret_word=random.choice(possible_lst)
# secret_word= "apple"
# print(secret_word)

# Input and check the condition of the input
with open("allowed_words.txt","r") as file:
    allowed_lst=[]
    for i in file:
        allowed_lst.append(i[:5])
for i in range(6):
    guess=input(f"Enter your {i+1}th guess: ").lower()
    while len(guess)!=5 or guess not in allowed_lst  :
        print("Invalid input guess!!")
        guess=input(f"Enter your {i+1}th guess AGAIN: ").lower() 
    
    '''There are some bugs relating to one letter of guess is shown both yellow and green in result;
        two letters of guess is same position in result; result does not prioritze green letter, etc..
        So, we need to check there is green or not and replace this letter by * in secret_word_lst ,
        then check there is yellow or not in REMAINER list and replace this letter by * in secret_word_lst to avoid bugs'''
    
    # Check input with the secret_word and print the result
    secret_word_lst=[i for i in secret_word]
    result_lst=["⬜" for i in range(5)]
    remainer=[i for i in range(5)] # store all letter which is not green
    # check all green letter firstly
    for i in range(5):
        if guess[i]==secret_word[i]:
            result_lst[i]="🟩"
            remainer.remove(i)
            # replace this letter to *
            secret_word_lst[i]='*' 

    # check all remainers is yellow or not
    for i in remainer:
        if guess[i] in secret_word_lst:
            y=secret_word.find(f'{guess[i]}')
            result_lst[i]="🟨"                    
            # find index of yellow letter in the secret word then replace this letter to *
            secret_word_lst[y]='*'

    result="".join(result_lst)
    print(result)
    if result=="🟩🟩🟩🟩🟩":
        break
    
print("CONGRATULATION 🎉 🎉" if result=="🟩🟩🟩🟩🟩" else f'LOSER!!! 😭😭 \nResult is {secret_word.upper()}')

            
            
            
            
    

