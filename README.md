# Gomoku
A Gomoku AI using CNN, which is inspired by [AlphaZero](https://www.deepmind.com/blog/alphazero-shedding-new-light-on-chess-shogi-and-go) 

## Note
if anyone tries to run this program directly on a M1 Mac, please uses a python interpreter of version 3.9.13 (Intel only), because its unknown wehther PyQt5 can run correctly under other versions.

## Dependencies
[Pytorch](https://pytorch.org)

[PyQt5](https://pypi.org/project/PyQt5/)

[numpy](https://numpy.org)

## How to run

### For directly downloading 
change the working directory to Gomoku, then run commands:  
***python3 main.py play***   for playing with AI  
***python3 main.py train [training times (optional)]***   for training the AI

it is strongly recommended that training the AI on GPUs

