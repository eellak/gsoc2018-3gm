import re
import numpy as np
from datetime import date, datetime, time
import urllib
from urllib.request import Request
import shutil
import urllib.parse
import os
import json
import collections
import datetime
import re

# Helper class that defines useful formatting and file handling functions
class Helper:

    # Initialize empty dict for saving compiled regex objects
    date_patterns = {}
    camel_case_patteren = re.compile("([α-ω])([Α-Ω])")
    final_s_pattern = re.compile("(ς)([Α-Ωα-ωά-ώ])")
    upper_s_pattern = re.compile("(Σ)(ΚΑΙ)")
    u_pattern = re.compile("(ύ)(και)")

    # Converts upper / lowercase text with possible ambiguous latin characters to a fully greek uppercase word with
    # no accents.
    # @todo: Use regex or other way to speed up
    @staticmethod
    def normalize_greek_name(name):
        name = name.replace(",", " ")
        # α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, ο, π, ρ, σ, τ, υ, φ, χ, ψ, ω
        name = name.replace("ΐ", "ϊ").upper()

        # Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
        # A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

        replace_chars = {'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ϊ': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ϋ': 'Υ', 'Ώ': 'Ω',
                         'A': 'Α', 'B': 'Β', 'E': 'Ε', 'H': 'Η', 'I': 'Ι', 'K': 'Κ', 'M': 'Μ', 'N': 'Ν', 'O': 'Ο',
                         'T': 'Τ', 'X': 'Χ', 'Y': 'Υ', 'Z': 'Ζ'}

        for char in replace_chars:
            name = name.replace(char, replace_chars[char])

        # Remove characters that should not belong in the name
        name = re.sub("[^Α-ΩΪΫ\s]+", "", name)

        return ' '.join(name.split())

    @staticmethod
    # Performs an http request and returns the response
    def get_url_contents(link, content_type=''):
        try:
            with urllib.request.urlopen(link, data=None, timeout=240) as url:
                response = url.read().decode("utf-8")

                if content_type == 'json':
                    s = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(response)
                    return s
                else:
                    return response

        except urllib.error.HTTPError as e:
            print(e)
            return {}
        except urllib.error.URLError as e:
            print(e)
            return {}

    @staticmethod
    def download(url, file_name= None, folder = os.getcwd()):
        @staticmethod
        def get_file_name(open_request):
            if 'Content-Disposition' in open_request.info():
                # If the response has Content-Disposition, try to get filename from it
                cd = dict(map(
                    lambda x: x.strip().split('=') if '=' in x else (x.strip(), ''),
                    open_request.info()['Content-Disposition'].split(';')))
                if 'filename' in cd:
                    filename = cd['filename'].strip("\"'")
                    if filename:
                        return filename

            # If no filename was found above, parse it out of the final URL.
            return os.path.basename(urllib.parse.urlsplit(open_request.url)[2])

        request = Request(url)
        r = urllib.request.urlopen(request)

        try:
            if not file_name:
                file_name = get_file_name(r)

            file_path = os.path.join(folder, file_name)

            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r, f)
        finally:
            r.close()
            return True

    # Clears wikipedia annotations from a string
    @staticmethod
    def clear_annotations(text):
        return re.sub('\[[0-9]+\]', '', text)

    # Converts a textual date to a unix timestamp
    @staticmethod
    def date_to_unix_timestamp(date, lang='el'):
        if lang == 'el':
            d = 0
            m = 1
            y = 2
            months = {'Ιανουαρίου': 1, 'Φεβρουαρίου': 2, 'Μαρτίου': 3, 'Απριλίου': 4, 'Μαΐου': 5, 'Ιουνίου': 6,
                      'Ιουλίου': 7, 'Αυγούστου': 8, 'Σεπτεμβρίου': 9, 'Οκτωβρίου': 10, 'Νοεμβρίου': 11,
                      'Δεκεμβρίου': 12, 'Μαίου': 5}
            text_month = False
            separator = " "
            pattern = "Α-Ωα-ωά-ώ"

        if re.match('[0-9]{1,2} [' + pattern + ']{1,} [0-9]{4,4}', date):
            separator = " "
            text_month = True
        elif re.match('[0-9]{1,2}-[0-9]{1,2}-[0-9]{,4}', date):
            separator = "-"
        elif re.match('[0-9]{1,2}/[0-9]{1,2}/[0-9]{,4}', date):
            separator = "/"
        elif re.match('[0-9]{4,4}', date):
            # Remove non numeric elements from string
            return datetime.datetime(year=int(re.search("^\d{4,4}", date).group(0)), month=1, day=1)
        else:
            return 0
        date = Helper.clear_annotations(date)
        parts = date.split(separator)

        if d < len(parts):
            day = parts[d]
        else:
            day = 1

        if m < len(parts) and text_month:
            month = months[parts[m]]
        elif m < len(parts):
            month = parts[m]
        else:
            month = 1

        if y < len(parts):
            # Remove non numeric elements from string
            year = re.search("^\d{4,4}", parts[y]).group(0)
        else:
            return 0

        return datetime.datetime(year=int(year), month=int(month), day=int(day))

    # Returns a compiled regex object to find dates in text
    @staticmethod
    def date_match(year= 0):

        if not year in Helper.date_patterns:
            operator = str(year) if year != 0 else r"\d{4,4}"
            date_pattern = "\w+,\s?\d{1,2}\s+?\w+\s+" + "{year}".format(year=operator)
            Helper.date_patterns[year] = re.compile(date_pattern)

        return Helper.date_patterns[year]

    # Formats roles extracted from pdfs. Specifically, splits separate words that are stuck together
    @staticmethod
    def format_role(text):
        parts = text.split(" ")

        final_word = ""
        for part in parts:
            split = Helper.camel_case_patteren.sub(r'\1 \2', part).split()

            # If no TitleCase or camelCase was found then we address the possibility of a final s inside a word
            if len(split) == 1:
                split = Helper.final_s_pattern.sub(r'\1 \2', part).split()

            # If no TitleCase or camelCase was found then we address the possibility of a final s inside a word
            if len(split) == 1:
                split = Helper.u_pattern.sub(r'\1 \2', part).split()

            # If no TitleCase or camelCase was found then we address the possibility of a final s inside a word
            if len(split) == 1:
                split = Helper.upper_s_pattern.sub(r'\1 \2', part).split()

            for word in split:
                final_word += word + " "

        # Returns the word without trailing spaces
        return Helper.normalize_greek_name(final_word.strip())

    # Finds all occurences of a substring in a string
    # @return The indexes of all matched substrings.
    @staticmethod
    def find_all(key, string):
        matches = []
        start = 0
        searching = True
        while searching:
            index = string.find(key, start)

            if index == -1:
                searching = False
            else:
                matches.append(index)
                start = index + 1

        return matches

    # Orders a list of dicts by a value inside the dicts
    @staticmethod
    def qsort_by_dict_value(inlist, dict_key):
        if inlist == []:
            return []
        else:
            pivot = inlist[0]
            lesser = Helper.qsort_by_dict_value([x for x in inlist[1:] if x[dict_key] < pivot[dict_key]], dict_key)
            greater = Helper.qsort_by_dict_value([x for x in inlist[1:] if x[dict_key] >= pivot[dict_key]], dict_key)
            return lesser + [pivot] + greater

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

MONTHS_PREFIXES = {
	'Ιανουαρίο': 1,
	'Φεβρουαρίο': 2,
	'Μαρτίο': 3,
	'Απριλίο': 4,
	'Μαΐο': 5,
	'Ιουνίο': 6,
	'Ιουλίο': 7,
	'Αυγούστο': 8,
	'Σεπτέμβριο': 9,
	'Οκτωβρίο': 10,
	'Νοεμβρίο': 11,
	'Δεκεμβρίο': 12,
}

def string_to_date(d):
    full, day, month, year = d

    for m in MONTHS_PREFIXES.keys():
        if month == m + 'υ':
            month = MONTHS_PREFIXES[m]
            break

    return date(int(year), month, int(day))
