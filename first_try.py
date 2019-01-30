# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 11:14:05 2019

@author: Annie
"""

from gurobipy import *

#time points in seconds
time_points = [0,1,2,3,4,5]

#time points for subtracting ith time value from 
#i+1th time value
time_points_it = [0,1,2,3,4]
#pv output for each time point
P_pf = [10,20,30,20,10,10]

#load forecast for each time point
P_lf = [20,30,50,50,30,20]


#setting up a model to minimize demand charge
#which is the sum of the differences of the 
#load forecasts and the pv+ output multiplied by 
#the time change (each time change is one second)
#pv= output = pv output + storage output
model = Model('Demand Charge Minimization')

#trying to add a storage variable for each time point
storage = model.addVars(time_points, name = "Storage")

#setting up a simplified objective function
obj = quicksum(P_lf[i] - P_pf[i] - storage[i] for i in time_points)

#adding random lower bound to sum of storage output
model.addConstr(storage.sum()>= 10, "Minimum Storage Sum")

#adding random upper bound to sum of storage output
#gurobi does not seem to support strict inequalities for this 
#type of constraint expression
model.addConstr(storage.sum()<= 300, "Maximum Storage Sum")

#adding a constraint on each storage value
model.addConstrs((storage[i] >= 10 for i in time_points) , "Minimum Storage")

#adding a constraint on each storage value
model.addConstrs((storage[i] <= 200 for i in time_points), "Maximum Storage")

#adding a constraint for the power ramp
#power generation is the sum of the storage and the PV output
model.addConstrs((((storage[i+1] + P_pf[i+1]) - (storage[i] + P_pf[i])) == 10 for i in time_points_it), "Power Ramp Condition")

#inputting objective function and command to minimize into model
model.setObjective(obj, GRB.MINIMIZE)

#optimizing model
model.optimize()

#examining storage for each time point
for v in model.getVars():
  print('%s %g' % (v.varName, v.x))