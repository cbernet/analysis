import math

def deltaR2( e1, p1, e2=None, p2=None):
    """Take either 4 arguments (theta,phi, theta,phi) or two objects that have 'theta', 'phi' methods)"""
    if (e2 == None and p2 == None):
        return deltaR2(e1.theta(),e1.phi(), p1.theta(), p1.phi())
    de = e1 - e2
    dp = deltaPhi(p1, p2)
    return de*de + dp*dp


def deltaR( *args ):
    return math.sqrt( deltaR2(*args) )


def deltaPhi( p1, p2):
    '''Computes delta phi, handling periodic limit conditions.'''
    res = p1 - p2
    while res > math.pi:
        res -= 2*math.pi
    while res < -math.pi:
        res += 2*math.pi
    return res


def matchObjectCollection2 ( objects, matchCollection, deltaRMax = 0.3 ):
    '''Univoque association of an element from matchCollection to an element of objects.
    Reco and Gen objects get the "matched" attribute, true is they are re part of a matched tulpe.
    By default, the matching is true only if delta R is smaller than 0.3.
    '''
    
    pairs = {}
    if len(objects)==0:
            return pairs
    if len(matchCollection)==0:
            return dict( zip(objects, [None]*len(objects)) )
    # build all possible combinations
    allPairs = [(deltaR2 (object.theta(), object.phi(), match.theta(), match.phi()), (object, match)) for object in objects for match in matchCollection]
    allPairs.sort ()

    # to flag already matched objects
    # FIXME this variable remains appended to the object, I do not like it
    for object in objects:
        object.matched = False
    for match in matchCollection:
        match.matched = False
    
    deltaR2Max = deltaRMax * deltaRMax
    for dR2, (object, match) in allPairs:
	if dR2 > deltaR2Max:
		break
        if dR2 < deltaR2Max and object.matched == False and match.matched == False:
            object.matched = True
            match.matched = True
            pairs[object] = match
    
    for object in objects:
       if object.matched == False:
	   pairs[object] = None

    return pairs
    # by now, the matched attribute remains in the objects, for future usage
    # one could remove it with delattr (object, attrname)

