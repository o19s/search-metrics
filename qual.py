def rr(grades, n=0):
    """
    Reciprocal Rank is the first step in calculating Mean Reciprocal Rank
    https://en.wikipedia.org/wiki/Mean_reciprocal_rank

    This is a measure for how far down a results list a user has to go to find the first relevant document. A document
    is relevant if its grade is > 0.

    :param grades: A list of numbers indicating how relevant the corresponding document was at that position in the list
    :param n: A number indicating how far down the list to go before giving up
    :return: A number between 1.0 and 0.0 indicating how far up the list the relevant document was found
    """
    if n == 0:
        n = len(grades)
    n = min(n, len(grades))
    for i in range(0, n):
        if grades[i] > 0.0:
            return float(1.0 / (i + 1.0))
    return 0.0


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

    :param grades: A list of numbers indicating how relevant the corresponding document was at that position in the list
    :param n: A number indicating the maximum number of positions to consider
    :param max_grade: A float indicating the maximum grade a doc can get
    :return: A number between 1.0 and 0.0 indicating how good the results were (higher is better)
    """
    if n == 0:
        n = len(grades)
    n = min(n, len(grades))
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


def damage(results1, results2, at=10):
    """ How "damaging" could the change from results1 -> results2 be?

        (results1, results2 are an array of document identifiers)

        For each result in result1,
            Is the result in result2[:at]
                If so, how far has it moved?
            If not,
                Consider it a move of at+1

            damage += discount(idx) * moveDist
                """

    from math import log

    def discount(idx):
        return 1.0 / log(idx + 2)

    idx = 0
    dmg = 0.0

    if len(results1) < at:
        at = len(results1)

    for result in results1[:at]:
        movedToIdx = at + 1 # out of the window
        if result in results2:
            movedToIdx = results2.index(result)
        moveDist = abs(movedToIdx - idx)
        dmg += discount(idx) * moveDist
        idx += 1

    return dmg


def dcg(grades, n=0):
    """
    Discounted Cumulative Gain
    https://en.wikipedia.org/wiki/Discounted_cumulative_gain#Discounted_Cumulative_Gain

    A metric that varies directly with the average judgement of the result set, placing more weight toward the top.

    :param grades: A list of numbers indicating how relevant the corresponding document was at that position in the list
    :param n: A number indicating the maximum number of positions to consider
    :return: A number >= 0.0 indicating how the result set should be judged
    """
    if n == 0:
        n = len(grades)
    n = min(n, len(grades))
    from math import log
    dcg = 0
    for i in range(0,n):
        r = i + 1
        dcg += grades[i] / log((r + 1), 2.0)
    return dcg

def dcgWConfs(grades, confs, midGrade=2.0, n=0):
    if len(grades) != len(confs):
        raise ValueError("dcgWConfs needs same number of grades as confs")
    if n == 0:
        n = len(grades)
    n = min(n, len(grades))
    from math import log
    dcg = 0
    for i in range(0,n):
        # Conf adjusted grade, if low confidence we dont have good information
        # on the 'true' grade, so it gets pushed to a 2. The true DCG is a bell curve...
        # This is similar to the RankSVM unbiased technique in Joachim's paper
        r = (i + 1)
        confAdjustedGrade = midGrade + confs[i] * (grades[i] - midGrade)
        print("Grade %s Conf Adjusted %s" % (grades[i], confAdjustedGrade))
        dcg += (confAdjustedGrade / log((r + 1), 2.0))
    return dcg


def ndcg(grades, n=0):
    """
    Normalized Discounted Cumulative Gain
    https://en.wikipedia.org/wiki/Discounted_cumulative_gain#Normalized_DCG

    A metric that considers the sort order of the rated documents against an ideal sort order with higher rated docs
    at the top and lower rated docs at the bottom.

    :param grades: A list of numbers indicating how relevant the corresponding document was at that position in the list
    :param n: A number indicating the maximum number of positions to consider
    :return: A number between 1.0 and 0.0 indicating how close to the ideal ordering the docs are (higher is better)
    """
    _dcg = dcg(grades, n=n)
    _idcg = dcg(sorted(grades, reverse=True), n=n)
    if _idcg > 0.0:
        return _dcg / _idcg
    else:
        return 0.0
