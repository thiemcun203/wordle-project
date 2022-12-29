# WordleBot

## Overview
Wordle is a word game (owned by The New York Times Company), where players are given six attempts to guess a five-letter word.
For each guess, the game returns feedback in the form of colored tiles. Specifically,
  A green tile suggests a correct letter (a letter in the answer) in the right position.
  A yellow tile suggest a correct letter in the wrong position.
  A gray tile suggests a wrong letter (a letter not in the answer).
  
## Goal
An algorithm that plays Wordle by itself, aiming to minimize the number of guesses needed to reach the answer.
From a statistical point of view, this is an algorithm that minimizes the expected number of guesses needed to reach a sample of answers.

## Algorithm
Version 0.1 uses the feedback to shrink the guess space (a.k.a. list of still-possible guesses) till there is only one possible guess left. A guess is given randomly.
Version 0.2 works the same, but utilizes letter frequency (taken from the list of 13,000 possible words) to determine a guess from a guess space.

Version 1.1 computes entropy for each word of a guess space, based on the words still in the guess space, for the words still in the guess space. The word with the highest entropy is chosen as a guess.
Version 1.2 does the same, but for all original possible words (13000).