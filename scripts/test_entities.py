##############################################
# This is a simple file used for development
# regarding feature extraction. Our goal is to enhance the functionalites
# of the entities.py using regular expressions. Once we find the proper
# one and we are happy with the results we will integrate changes
# the entites file
###############################################


import re
from typing import Generator
import string


if __name__ == "__main__":

    # YOUR FILE HERE
    with open('corpus_AAP.txt', 'r') as myfile:
        data = myfile.read()

    # Very simple preprocessing for txt
    re.sub('-\n', '', data)
    re.sub('/\n', '/ ', data)

    # URLS
    urls = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', data)
    print("Urls: ", len(urls))

    # CPC
    cpc = re.findall('CPC .+[0-9]', data)
    print("CPC: ", cpc)

    # CPV code mainly found in YODD
    cpv = re.findall('[0-9]{8}-[0-9]', data)
    print("CPV: ", cpv)

    # POEPLE

    military_personel = re.findall('ΣΑ [0-9]{3}/[0-9]{3}/[0-9]{2}', data)
    print("Military personnel: ", military_personel)
    id_numbers = re.findall(
        'Α.Δ.Τ. [Α-Ωα-ω]{0,2} [0-9]{6}|Α.Δ.Τ.: [Α-Ωα-ω]{0,2}-[0-9]{6}|Α.Δ.Τ. [Α-Ωα-ω]{0,2}[0-9]{6}|ΑΔΤ Α[Α-Ωα-ω]{0,2}[0-9]{6}', data)
    print("ID numbers: ",  len(id_numbers))

    # IBAN accounts
    ibans = re.findall(
        '^[A-Z]{2}(?:[ ]?[0-9]){18,20}$|[A-Z]{2} [0-9]{25}', data)
    print("IBAN numbers: ", len(ibans))

    # TVA tax
    TVA = re.findall('Φ.Π.Α. [0-9]{1,2}%', data)
    print("TVA rates: ", TVA)
    e_mails = re.findall(r'[\w\.-]+@[\w\.-]+', data)

    # E-MAILS
    print("Emails :", len(e_mails))
    phone_numbers = re.findall(
        'τηλ. .+[0-9]|τηλ: .+[0-9]|tel: .+[0-9]|τηλ.: .+[0-9]|Τηλέφωνο: .+[0-9]', data)

    # Phone numbers
    print("Phone numbers: ", len(phone_numbers))
    post_codes = re.findall('ΤΚ: [0-9]{3} [0-9]{2}', data)
    print("Post codes: ", len(post_codes))

    # exact times can be found in issues like YODD documenting mainly
    # when an assebly or meeting took place
    exact_times = re.findall(
        '[0-9]{2}:[0-9]{2} π.μ.|[0-9]{2}:[0-9]{2} μ.μ.|[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}', data)
    print("Exact time: ", len(exact_times))

    # money YODD many variations
    money = re.findall(
        r'[$€£]{1}\d+\.?\d{0,2}|\d+\.\d+\,?\d{0,2} [$€£]{1}|\d+\.\d+\,?\d{0,2} EUR|\d+\.\d+\,?\d{0,2} ευρώ', data)
    print("Monetary amounts: ", len(money))

    # Other issues (simple heurestic needs work finds around half)
    issues = re.findall(
        'ΦΕΚ [0-9]{1,4}[/.-]{0,1}[Α-Ωα-ω.΄\s][/.-]{0,1}.+[0-9]|\(ΦΕΚ [0-9]{1,4}[/.-]{0,1}[Α-Ωα-ω.΄\s][/.-]{0,1}.+[0-9]', data)
    #print("Issues mentioned: ",  issues)
    print("number: ", len(issues))
    # Public work using code http://epde.gr/liferay-portal/documents/10181/4692465/%CE%95%CE%93%CE%A7%CE%95%CE%99%CE%A1%CE%99%CE%94%CE%99%CE%9F+%CE%9B%CE%95%CE%99%CE%A4%CE%9F%CE%A5%CE%A1%CE%93%CE%99%CE%A9%CE%9D/d9ad1db6-bfb7-42ce-8fba-74666568a083
    publc_works = re.findall('[0-9]{4}[Α-Ωα-ω]{2}[0-9]{8}', data)
    print("Public works: ", len(publc_works))

    # find NUTS european regions https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:02003R1059-20180118&qid=1519136585935
    NUTS_reg = re.findall('NUTS: [A-Z]{2}[0-9]{1,3}', data)
    print("NUTS_reg: ", len(NUTS_reg))

    # find KAEK  code basic heurestic  http://www.ktimatologio.gr/aboutus/Documents/Pages/33/LqYyvusGBh2JgNdw/diad_entaksis_praxis_efarmogis_1.pdf
    kaek = re.findall('ΚΑΕΚ-[0-9]{12}|ΚΑΕΚ [0-9]{12}', data)
    #print("KAEK: ", kaek)
    print("KAEK: ", len(kaek))

    # FIND METRICS -Distances
    # Scale
    scales = re.findall('1:[0-9]{1,10}', data)
    print("Scales: ", len(scales))
    # meters
    meters = re.findall('\d+m', data)
    print("Meters : ", len(meters))
    kilometers = re.findall('\-?\d+\,\d+ km', data)
    print("KiloMeters : ", kilometers)
