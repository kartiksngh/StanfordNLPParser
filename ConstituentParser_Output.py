#In general, more entities are not matched, because although pCFG might label a multi token entity as a constituent at an intermediate step of probabilistic CKY,
#if another rule that does not involve the entire multi token has a higher decoding probability, then, probabilistic CKY will always choose that,
#and hence, the multi token entity might not be recognized when the sentence with the highest probability is emitted
#

entities = []
trueentities = []

def IsValid(sentence):
  leftpar = 0
  rightpar = 0
  runningsum = 0
  
  for index in range(len(sentence)):
    if sentence[index] == '(': 
      leftpar += 1
      runningsum += 1
    elif sentence[index] == ')': 
      rightpar += 1
      runningsum -= 1
    if runningsum < 0: return False
    if runningsum == 0 and leftpar > 0 and index < len(sentence)-1: return False
    
  return runningsum == 0
  
STATE_START = 0
STATE_LEFTPAR = 1
STATE_SPACE = 2
STATE_LEFTBRACKET = 3
STATE_ACCEPT  = 4
TRANSITION_CHARS = '()[] '
transition = {}

def BuildTransitionMatrix():
  transition[(STATE_START, TRANSITION_CHARS.find('('))] = STATE_LEFTPAR
  transition[(STATE_START, TRANSITION_CHARS.find(' '))] = STATE_SPACE
  transition[(STATE_START, TRANSITION_CHARS.find('['))] = STATE_LEFTBRACKET
  transition[(STATE_START, -1)] = STATE_ACCEPT
  transition[(STATE_START, TRANSITION_CHARS.find(')'))] = STATE_START
  transition[(STATE_START, TRANSITION_CHARS.find(']'))] = STATE_START
  
  
  transition[(STATE_LEFTPAR, TRANSITION_CHARS.find(')'))] = STATE_START
  transition[(STATE_LEFTPAR, TRANSITION_CHARS.find(' '))] = STATE_SPACE
  transition[(STATE_LEFTPAR, -1)] = STATE_LEFTPAR
  transition[(STATE_LEFTPAR, TRANSITION_CHARS.find('['))] = STATE_LEFTPAR
  transition[(STATE_LEFTPAR, TRANSITION_CHARS.find(']'))] = STATE_LEFTPAR  
  transition[(STATE_LEFTPAR, TRANSITION_CHARS.find('('))] = STATE_LEFTPAR
  
  
  transition[(STATE_SPACE, TRANSITION_CHARS.find('('))] = STATE_LEFTPAR
  transition[(STATE_SPACE, TRANSITION_CHARS.find('['))] = STATE_LEFTBRACKET
  transition[(STATE_SPACE, TRANSITION_CHARS.find(' '))] = STATE_SPACE
  transition[(STATE_SPACE, -1)] = STATE_ACCEPT
  transition[(STATE_SPACE, TRANSITION_CHARS.find(')'))] = STATE_ACCEPT
  transition[(STATE_SPACE, TRANSITION_CHARS.find(']'))] = STATE_ACCEPT
  
  transition[(STATE_LEFTBRACKET, TRANSITION_CHARS.find(']'))] = STATE_START
  transition[(STATE_LEFTBRACKET, TRANSITION_CHARS.find(' '))] = STATE_SPACE
  transition[(STATE_LEFTBRACKET, -1)] = STATE_LEFTBRACKET
  transition[(STATE_LEFTBRACKET, TRANSITION_CHARS.find('('))] = STATE_LEFTBRACKET
  transition[(STATE_LEFTBRACKET, TRANSITION_CHARS.find(')'))] = STATE_LEFTBRACKET
  transition[(STATE_LEFTBRACKET, TRANSITION_CHARS.find('['))] = STATE_LEFTBRACKET
  
  transition[(STATE_ACCEPT, TRANSITION_CHARS.find(')'))] = STATE_START
  transition[(STATE_ACCEPT, -1)] = STATE_ACCEPT
  transition[(STATE_ACCEPT, TRANSITION_CHARS.find('('))] = STATE_ACCEPT
  transition[(STATE_ACCEPT, TRANSITION_CHARS.find('['))] = STATE_ACCEPT
  transition[(STATE_ACCEPT, TRANSITION_CHARS.find(']'))] = STATE_ACCEPT
  transition[(STATE_ACCEPT, TRANSITION_CHARS.find(' '))] = STATE_ACCEPT

def GetSequence(sentence):
  state = STATE_START
  prevstate = STATE_START
  ret = ''
  for index in range(len(sentence)):
    prevstate = state
    state = transition[(state, TRANSITION_CHARS.find(sentence[index]))]
    if state == STATE_ACCEPT:
      if prevstate != STATE_ACCEPT and ret != '': ret = ret + ' '
      ret = ret + sentence[index]
      
  return ret
  
def GetEntities(lineindex, sentence):
  vec = []
  
  for index in range(1,len(sentence)):
    if sentence[index] == '(':
      runningsum = 1
      for index2 in range(index+1, len(sentence)):
        if sentence[index2] == ')':
          runningsum -= 1
          if runningsum == 0 and IsValid(sentence[index:index2+1]):
            vec.append(GetSequence(sentence[index:index2+1]))
        elif sentence[index2] == '(': runningsum += 1
  entities.append(vec)

def ReadAllLines(file):
  linevec = []
  f = open(file, 'rU')
  for line in f:
    linevec.append(line.strip())
  f.close()
  return linevec

def GetAllSentences(linevec):
  sentencevec = []
  sentence= ''
  for lineindex in range(len(linevec)):
    line = linevec[lineindex].strip()
    if line == '':
      if len(sentence) > 0: sentencevec.append(sentence)
      sentence = ''
    else: sentence += line
      
  if sentence != '': sentencevec.append(sentence)
  return sentencevec
  
def GetConstituents(sentencevec):
  lineindex = 0
  for sentence in sentencevec:
    GetEntities(lineindex, sentence)
    lineindex += 1
  
def PrintEntities():
  for entityvec in entities:
    for item in entityvec:
      print item

def TestIsValid():
  print IsValid('a b')
  print IsValid('(a b)')
  print IsValid('((a)b')
  print IsValid(')(')
  print IsValid('(NP [26.001] (NNP LONDON) (NNP 1996-08-30))')
      
def TestGetSequence():
  print GetSequence('(NNP LONDON)')
  print GetSequence('(NNP 1996-08-30)')
  print GetSequence('(NP [26.001] (NNP LONDON) (NNP 1996-08-30))')
  
def GetMultiTokenEntities(file):
  f = open(file, 'rU')
  linevec = f.readlines()
  lenlinevec = len(linevec)
  f.close()
  
  vec = []
  multitokenentity = ''
  prevtag = ''
  isEntitySeen = False
  
  for lineindex in range(lenlinevec):
    if linevec[lineindex].strip() == '':
      if multitokenentity != '': vec.append(multitokenentity)
      if isEntitySeen: trueentities.append(vec)
      
      prevtag = ''
      vec = []
      multitokenentity = ''
      isEntitySeen = False
    else:
      isEntitySeen = True
      splits = linevec[lineindex].strip().split()
      if splits[-1][0] == 'I':
        if prevtag[0] == 'B': multitokenentity = linevec[lineindex-1].strip().split()[0]
        multitokenentity = multitokenentity + ' ' + splits[0]
      elif multitokenentity != '': 
        vec.append(multitokenentity)
        multitokenentity = ''

      prevtag = splits[-1]
      
  if multitokenentity != '': vec.append(multitokenentity)
  if isEntitySeen: trueentities.append(vec)
      
def PrintTrueEntities():
  for trueentityvec in trueentities:
    if len(trueentityvec) == 0: print '[]'
    for trueentity in trueentityvec:
      print trueentity

def GetRecall():
  numNonEmptySentences = len(trueentities)
  totalTrueEntities = 0
  numTrueEntitiesFound = 0
  for index in range(numNonEmptySentences):
    for trueentity in trueentities[index]:
      totalTrueEntities += 1
      if trueentity in entities[index]: numTrueEntitiesFound += 1
      else: print index, trueentity, entities[index]
  
  recall = float(numTrueEntitiesFound) / float(totalTrueEntities)
  print 'numNonEmptySentences:', numNonEmptySentences, 'totalTrueEntities:', totalTrueEntities, 'numTrueEntitiesFound:', numTrueEntitiesFound, 'recall:', recall
  return recall
  
def main():
  BuildTransitionMatrix()
  #linevec = ReadAllLines('debug.txt')
  linevec = ReadAllLines('deliverable3constituentparse.txt')
  sentencevec = GetAllSentences(linevec)
  GetConstituents(sentencevec)  
  #PrintEntities()
  #GetMultiTokenEntities('debug2.txt')
  GetMultiTokenEntities('eng.testamodified.out')  
  #PrintTrueEntities()
  GetRecall()
  
if __name__ == '__main__':
  main()