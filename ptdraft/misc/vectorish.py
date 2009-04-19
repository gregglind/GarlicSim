import math

def add(vec1,vec2):
    return tuple((vec1[i]+vec2[i]) for i in range(len(vec1)))

def mult(scal,vec1):
    return tuple(vec1[i]*scal for i in range(len(vec1)))

def average(vec1,vec2):
    return mult(0.5,add(vec1,vec2))