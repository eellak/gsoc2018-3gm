import distance
import sys
import glob
import os
import multiprocessing

threshold = 3
output_dir = sys.argv[1]

os.chdir(output_dir)
filelist = glob.glob('*.txt')


def fix_file(filename):
    print(filename)
    with open(filename, 'r') as f:
        lines = f.read().splitlines()

    result = []
    for line in lines:
        tmp = line.split(' ')
        for i, x in enumerate(tmp):
            for w in words:
                x = x.replace('|', 'Ι')
                if ' ' not in x and distance.levenshtein(x, w) <= threshold:
                    tmp[i] = w
                elif x == 'ΠΡΟΕΔΡ|ΚΟ':
                    tmp[i] = 'ΠΡΟΕΔΡΙΚΟ'
                elif x in ['ΔίΑΤΑΓΜΑ', 'Δ|ΑΤΑΓΜΑ']:
                    tmp[i] = 'ΔΙΑΤΑΓΜΑ'
                elif len(x) <= 3 and 'ΥΠ' in x:
                    tmp[i] = 'ΥΠ’'
                tmp[i] = tmp[i].replace('|', 'Ι')

        result.append(' '.join(tmp) + '\n')

    with open(filename, 'w') as f:
        for r in result:
            f.write(r)


words = [
    'ΝΟΜΟΣ',
    'ΔΙΑΤΑΓΜΑ'
    'ΠΡΟΕΔΡΙΚΟ',
    'ΚΟΙΝΗ',
    'ΥΠΟΥΡΓΙΚΗ',
    'ΑΠΟΦΑΣΗ',
    'ΝΟΜΟΘΕΤΙΚΟ',
    'ΑΡΙΘΜ.'
]

pool = multiprocessing.Pool(5)
pool.map(fix_file, filelist)
