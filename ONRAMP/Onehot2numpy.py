
import random
import numpy as np
from numpy import array
from numpy import argmax
# from tensorflow.keras.utils import to_categorical
# from sklearn.preprocessing import LabelEncoder

class Onehot2numpy():
    def __init__(self,n):
        self.data = ['straight','left','right']
        self.values = array(self.data)
        self.n = n

    def bindigits(self,a, bits):

        s = bin(a & int("1" * bits, 2))[2:]

        return ("{0:0>%s}" % (bits)).format(s)

    def bit_to_list(self,a, n):
        S = [0 for i in range(n)]
        i = -1
        while a != 0:
            S[i] = a % 2
            a = a >> 1
            i -= 1
        return S

    def num_2_bit(self,a):#输入一个十进制整数
        b = np.zeros(self.n)
        list = []
        for i in range(1,self.n//4+1):
            a_i = self.get_mod(a,i-1) - 10 * self.get_mod(a,i)
            a_i_list = self.bit_to_list(a_i,4)
            # print(i,'位',self.get_mod(a,i-1) - 10 * self.get_mod(a,i),a_i_list)
            if i > 1:
                b[-i * 4:-(i - 1) * 4] = a_i_list
                # print(i,'数组',-(i-1)*4,-i*4,b[-i*4:-(i-1)*4] )
            elif i == 1:
                b[-i * 4:] = a_i_list
                # print(i,'数组',-(i-1)*4,-i*4,b[-i*4:] )
        # print('终',b)
        # while i:
        #     list.append(i % 2)
        #     i = i // 2
        #
        # if i == 0:
        #     list.append(0)
        #
        # list.reverse()
        # print('len',len(list))
        # # print('len',i,len(list))
        # b[-len(list):] = list
        # # print(list)

        return np.append(b,0)

    def get_binary(self,a):
        bin_a = bin(a)
        c = self.bit_to_list(bin_a,440)
        # print('c',len(c))

        b = np.zeros(self.n)
        b[:len(bin_a)] = bin_a
        # print(b,bin_a)
        return

    def get_digit(self,a):
        num = np.array()
        num = np.array([self.bit_to_list(self.get_mod(a,i) - 10 * self.get_mod(a,i+1),self.n) for i in range(self.n)][::-1])
        # print(num)
        # print(num.reshape(1,-1)[0])
        return num.reshape(1,-1)[0]

    def get_mod(self,a,n):

        return a//10**(n)

    def get_action(self,act):

        action = self.get_digit(act)
        # print(action)

        return action

    #     self.label_encoder = LabelEncoder()
    #     self.integer_encoded = self.label_encoder.fit_transform(self.values)
    #
    # def onehot_encode(self):
    #     encoded = to_categorical(self.integer_encoded)
    #
    #     print(self.integer_encoded,encoded)
    #
    # def invert_encode(self):
    #     self.inverted = argmax(self.encoded[0])
    #
    #

# one hot encode
# encoded = to_categorical(integer_encoded)
# print(encoded)
# # invert encoding
# inverted = argmax(encoded[0])
# print(inverted)

if __name__ == '__main__':
    # b = 2**659-1
    # a = random.randint(0,b)
    # O = Onehot2numpy()
    # s = O.bit_to_list(a,b)
    # print(s)

    # a = 9
    # b = bin(a)
    # print(b[2:])

    a = 1234
    O = Onehot2numpy(24)
    b = O.num_2_bit(a)
    print(len(b),b)
    # b = O.get_binary(a)
    # c = O.get_digit(a)
    # print(c,len(c))
    # # b = O.get_action(a)
    # print(len(b))
    # O.get_action(a)
    # print(O.bindigits(9,8))
    # O.get_binary(a)
