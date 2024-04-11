
from pyeda.inter import *

# symbols to create bool vars
A, B, C, D, E = map(exprvar, ['xx1', 'xx2', 'xx3', 'xx4', 'xx5'])
a, b, c, d, e = map(exprvar, ['yy1', 'yy2', 'yy3', 'yy4', 'yy5'])

x = [A, B, C, D, E]
y  = [a, b, c, d, e]
prime = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

# function to create an expression given an int
def int2expr(n):
  intStr = format(n, '05b')
  if n % 2 == 0: # if n is even create expr using xxs
    nodeExpr = y.copy()
  else: # else use yys
    nodeExpr = x.copy()
  for i in range(5):
    if intStr[i] == '0':
      nodeExpr[i] = Not(nodeExpr[i])
  return exprvar(str(tuple(nodeExpr))) # return expr

# function returns edge formula if it exists
def RR(i, j):
  edge = None
  if ((i + 3) % 32 == j % 32) or ((i + 8) % 32 == j % 32): # checks constraints
    edge = And(int2expr(i), int2expr(j))
  return edge

# function returns an expr of i if even
def EVEN(i):
  n = None
  if i % 2 == 0:
    n = int2expr(i)
  return n

# function returns expr of i if prime
def PRIME(i):
  n = None
  if i in prime:
    n = int2expr(i)
  return n

# function returns the expr of i and j if there are connected in 2 steps
def RR2(i, j):
  edge = None
  for k in range(32): # check every possible value that can be node between i and j
    if RR(i, k) and RR(k, j):
      edge = And(RR(i, k), RR(k, j)) # if found create the formula using the 3 nodes
      edge = edge.compose({int2expr(k): int2expr(i) & int2expr(j)}) # exclude the node in between
      # edge = edge.smoothing()
      break
  return edge

# function returns the pair of nodes in an expr if they are connected by an even number of steps
def RR2star(u, v):
  if RR2(u, v): # checks if u and v are connected in 2 steps
      return RR2(u, v)

  for i in range(32): # find possibles nodes in between u and v
    k = 0
    if RR2(u, i): # if u and i are connected by 2 steps
      k = i + 6
      while k != i: # iterate until k becomes i
        if k == v: # if u is found to connect v in an even number of steps, return the expr of u and v
          return And(int2expr(u), int2expr(k))
        k += 6 # else increment k by 6
        if k >= 32: # if k is out of boundaries, compute real k value
          k -= 32
  return None

# function returns True if bdd is True
def StatementA():
  statement = And()
  for u in prime: # for every u in prime list
    for v in range(32): # find every even number
      if v % 2 == 0:
        # create formula
        statement = And(statement, Or(Not(PRIME(u)), And(EVEN(v), RR2star(u, v))))
        # convert expr to bdd to eliminate v exprs
        statement = expr2bdd(statement).smoothing(expr2bdd(int2expr(v)))
        # convert bdd to expr to continue editing it
        statement = bdd2expr(statement)

      # negate statement
      statement = Not(statement)
      # convert expr to bdd to eliminate u exprs
      statement = expr2bdd(statement).smoothing(expr2bdd(int2expr(u)))
      # convert bdd to expr again
      statement = bdd2expr(statement)

  # negate statement again
  statement = Not(statement)
  # convert expr to bdd
  statement = expr2bdd(statement)

  return statement.is_one() # returns if bdd is True

print(StatementA())