def gain(grade, maxGrade=4.0):
    return (2**grade - 1.0) / (2 ** maxGrade)


#def gain(grade, maxGrade=4.0):
#    return (grade / maxGrade)


def err(grades, n=0):
    """ Algorithm from: http://olivier.chapelle.cc/pub/err.pdf

    Gets at the probability a user will find something useful before
    getting annoyed

    Useful stuff has a probability near 1 of satisfying the user.
    In the cascading model As the user scans down. If something has a
    near 1 probability of satisfying user near the top. If something near top has

    """
    if n > len(grades):
        raise ValueError("err@%s cannot be calculated with %s grades" % (n, len(grades)))
    if n == 0:
        n = len(grades)
    ERR = 0
    trustBank = 1 # In a way the users "trustBank"
    for i in range(0,n):
        r = i + 1
        pThisUseful = gain(grades[i], maxGrade=4.0)
        discThisUseful = pThisUseful / r # How much of this users trustBank
                                         # you're about to exhaust
                                         # So good stuff at r=1, less trustBank
                                         # Bad stuff, at r=1, trustBank reduced a lot

        ERR += trustBank * discThisUseful # Sum the users remaining trustBank at pos'n r
        trustBank *= (1 - pThisUseful) # Reduce users trustBank
        # print("ERR@%s trust? %s trustBank? %s" % (r, ERR, trustBank))
    return ERR


def dcg(grades, n=0):
    if n > len(grades):
        raise ValueError("dcg@%s cannot be calculated with %s grades" % (n, len(grades)))
    if n == 0:
        n = len(grades)
    from math import log
    dcg = 0
    for i in range(0,n):
        r = i + 1
        dcg += grades[i] / log((r + 1), 2.0)
    return dcg


def ndcg(grades, n=0):
    return dcg(grades, n=n) / dcg(sorted(grades, reverse=True), n=n)
