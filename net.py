import os
import torch
from torch import nn
from global_var import BOARD_SIZE, ONGOING, BLACK, WHITE, DRAW, UNCHECKED


class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()

        self.conv1 = nn.Conv2d(4, 50, 5, padding = 2)
        self.conv2 = nn.Conv2d(50, 100, 3, padding = 1)
        self.conv3 = nn.Conv2d(100, 100, 3, padding = 1)
        self.pool = nn.MaxPool2d(3, stride = 1, padding = 1)
    

        self.dense1 = nn.Linear(100 * BOARD_SIZE * BOARD_SIZE, 100)
        self.dense2 = nn.Linear(100, 50)
        self.dense3 = nn.Linear(50, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.pool(x)
        x = self.relu(x)

        x = self.conv3(x)
        x = self.conv3(x)
        x = self.pool(x)
        x = self.relu(x)

        value = torch.flatten(x,1)
        value = self.dense1(value)
        value = self.relu(value)
        value = self.dense2(value)
        value = self.relu(value)
        value = self.dense3(value)
        value = self.relu(value)
        return value

def main() :
    os.chdir(os.path.dirname(__file__))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('Using {} device'.format(device))

    board_list = [[[[0 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)] for z in range(4)] for a in range(1)]
    board_tensor = torch.tensor(board_list, dtype=torch.float)
    print(board_tensor.shape)

    model = NeuralNetwork().to(device)

    X = model(board_tensor)

    c = board_tensor.tolist()[0][0][1][2]
    print('list: ', c)


if __name__ == '__main__' :
    main()





