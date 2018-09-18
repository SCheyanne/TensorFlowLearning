 # encoding: utf-8
__author__ = 's00416283'

from numpy import *
import feedparser

def textParse(bigString):
    import re
    listOfTokens = re.split(r'\w*', bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]


def createVocabList(dataSet):
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)
    return list(vocabSet)

# 词袋模式
def bagOfWords2Vec(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
        else:
            print "the word: %s is not in my vocabulary" %word
    return returnVec

# trainCategory = label
def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numwords = len(trainMatrix[0])
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    p0Num = ones(numwords)
    p1Num = ones(numwords)
    p0Denom = 2.0
    p1Denom = 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = log(p1Num/p1Denom)
    p0Vect = log(p0Num/p0Denom)
    return p0Vect, p1Vect, pAbusive


def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    p0 = sum(vec2Classify * p0Vec) + log(1 - pClass1)
    p1 = sum(vec2Classify * p1Vec) + log(pClass1)
    if p0 > p1:
        return 0
    else:
        return 1

def calMostFreq(vocabList, fullText):
    import operator
    freqDict = {}
    for token in vocabList:
        freqDict[token] = fullText.count(token)
    sortedFreq = sorted(freqDict.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedFreq[:30]


def localWords(feed1, feed0):
    docList = []; classList = []; fullText = []
    minLen = min(len(feed1['entries']), len(feed0['entries']))
    for i in range(25):
        wordList = textParse(feed1['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(feed0['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = createVocabList(docList)
    top30Freq = calMostFreq(vocabList, fullText)
    for pairW in top30Freq:
        if pairW[0] in vocabList:
            vocabList.remove(pairW[0])
    trainingSet = range(2 * minLen)
    testSet = []
    for i in range(20):
        readIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[readIndex])
        del(trainingSet[readIndex])
    trainMat = []
    trainClass = []
    for i in trainingSet:
        trainMat.append(bagOfWords2Vec(vocabList, docList[i]))
        trainClass.append(classList[i])
    p0V, p1V, pAb = trainNB0(trainMat, trainClass)
    ErrorCount = 0

    for i in testSet:
        result = classifyNB(bagOfWords2Vec(vocabList, docList[i]), p0V, p1V, pAb)
        if result != classList[i]:
            ++ErrorCount
    print "the error rate is:", float(ErrorCount)/len(testSet)
    return p0V, p1V, vocabList


def getTopWords(ny, sy):
    import operator
    p0V, p1V, vocabList = localWords(ny, sy)
    topNY = []; topSY = []
    for i in range(len(p0V)):
        if p0V[i] > -6.0: topSY.append((vocabList[i], p0V[i]))
        if p1V[i] > -6.0: topNY.append((vocabList[i], p1V[i]))
    sortedSY = sorted(topSY, key=lambda pair: pair[1], reverse=True)
    sortedNY = sorted(topNY, key=lambda pair: pair[1], reverse=True)
    print p0V, p1V
    print "**************************** sy ********************"
    for item in sortedSY:
        print item[0]
    print "**************************** ny ********************"
    for item in sortedNY:
        print item[0]


if __name__ == '__main__':
    # testingNB()
    # spamTest(）

    ny = feedparser.parse('https://ieeexplore.ieee.org/rss/TOC41.XML')
    sy = feedparser.parse('http://www.engadget.com/rss.xml')
    getTopWords(ny, sy)
