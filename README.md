# Gomoku
A Gomoku AI using CNN, which is inspired by [AlphaZero](https://www.deepmind.com/blog/alphazero-shedding-new-light-on-chess-shogi-and-go) 

## Note
if anyone tries to run this program directly on a M1 Mac, please uses a python interpreter of version 3.9.13 (Intel only), because its unknown wehther PyQt5 can run correctly under other versions.

## Dependencies
[Pytorch](https://pytorch.org)

[PyQt5](https://pypi.org/project/PyQt5/)

[numpy](https://numpy.org)

## How to run

### For directly download 
After downloading, change the working directory to Gomoku, then run commands:  
***python3 main.py play***   for playing with AI  
***python3 main.py train [training times (optional)]***   for training the AI

it is strongly adviced to train the AI on GPUs and it may take hours to finish the train depending on the 'training times' parameter.
The trained net is saved in net_weights.pth.

