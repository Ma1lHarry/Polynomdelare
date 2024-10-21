
import os

def prettyNum(fNum):
    #Removes the decimal part if not needed
    if fNum % 1 == 0:
        return str(int(fNum))
    else:
        return str(fNum)

class Monom:
    def __init__(self,k, deg):
        self.k = k
        self.deg = deg

    def __str__(self):
        if self.deg == 0:
            return str(self.k)
        elif self.deg == 1:
            return str(self.k) + "x"
        else:
            return str(self.k) + "x^" + prettyNum(self.deg)

class C:
    def __init__(self, re, im):
        self.a = re
        self.b = im
    
    def __str__(self):
        if self.b == 0 and self.a == 0:
            return "0"
        #Don't return complex part if zero
        if self.b == 0:
            return prettyNum(self.a)
        #Return just complex part if real is zero
        if self.a == 0:
            return prettyNum(self.b) + "i"
        #If mixed:
        if self.b >= 0:
            #print("+C.str returning: " + str(self.a) + "+" + str(self.b) + "i")
            return "(" + prettyNum(self.a) + "+" + prettyNum(self.b) + "i)"
        else:
            #Negative num returns minussign automaticly
            return "(" + prettyNum(self.a) +  prettyNum(self.b) + "i)"

def splitPolynom(strPoly, verbose):
    polyTerms = []#List with parsed terms to be returned
    #First seperate into terms by splitting at + and -
    parts = []
    separators = ['+', '-']
    lastcut = 0
    for i in range(0, len(strPoly)):
        if strPoly[i] in separators:
            parts.append(strPoly[lastcut:i])
            lastcut = i
    parts.append(strPoly[lastcut:len(strPoly)])

    #Then parse eatch terms into k and deg
    count = 0
    for part in parts:
        if "x" in part:
            #There is a x in the term
            splitPart = part.split("^")
            if len(splitPart) > 1:
                #if it was split, first part will be NNx, k is everything but last char
                #Uses helperfunction to convert empty or negative str to int
                #polyTerms.append({"k":numToStr(splitPart[0].split("x")[0]),"deg":int(splitPart[1])})
                polyTerms.append(Monom(numToStr(splitPart[0].split("x")[0]),int(splitPart[1])))
            else:
                #It was not split, just x, meaning kx^1
                #Uses helperfunction to parse k, which might be empty or negative
                #polyTerms.append({"k":numToStr(splitPart[0].split("x")[0]),"deg":1})
                polyTerms.append(Monom(numToStr(splitPart[0].split("x")[0]), 1))
        else:
            #There is no x, either its a begining -
            if len(part) == 0:
                continue;
            else:
                #Or just constant
                #polyTerms.append({"k":int(numToStr(part)),"deg":0})
                polyTerms.append(Monom(numToStr(part), 0))
        if verbose:
            print(part + " = " + str(polyTerms[count]))
        count += 1
    return polyTerms

def deDup(polynom):
    oldlist = polynom
    tmp = []
    same = []
    while True:
        if len(oldlist) == 0:
            break
        #Pick a deg
        deg = oldlist[0].deg
        #Create an zero monom of that deg
        tmp.append(Monom(C(0,0), deg))
        #Find all monoms in polynom with same deg
        for i in range(0,len(oldlist)):
            if polynom[i].deg == deg:
                #Add monoms with same deg together
                tmp[len(tmp) - 1].k.a += polynom[i].k.a
                tmp[len(tmp) - 1].k.b += polynom[i].k.b
                #Can't delete while looping, remeber and del later
                same.append(polynom[i])
        #Delete the monoms that have been added
        for i in same:
            polynom.remove(i)
        same = [] 
        #Continue 'till nothing remains in oldlist
    return tmp
    
def sort(listofterms):    
    tmp = [] #Where the sorted list will be stored
    #Begin by dedupping terms of same deg
    oldlist = deDup(listofterms)
    bigI = 0
    bigDeg = 0
    while len(oldlist) > 0:
        #Loop through the list to find the highest deg
        bigI = 0
        bigDeg = 0
        for i in range(0, len(oldlist)):
            if oldlist[i].deg >= bigDeg:
                #Remeber index of highest deg
                bigI = i
                bigDeg = oldlist[i].deg
    
        #Add the hightest deg to new list
        tmp.append(oldlist[bigI])
        #Remove the hightest deg from old list
        del(oldlist[bigI])
        #Loop 'till old list is empty
    #Tmp is the ordered list
    return tmp

def divide(nom, denom):
    #Takes to monoms, that may be complex, and divides them
    #First calculate the denometor times complex konjugat
    reDenom = (denom.k.a * denom.k.a) + (denom.k.b * denom.k.b)
    #Then the real part
    re = ((nom.k.a*denom.k.a) + (nom.k.b*denom.k.b))/reDenom
    #Then complex
    im = ((nom.k.b*denom.k.a) - (nom.k.a*denom.k.b))/reDenom
    #Degree is calculated and returned
    return Monom(C(re,im), nom.deg - denom.deg)

def mult(monom,poly):
    tmp = []
    for term in poly:
        #tmp.append({"deg":p["deg"]+ monom["deg"], "k":p["k"]* monom["k"]})
        tmp.append(Monom(C(term.k.a*monom.k.a - (term.k.b * monom.k.b), term.k.a * monom.k.b + (term.k.b * monom.k.a)), term.deg + monom.deg))
    return tmp

def subtract(term1, term2):
    #Expects sorted termlists
    tmp = []

    #Find highest deg
    bigDeg = term1[0].deg
    if term2[0].deg > bigDeg:
        bigDeg = term2[0].deg
    
    #subtract termparts of same deg
    for i in range(0, bigDeg + 1):
        tmp.append(Monom(C(0,0),0)) #append zero monom
        
        #Extract monoms of the same deg
        c1 = -1
        for m in range(0,len(term1)):
            if term1[m].deg == bigDeg - i:
                c1 = m
                break;
        c2 = -1
        for m in range(0,len(term2)):
            if term2[m].deg == bigDeg - i:
                c2 = m
                break;

        #Do the subtraction of the monoms
        if c1 >= 0 and c2 >= 0:
            #Can only subtract if both terms contain same degree
            tmp[i].k = C(term1[c1].k.a - term2[c2].k.a, term1[c1].k.b - term2[c2].k.b)
            tmp[i].deg = bigDeg - i
        elif c1 >= 0:
            #If only present in first term, remains the same in result
            tmp[i].k = term1[c1].k
            tmp[i].deg = bigDeg - i
        elif c2 >= 0:
            #If only present in second term, negative value added to result
            tmp[i].k = C(-term2[c2].k.a, -term2[c2].k.b)
            tmp[i].deg = bigDeg - i
        #If present in neither term, nothing happens
    
    #remove zeroterms
    final = []
    for term in tmp:
        if term.k.a != 0 or term.k.b != 0:
            final.append(term)

    return final

def polyToString(poly):
    if len(poly) == 0:
        return ""
    tmp = ""
    for term in poly:
        if term.k.a == 0 and term.k.b == 0:
            continue
        #positive => join terms with +
        if len(tmp) == 0:
            #Dont begin with +
            tmp += str(term)
        else:
            tmp += "+" + str(term)
    return tmp

def numToStr(strNum):
    #Takes a string that might be negative, empty or complex and returns it as a C
    if len(strNum) == 0:
        #No number before x means k = 1
        return C(1,0)
    if strNum[0] == '-':
        #Number is negative
        if len(strNum) == 1:
            #Just -x, means k = -1 + 0i
            return C(-1,0)
        else:
            #Check if complex
            parts = strNum.split("i")
            if len(parts) == 1:
                #There was no i's
                #Convert all but the minussign, then negate
                return C(-int(parts[0][1:]), 0)
            else:
                #Its complex, everything before the i is k.b
                if len(parts[0]) == 1:
                    #just -i means k = 0 -1i
                    return C(0, -1)
                else:
                    #There is a negative number before i
                    return C(0, -int(parts[0][1:]))

    elif strNum[0] == '+':
        #Number is positive
        if len(strNum) == 1:
            #Just +x, means k = 1 + 0i
            return C(1,0)
        else:
            #Check if complex
            parts = strNum.split("i")
            if len(parts) == 1:
                #There was no i's, k is just real, convert all but plussign
                return C(int(parts[0][1:]), 0)
            else:
                if len(parts[0]) == 1:
                    #Just +i, means k is 0+1i
                    return C(0, 1)
                else:
                    #Its complex, everything before the i is k.b
                    return C(0, int(parts[0][1:]))
    else:
        #Check if complex
            parts = strNum.split("i")
            if len(parts) == 1:
                #There was no i's, k is just real, convert all but plussign
                return C(int(parts[0]), 0)
            else:
                #Its complex
                #If no number in front its 1 * k
                if len(parts[0]) < 1:return C(0, 1)
                else: return C(0, int(parts[0]))
                



os.system('cls')

print("Enter a polynom to be divided in the form of 'x^2+4x+5' without spaces")
#strPoly = "x^4+4x^3+14x^2+36x^1+45"
strPoly = input()
strDenom = input("Enter Denomenator:\n")
#strDenom = "x-i+2"
print("input:" + strPoly)
print("Divided by " + strDenom + "\n")

#Split the strings and decode their mathematical meaning
polyTerms = splitPolynom(strPoly, True)
denomTerms = splitPolynom(strDenom, True)
#Sort the terms by size of deg
polyTerms = sort(polyTerms)
denomTerms = sort(denomTerms)

polycount = 0
kvot = []
tRest = polyTerms

while True:
    if len(tRest) == 0:
        break
    if tRest[0].deg < denomTerms[0].deg:
        break

    #Calculate the kvot
    #print("Divide "+ termToStr(tRest[0]) + " by " + termToStr(denomTerms[0]))
    kvot.append(divide(tRest[0],denomTerms[0]))
    print("\nRound " + str(polycount))
    print("    " + polyToString(kvot))
    print("  -------------------|" + polyToString(denomTerms))
    print("    " + polyToString(tRest))
    tSub = mult(kvot[polycount],denomTerms)
    print("  -(" + polyToString(tSub) + ")")
    tRest = subtract(tRest, tSub)
    print("  ------------")
    print("    " + polyToString(tRest))
    polycount += 1

print("\n\nKvot:" + polyToString(kvot))
print("Rest:" + polyToString(tRest))
