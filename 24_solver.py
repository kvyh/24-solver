# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 07:36:42 2021

@author: karlv

Given a list of input values to n_solver and a target (default 24)
finds the combinations of operations between the values that reach
the target value.
n_solver([8,3], 24) will find 8*3
n_solver([4,6], 10) will find 4+6
"""

import copy

 
class Value():
    """
    preserves the process of reaching the current value
    and handles equivalence
    """
    def __init__(self, value, desc):
        self.value = value
        self.added = [value]
        self.sub = []
        self.desc = desc

    def __repr__(self):
        # when printing the object, it will print the description
        return self.desc
        
    def __eq__(self, val2):
        # 5-(3-5) == 5+(5-3) but we want to keep separate from (5*2)-3 
        return (self.value == val2.value and self.added == val2.added 
                and self.sub == val2.sub)
        
    def create_add(self,val2):
        """creates a new Value with the sum of val2 and itself"""
        new_val = Value(self.value + val2.value, "(" + self.desc + "+"
                        + val2.desc + ")")
        new_val.added = sorted(self.added + val2.added)
        new_val.sub = sorted(self.sub + val2.sub)
        
        return new_val
        
    def create_multi(self,val2):
        """creates a new Value with the product of val2 and itself"""
        new_val = Value(self.value * val2.value, "(" + self.desc + "*"
                        + val2.desc + ")")
        new_val.added = sorted([x*y for x in self.added for y in val2.added] +
                               [a*b for a in self.sub for b in val2.sub])
        new_val.sub = sorted([x*y for x in self.added for y in val2.sub] +
                               [a*b for a in self.sub for b in val2.added])        
        return new_val
        
    def create_sub(self,val2):
        """creates a new Value with the difference of val2 and itself"""
        new_val = Value(self.value - val2.value, "(" + self.desc + "-"
                        + val2.desc + ")")
        new_val.added = sorted(self.added + val2.sub)
        new_val.sub = sorted(self.sub + val2.added)
        
        return new_val
        
    def create_div(self, val2):
        """creates a new Value with the quotient of val2 and itself"""
        if val2.value == 0:
            return ValueError("Cannot divide by 0!")
        new_val = Value(self.value / val2.value, "(" + self.desc + "/"
                        + val2.desc + ")")
        new_val.added = sorted([a / val2.value for a in self.added])
        new_val.sub = sorted([s / val2.value for s in self.sub])  
        
        return new_val


def operations(unused: list, current, op_value):
    """
    performs +-*/ operations between current and op_value
    
    returns [(unused, new_value),]
    """
    results = []
    
    results.append((unused, current.create_add(op_value)))
    results.append((unused, current.create_multi(op_value)))
    results.append((unused, current.create_sub(op_value)))
    results.append((unused, op_value.create_sub(current)))
    if op_value.value != 0:
        results.append((unused, current.create_div(op_value)))
    if current.value != 0:
        results.append((unused, op_value.create_div(current)))
    
    return results
    
def next_iterations(unused: list, current):
    """
    separates values from the unused list for the next step
    """
    nxt = []
    for i in range(len(unused)):
        cpy = copy.copy(unused)
        oper = cpy.pop(i)
        if (cpy, oper) not in nxt:
            nxt.append((cpy, oper))
    
    other = get_all_options(unused)
    for o in other:
        if ([], o) not in nxt:
            nxt.append(([], o))
    
    return [(x[0], current, x[1]) for x in nxt]

def get_all_options(values: list):
    """
    returns all possible values reachable with the input list of values
    """
    # create a frontier to hold the potential next steps while 
    # we work through them 1-by-1
    frontier = []
    for i in range(len(values)):
        # separate one value from the list for a starting value
        cpy = copy.copy(values)
        cur = cpy.pop(i)
        if (cpy, cur) not in frontier:
            frontier.append((cpy, cur))
            
    # iterate and record final Values
    ends = []
    while frontier:
        # get the oldest item from the frontier (breadth-first search)
        edge = frontier.pop(0)
        # get each possible value to +-*/ with the current total
        steps = next_iterations(edge[0], edge[1])
        for s in steps:
            # get the results from perforimg +-*/
            ops = operations(s[0], s[1], s[2])
            for op in ops:
                # remove from cycle if nothing left unused
                if not op[0]:
                    ends.append(op[1])
                # add the result to the frontier if it is not already there
                elif op not in frontier:
                    frontier.append(op)

    return ends

def n_solver(values: list, target = 24, verbose = True):
    """
    inputs: a list of values and a target
    
    returns: a list of 'Value's that meet the target
    
    the returned list is condensed by removing as many redundant results
    as possible, this may remove some similiar-but-unique options
    """
    # turn the values into 'Value's for recording operations and pruning
    lis = []
    for v in sorted(values):
        lis.append(Value(v, str(v)))
    
    # find all the 'Value's that can be reached from the input values
    opts = get_all_options(lis)
    
    # remove redundant solutions (e.g. only keep one of 6+3*(10-4) and 6-3*(4-10))
    unique = []
    for opt in opts:
        if opt.value == target and opt not in unique:
                unique.append(opt)
    
    if verbose:
        print("unique solutions:")
        for u in unique:
            print(u)
    
    return unique