from bitarray import bitarray
import mmh3
import os
import sys
import math
# from Crypto.Util.number import size
from fileinput import filename

class BloomFilter:
    
    
        
    
    
    def __init__(self,num_elem, fp, flname):
#         self.size = size
        self.num_elem = num_elem
#         self.fp = fp
#         self.hash_cout = hash_cout
       
        k = 1.0
        min_m = float("inf")
        min_k = 0.0
        curr_m = 0.0
        
        while k < 10000.0:
            numerator = (-k* num_elem)
            denomiator = math.log(1.0-math.pow(fp, 1.0/k))
            curr_m = numerator / denomiator
            if curr_m < min_m:
                min_m = curr_m
                min_k = k 
            k +=1.0
        self.hash_cout= int(min_k)
        self.size = self.hash_cout*self.num_elem
#         self.size = math.ceil(num_elem * self.hash_cout)
        
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)
        self.fp = open(flname)
        print self.hash_cout
        print self.size
            
            
        
    def add(self,string):
        for seed in xrange(self.hash_cout):
            result = mmh3.hash(string,seed) % self.size
            self.bit_array[result]=1
            
    def lookup(self,string):
        for seed in xrange(self.hash_cout):
            result = mmh3.hash(string,seed)%self.size
            if self.bit_array[result] == 0:
                return 0
        return 1
