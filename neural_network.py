import random
import math
import aigame_config as config

def random_weight():
    return random.random() *2-1

def sigmod(x):
    if x<= -700:
        return 0.0
    elif x>= 50:
        return 1.0
    return 1/(1+math.exp(-x))

class NeuralErr(Exception):
    pass

class Neuron(object):#神经元
    def __init__(self,pre_Neuron_num):#pre_Neuron_num ：上一层数据的个数
        self.weights = []
        #根据上一层神经元的数量来初始化weights
        #初始化的weights应该选择： 权值*输入数据的结果的累计和尽量处于活跃状态（-5,+5)
        #这里将权值设定在（-1，+1）
        self.weights = [random_weight() for _ in range(pre_Neuron_num)]
        self.value = 0 #结果  要传递给下一层

    def cal_result(self,inputs):
        if not len(inputs) == len(self.weights):
            raise NeuralErr("inputs's numbers is not right")
        sum = 0
        for i in range(len(inputs)):
            sum+=inputs[i]*self.weights[i]
        self.value = sigmod(sum)
        return self.value

class Layer(object):
    def __init__(self,neuron_num,pre_Neuron_num):
        self.neurons = [Neuron(pre_Neuron_num) for i in range(neuron_num)]

    def __iter__(self):
        for n in self.neurons:
            yield n

    def __len__(self):
        return len(self.neurons)

#构建神经网络
class Neural_Network(object):
    #输入层神经元数量，隐含层神经元数量，输出层神经元数量
    def __init__(self,input,hiddens,output):
        self.layers = []
        pre_layer_neurous = 0
        #输入层
        input_layer = Layer(input,pre_layer_neurous)
        self.layers.append(input_layer)
        #隐含层
        pre_layer_neurous = len(input_layer)
        for hidden in hiddens:
            hidden_layer = Layer(hidden,pre_layer_neurous)
            self.layers.append(hidden_layer)
            pre_layer_neurous = len(hidden_layer)
        #输出层
        output_layer = Layer(output,pre_layer_neurous)
        self.layers.append(output_layer)

    def getResult(self,inputs):
        if not len(inputs) == len(self.layers[0]):
            raise NeuralErr("the data that your provide is no right")
        #输入层采集数据
        pre_values = []
        for layer in self.layers:
            result = []
            if layer == self.layers[0]:
                for i in range(len(inputs)):
                    layer.neurons[i].value = inputs[i]
                    pre_values.append(layer.neurons[i].value)
            else:
                for neuron in layer:
                    neuron.cal_result(pre_values)
                    result.append(neuron.value)
                pre_values = result

        return  result

    def getNetwork(self):
        '''
        将神经网络模型数据化
        :return:{"network"：[5,5,1],"weights":[w1,w2,w3,w4......]}
        '''
        data = {"network":[],"weights":[]}
        for layer in self.layers:
            data['network'].append(len(layer))
            if layer == self.layers[0]:
                continue
            for neuron in layer:
                for weight in neuron.weights:
                    data['weights'].append(weight)
        return data

    def setNetwork(self,networkData):
        '''
        使用数据化模型重置神经网络
        :param networkData:
        :return:None
        '''
        self.layers=[]
        pre_layer_neurous = 0
        weigt_index = 0
        for layer_neuron_num in networkData['network']:
            layer = Layer(layer_neuron_num,pre_layer_neurous)
            for neuron in layer:
                for i in range(len(neuron.weights)):
                    neuron.weights[i] = networkData['weights'][weigt_index]
                    weigt_index+=1
            self.layers.append(layer)
            pre_layer_neurous = layer_neuron_num



    def __str__(self):
        s = ""
        for layer in self.layers:
            s+="=" * 50+"\n"
            for n in layer:
                s+="{"
                for w in n.weights:
                    s+=str(w)+","
                s+="}\n"
        return s



if __name__ == '__main__':
    network = config.network
    myNetwork1 = Neural_Network(network[0],network[1],network[2])
    myNetwork2 = Neural_Network(network[0], network[1], network[2])
    print(myNetwork1)
    print(myNetwork2)
    myNetwork2.setNetwork(myNetwork1.getNetwork())
    print(myNetwork2)





