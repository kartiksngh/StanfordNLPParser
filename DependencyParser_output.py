import numpy as np

transitionprob = np.zeros((1, 1))
postags = {}
EPSILON = 1e-9

def IsLineWellFormed(line):
  if line.strip() == '': return False
  return True

def GetTag(line):
  tag = line.split('\t')[5]
  # if not tag[:1].isalpha(): return ''
  # if not tag[-1:].isalpha(): tag = tag[:-1]
  return tag
  
def GetListofPOStags(file):
  global postags
  
  f = open(file, 'rU')
  postags['ROOT'] = 0
  for line in f:
    if not IsLineWellFormed(line): continue
    tag = GetTag(line)
    if tag != '' and tag not in postags: postags[tag] = len(postags)

  f.close()
  
def UpdateTransitionCounts(sentencevec):
  global transitionprob
  dict = {}

  lensentencevec = len(sentencevec)
  for sentenceindex in range(lensentencevec):
    tag = GetTag(sentencevec[sentenceindex])
    if tag != '': 
      tokenindex = sentencevec[sentenceindex].split()[0]
      if tokenindex.isdigit(): 
        tokenindex = int(tokenindex)
        dict[tokenindex] = tag

  for sentenceindex in range(lensentencevec):
    tag = GetTag(sentencevec[sentenceindex])
    if tag != '': 
      partokenindex = sentencevec[sentenceindex].split()[9]
      if partokenindex.isdigit(): 
        partokenindex = int(partokenindex)
        if partokenindex == 0 or partokenindex in dict:
          if partokenindex > 0: partag = dict[partokenindex]
          else: partag = 'ROOT'
          partagid = postags[partag]
          tagid = postags[tag]
          transitionprob[partagid, tagid] += 1
  
def ComputeLikelihood(sentencevec):
  lensentencevec = len(sentencevec)
  dict = {}

  lensentencevec = len(sentencevec)
  for sentenceindex in range(lensentencevec):
    tag = GetTag(sentencevec[sentenceindex])
    if tag != '': 
      tokenindex = sentencevec[sentenceindex].split()[0]
      if tokenindex.isdigit(): 
        tokenindex = int(tokenindex)
        dict[tokenindex] = tag

  retprob = 1.0
  for sentenceindex in range(lensentencevec):
    tag = GetTag(sentencevec[sentenceindex])
    if tag != '': 
      partokenindex = sentencevec[sentenceindex].split()[9]
      if partokenindex.isdigit(): 
        partokenindex = int(partokenindex)
        if partokenindex == 0 or partokenindex in dict:
          if partokenindex > 0: partag = dict[partokenindex]
          else: partag = 'ROOT'
          partagid = postags[partag]
          tagid = postags[tag]
          retprob *= transitionprob[partagid, tagid]
          print 'p(' + tag + '|' + partag + ')=' + str(transitionprob[partagid, tagid])

  print 'Likelihood='+str(retprob)
  return retprob
  
def ComputeTransitionProbabilities(file):
  global transitionprob
  transitionprob = np.zeros((len(postags), len(postags)))

  f = open(file, 'rU')
  linevec = f.readlines()
  lenlinevec = len(linevec)
  f.close()

  sentence = []

  for lineindex in range(lenlinevec):
    if not IsLineWellFormed(linevec[lineindex]): 
      if len(sentence) > 0: UpdateTransitionCounts(sentence)
      sentence = []
    else: sentence.append(linevec[lineindex])

  if len(sentence) > 0: UpdateTransitionCounts(sentence)

  for tag in postags:
    denominator = np.sum(transitionprob[postags[tag],:])
    if denominator < EPSILON: denominator = 1 
    transitionprob[postags[tag], :] /= denominator
    
def PrintTransitionProbabilities(tag):
  print 'Transition Probabilities for tag:' + tag
  for tag2 in postags: print 'transition from %s to %s: %6.6f'%(tag, tag2, transitionprob[postags[tag], postags[tag2]])
  print ''
  
def main():
  GetListofPOStags('CoNLL2009-ST-English-development.txt')
  ComputeTransitionProbabilities('CoNLL2009-ST-English-development.txt')
  PrintTransitionProbabilities('NN')
  PrintTransitionProbabilities('VB')
  
  sentence = []
  sentence.append('1	It	it	it	PRP	PRP	_	_	2	2	SBJ	SBJ	_	_	A1')
  sentence.append('2	should	should	should	MD	MD	_	_	0	0	ROOT	ROOT	_	_	AM-MOD')
  sentence.append('3	run	run	run	VB	VB	_	_	2	2	VC	VC	Y	run.01	_')
  sentence.append('4	forever	forever	forever	RB	RB	_	_	3	3	TMP	TMP	_	_	AM-TMP')
  sentence.append('5	.	.	.	.	.	_	_	2	2	P	P	_	_	_')
  
  ComputeLikelihood(sentence)
  
if __name__ == '__main__':
  main()