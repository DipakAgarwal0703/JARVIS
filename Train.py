# 1 -(pip install nltk==3.7,torch==1.11.0) 
#Qc-
import nltk 
from nltk.stem.porter import PorterStemmer
from torch.utils.data import Dataset,DataLoader
import torch.nn as nn
import json
import torch
import numpy as np 

def TrainTalks():
    class NeuralNet(nn.Module):

        def __init__(self,input_size,hidden_size,num_classes):
            super(NeuralNet,self).__init__()
            self.l1 = nn.Linear(input_size,hidden_size)
            self.l2 = nn.Linear(hidden_size,hidden_size)
            self.l3 = nn.Linear(hidden_size,num_classes)
            self.relu = nn.ReLU()

        def forward(self,x):
            out = self.l1(x)
            out = self.relu(out)
            out = self.l2(out)
            out = self.relu(out)
            out = self.l3(out)
            return out

    Stemmer = PorterStemmer()

    def tokenize(sentence):
        return nltk.word_tokenize(sentence)

    def stem(word):
        return Stemmer.stem(word.lower())

    def bag_of_words(tokenized_sentence,words):
        sentence_word = [stem(word) for word in tokenized_sentence]
        bag = np.zeros(len(words),dtype=np.float32)

        for idx , w in enumerate(words):
            if w in sentence_word:
                bag[idx] = 1

        return bag

    with open("DataBase\\Json DataBase\\Talks.json",'r') as f:
        intents = json.load(f)

    all_words = []
    tags = []
    xy = []

    for intent in intents['intents']:
        tag = intent['tag']
        tags.append(tag)

        for pattern in intent['patterns']:
            w = tokenize(pattern)
            all_words.extend(w)
            xy.append((w,tag))

    ignore_words = [',','?','/','.','!']
    all_words = [stem(w) for w in all_words if w not in ignore_words]
    all_words = sorted(set(all_words))
    tags = sorted(set(tags))

    x_train = []
    y_train = []

    for (pattern_sentence,tag) in xy:
        bag = bag_of_words(pattern_sentence,all_words)
        x_train.append(bag)

        label = tags.index(tag)
        y_train.append(label)

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    num_epochs = 1000
    batch_size = 8
    learning_rate = 0.001
    input_size = len(x_train[0])
    hidden_size = 8
    output_size = len(tags)
    print(">> Training The Chats Module :- Conciousness ")

    class ChatDataset(Dataset):

        def __init__(self):
            self.n_samples = len(x_train)
            self.x_data = x_train
            self.y_data = y_train

        def __getitem__(self,index):
            return self.x_data[index],self.y_data[index]

        def __len__(self):
            return self.n_samples
        
    dataset = ChatDataset()

    train_loader = DataLoader(dataset=dataset,
                                batch_size=batch_size,
                                shuffle=True,
                                num_workers=0)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = NeuralNet(input_size,hidden_size,output_size).to(device=device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)

    for epoch in range(num_epochs):
        for (words,labels)  in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)
            outputs = model(words)
            loss = criterion(outputs,labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch+1) % 100 ==0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

    print(f'Final Loss : {loss.item():.4f}')

    data = {
    "model_state":model.state_dict(),
    "input_size":input_size,
    "hidden_size":hidden_size,
    "output_size":output_size,
    "all_words":all_words,
    "tags":tags
    }

    FILE = "DataBase\\PTH DataBase\\Talks.pth"
    torch.save(data,FILE)

    print(f"Training Complete, File Saved To {FILE}")
    print("             ")

TrainTalks()