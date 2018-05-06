import re
import numpy as np


def edit_distance(str1, str2, weight=lambda s1, s2, i, j: 0.75 if s1[i-1] == ' ' or s2[j-1] == ' ' else 1):
    m, n = len(str1), len(str2)
    dp = [[0 for x in range(n+1)] for x in range(m+1)]

    for i in range(m+1):
        for j in range(n+1):

            if i == 0:
                dp[i][j] = j

            elif j == 0:
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]

            else:
                dp[i][j] = weight(str1, str2, i, j) + min(dp[i][j-1],
                                                          dp[i-1][j],
                                                          dp[i-1][j-1])
    return dp[m][n]


intonations = {
    'ά': 'α',
    'έ': 'ε',
    'ί': 'ι',
    'ό': 'ο',
    'ύ': 'υ',
    'ή': 'η',
    'ώ': 'ω'
}


def normalize_word(s):
    s = s.strip('-')
    global intonations
    for key, val in intonations.items():
        s = s.replace(key, val)
    return s


def normalize(x, l=None, r=None):
    x = x.astype('float64')
    if l == None:
        l = np.min(x)
    if r == None:
        r = np.max(x)
    if r != l:
        return (x - l) / (r - l)
    else:
        return np.zeros(x.shape)
