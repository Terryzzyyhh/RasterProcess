import torch
from torch import nn
from torchvision import datasets
from torchvision import transforms
from torch.utils.data import DataLoader
import torch.nn.functional as F
import torch.optim as opt

batch_size = 64
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))])

train_dataset = datasets.MNIST(root='../dataset/mnist/', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size)

test_dataset = datasets.MNIST(root='../dataset/mnist/', train=False, download=True, transform=transform)
test_loader = DataLoader(test_dataset, shuffle=False, batch_size=batch_size)

class InseptionA(torch.nn.Module):
    def __init__(self,in_channles):
        super(InseptionA, self).__init__()
        self.branch_pool=nn.Conv2d(in_channles,24,kernel_size=1)
        self.branch1x1=nn.Conv2d(in_channles,24,kernel_size=1)
        self.branch5x5_1=nn.Conv2d(in_channles,16,kernel_size=1)
        self.branch5x5_2=nn.Conv2d(16,24,kernel_size=5,padding=2)
        self.branch3x3_1=nn.Conv2d(in_channles,16,kernel_size=1)
        self.branch3x3_2=nn.Conv2d(16,24,kernel_size=3,padding=1)
        self.branch3x3_3=nn.Conv2d(24,24,kernel_size=3,padding=1)

    def forward(self,x):
        branchpool=F.avg_pool2d(x,kernal_size=3,stride=1,padding=1)
        branchpool=self.branch_pool(branchpool)

        branch1x1=self.branch1x1(x)

        branch5x5=self.branch5x5_1(x)
        branch5x5=self.branch5x5_2(branch5x5)

        branch3x3=self.branch3x3_1(x)
        branch3x3=self.branch3x3_2(branch3x3)
        branch3x3 = self.branch3x3_3(branch3x3)

        output=[branchpool,branch1x1,branch3x3,branch5x5]
        return torch.cat(output,dim=1)

class GoogleNetSimple(nn.Module):
    def __init__(self,x):
        super(GoogleNetSimple, self).__init__()
        self.conv1=nn.Conv2d(1,10,kernel_size=5)
        self.conv2=nn.Conv2d(88,20,kernel_size=5)

        self.insep1=InseptionA(in_channles=10)
        self.insep2=InseptionA(in_channles=20)

        self.mp=nn.MaxPool2d(2)
        self.fc=nn.Linear(1408,10)

    def forward(self,x):
        in_size=x.size(0)
        x=F.relu(self.mp(self.conv1(x)))
        x=self.insep1(x)
        x = F.relu(self.mp(self.conv2(x)))
        x=self.insep2(x)
        x=x.view(in_size,-1)
        x=self.fc(x)
        return x

def train(epoch):
    running_loss = 0.0
    for batch_idx, data in enumerate(train_loader, 0):
        inputs, target = data
        optimizer.zero_grad()

        # forward + backward + update
        outputs = model(inputs)
        loss = criterion(outputs, target)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if batch_idx % 300 == 299:
            print('[%d, %5d] loss: %.3f' % (epoch + 1, batch_idx + 1, running_loss / 300))
            running_loss = 0.0

def test():
    correct = 0
    total = 0
    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            outputs = model(images)
            _, predicted = torch.max(outputs.data, dim=1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        print('Accuracy on test set: %d %%' % (100 * correct / total))

model = GoogleNetSimple()
criterion = torch.nn.CrossEntropyLoss()
optimizer = opt.SGD(model.parameters(), lr=0.01, momentum=0.5)

if __name__ == '__main__':
    for epoch in range(6):
        train(epoch)
        test()



