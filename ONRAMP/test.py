
# from decimal import *
# getcontext().prec = 198
#
# print(2**659)
#
# from numpy import array
# from numpy import argmax
# from tensorflow.keras.utils import to_categorical
# from sklearn.preprocessing import LabelEncoder
#
# # define example
# ##对字符串
# data = ['cold', 'cold',  'cold', 'hot', 'hot',  'cold',  'hot']
# values = array(data)
# print(values)
# # integer encode
# label_encoder = LabelEncoder()
# integer_encoded = label_encoder.fit_transform(values)
# print(integer_encoded)
#
# ##对数值
# # data=[1, 3, 2, 0, 3, 2, 2, 1, 0, 1]
# # data=array(data)
# # print(data)
#
# # one hot encode
# encoded = to_categorical(integer_encoded)
# print(encoded)
# # invert encoding
# inverted = argmax(encoded[0])
# print(inverted)
# class A:
#     def __init__(self):
#         self.edgelist = {'gneE4': 3, 'gneE5': 4, 'gneE6': 3, 'gneE7': 1}
#         print(list(self.edgelist.keys()).index('gneE5'))
#
# # A()
#
# a = '3'
# b = int(a)
# c = str(b)
#
# print(a,b,type(b),c,type(c))

from tensorflow.keras import models, layers, optimizers