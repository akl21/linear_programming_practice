# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 11:14:05 2019

@author: Annie
"""

from gurobipy import *

#time points in seconds
time_points = list(range(6))

#time points for subtracting ith time value from 
#i+1th time value
time_points_it = list(range(5))

#pv output for each time point
P_pf = [10,20,30,20,10,10]

#load forecast for each time point
P_lf = [20,100,100,50,7,20]


#setting up a model that maximizes the sum of 
#the contributions of solar power for each time 
#point, where the contribution is measured as the 
#fraction of load forecast made up by solar output
#at each time point
model = Model('Total Contribution Maximization')

#adding a storage variable for each time point
storage = model.addVars(time_points, name = "Storage")

#setting up a simplified objective function
obj = quicksum((P_pf[ii] + storage[ii])/P_lf[ii] for ii in time_points)

#gurobi does not seem to support strict inequalities for this 
#type of constraint expression

#adding random lower bound to sum of storage output
model.addConstr(storage.sum()>= 0, "Minimum Storage Sum")

#adding random upper bound to sum of storage output
model.addConstr(storage.sum()<= 300, "Maximum Storage Sum")

#adding a constraint on each storage value
model.addConstrs((storage[ii] >= 0 for ii in time_points) , "Minimum Storage")

#adding a constraint on each storage value
model.addConstrs((storage[ii] <= 200 for ii in time_points), "Maximum Storage")

#adding a constraint for the power ramp
#power generation is the sum of the storage and the PV output
model.addConstrs((storage[kk + 1] - storage[kk] == 2 for kk in time_points_it), 
                 "Power Ramp Condition")

#adding constraint for the amount of extra energy that can be 
#accepted by the grid per day
model.addConstr(
        quicksum(P_pf[ii] + storage[ii] - P_lf[ii] for ii in time_points) <= 100, 
        "Maximum Accepted Energy Daily")

#adding constraint for the amount of extra energy that can be accepted in 
#a single second
model.addConstrs(((P_pf[ii] + storage[ii] - P_lf[ii]) <= 20 for ii in time_points),
                 "Maximum Accepted Energy Each Second")

#inputting objective function and command to minimize into model
model.setObjective(obj, GRB.MAXIMIZE)

#optimizing model
model.optimize()

#examining storage for each time point
for v in model.getVars():
  print('%s %g' % (v.varName, v.x))