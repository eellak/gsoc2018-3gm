"""
This is a simple file used for development
regarding feature extraction. Our goal is to enhance the functionalites
of the entities.py using regular expressions. Once we find the proper
one and we are happy with the results we will integrate changes
the entites file
"""


import re
from typing import Generator
from collections import Iterable
import string

conditions = ['Εκτός αν', 'αν', 'προϋπόθεση', 'κατά περίπτωση', 'εφόσον', 'εάν',
              'ανεξαρτήτως εάν', 'είναι δυνατόν να', 'τις προϋποθέσεις', 'μόνο εφόσον', 'μετά από', 'ενέχει']

constraints = ['εν όλω', 'εν μέρει', 'αρκεί', 'εκτός από',
               'πρέπει να', 'πλην', 'τουλάχιστον', 'μέχρι', 'το πολύ', 'εκτός','λιγότερο από']

durations = ['επί', 'μέσα στον μήνα', 'μέσα σε', 'εντός ',
             'μέχρι της ίδιας αυτής ημερομηνίας', 'προθεσμία',  'το αργότερο εντός']

days_of_week = ['Δευτέρα', 'Δευτέρας', 'Τρίτη', 'Τρίτης', 'Τετάρτη', 'Τετάρτης',
                'Πέμπτη', 'Πέμπτης', 'Παρασκευή', 'Παρασκευής', 'Σάββατο', 'Σαββάτου', 'Κυριακή',
                'Κυριακής']


# this is a list that will be used to mine the names of courts
# Since these entities can be expressser to more than on grammatical
# case we will have to integrate sufixes. An outline of the courts
# of Greece can be found here: http://www.ministryofjustice.gr/site/el/%CE%9F%CE%A1%CE%93%CE%91%CE%9D%CE%A9%CE%A3%CE%97br%CE%94%CE%99%CE%9A%CE%91%CE%99%CE%9F%CE%A3%CE%A5%CE%9D%CE%97%CE%A3/%CE%9F%CF%81%CE%B3%CE%B1%CE%BD%CF%8C%CE%B3%CF%81%CE%B1%CE%BC%CE%BC%CE%B1%CE%94%CE%B9%CE%BA%CE%B1%CF%83%CF%84%CE%B7%CF%81%CE%AF%CF%89%CE%BD%CF%83%CF%84%CE%B7%CE%BD%CE%95%CE%BB%CE%BB%CE%AC%CE%B4%CE%B1.aspx
# by combining the two following lists you can detect all Greek courts
high_courts = ['Άρειος Πάγος','Ελεγκτικό Συνέδριο','Συμβούλιο της Επικρατείας','Εισαγγελία Αρείου Πάγου']

courts = ['Ειρηνοδικείο', 'Μονομελές Πρωτοδικείο', 'Πολυμελές Πρωτοδικείο', 'Εφετείο', 'Πταισματοδικείο', 'Μονομελές Πλημμελειοδικείο', 'Τριμελές Πλημμελειοδικείο', 'Δικαστήριο Ανηλίκων', 'Μικτό Ορκωτό Δικαστήριο', 'Τριμελές Εφετείο', 'Πενταμελές Εφετείο', 'Μικτό Ορκωτό Εφετείο', 'Εισαγγελία Εφετών', 'Εισαγγελία Πρωτοδικών', 'Μονομελές Διοικητικό Πρωτοδικείο', 'Τριμελές Διοικητικό Πρωτοδικείο', 'Διοικητικό Εφετείο', 'Στρατοδικείο', 'Ναυτοδικείο', 'Αεροδικείο']

court_of = ['Θράκης', 'Ροδόπης', 'Δράμας', 'Έβρου', 'Καβάλας', 'Ξάνθης', 'Ορεστιάδας', 'Κoμoτηvής', 'Αλεξαvδρoύπoλης', 'Θάσoυ', 'Παγγαίoυ', 'Διδυμoτείχoυ', 'Θεσσαλονίκης', 'Βέροιας', 'Έδεσσας', 'Κατερίνης', 'Κιλκίς', 'Σερρών', 'Χαλκιδικής', 'Γιαννιτσών', 'Βασιλικώv', 'Κoυφαλίωv', 'Λαγκαδά', 'Αλεξάvδρειας', 'Νάoυσας', 'Αλμωπίας', 'Σκύδρας', 'Πιερίας', 'Κολινδρού', 'Πoλυκάστρoυ', 'Νιγρίτας', 'Ρoδoλίβoυς', 'Συvτικής', 'Πoλυγύρoυ', 'Αρvαίας', 'Ν.Μουδανιών', 'Δυτικής Μακεδονίας', 'Κοζάνης', 'Γρεβενών', 'Καστοριάς', 'Φλώρινας', 'Εoρδαίας', 'Κλεισούρας', 'Αμυvταίoυ', 'Ιωαννίνων', 'Άρτας', 'Πρέβεζας', 'Κέρκυρας', 'Θεσπρωτίας', 'Ηγoυμεvίτσας', 'Δυτικής Στερεάς', 'Αγρινίου', 'Λευκάδας', 'Μεσoλoγγίoυ', 'Βάλτoυ', 'Βovίτσας', 'Ναυπάκτoυ', 'Λάρισας', 'Βόλου', 'Καρδίτσας', 'Τρικάλων', 'Ελασσόvας', 'Φαρσάλων', 'Αλμυρoύ', 'Σκοπέλου', 'Καλαμπάκας', 'Λαμίας', 'Άμφισσας', 'Ευρυτανίας', 'Λιβαδειάς', 'Αταλάvτης', 'Εύβοιας', 'Θηβών', 'Χαλκίδας', 'Iστιαίας', 'Καρύστoυ', 'Κύμης', 'Ταμιvέωv', 'Αθηνών', 'Αμαρουσίου', 'Αχαρνών', 'Ελευσίνας', 'Ιλίου','Καλλιθέας', 'Κρωπίας', 'Λαυρίου', 'Νέας Iωvίας', 'Μαραθώvoς', 'Μεγάρωv', 'Περιστερίου', 'Χαλανδρίου', 'Πειραιά', 'Αιγίvης', 'Καλαυρίας', 'Κυθήρωv', 'Νίκαιας', 'Σαλαμίvας', 'Σπετσώv', 'Ναυπλίoυ', 'Αργoυς', 'Αστρoυς', 'Μάσσητoς', 'Κoρίvθoυ', 'Σικυώvoς', 'Νεμέας', ' Ξυλoκάστρoυ', 'Σπάρτης', 'Επιδαύρoυ-Λιμηράς', 'Τρίπoλης', 'Μεγαλόπολης', 'Ψωφίδoς', 'Καλαμάτας', 'Πύλου', 'Κυπαρισσίας', 'Πλαταμώδους', 'Γυθείου', 'Νεαπόλεως Βοιών', 'Πατρώv', 'Δύμης', 'Αιγιαλείας', 'Καλαβρύτωv', 'Ακράτας', 'Πύργoυ', 'Ολυμπίωv', 'Αρήvης', 'Αμαλιάδας', 'Γαστoύvης', 'Μυρτoυvτίωv', 'Ζακύvθoυ', 'Αργoστoλίoυ', 'Σαμαίωv', 'Βορείου Αιγαίου', 'Μυτιλήνης', 'Καλλovής', 'Λήμvoυ', 'Πλωμαρίoυ', 'Χίoυ', 'Αιγαίου', 'Σύρου', 'Αvδρoυ', 'Ερμoύπoλης', 'Μήλoυ', 'Μυκόvoυ', 'Πάρoυ', 'Τήvoυ', 'Σάμoυ', 'Iκαρίας', 'Καρλoβασίoυ', 'Νάξoυ', 'Θήρας', 'Δωδεκανήσων', 'Ρόδoυ', 'Καρπάθoυ', 'Κω', 'Καλύμvoυ', 'Λέρoυ', 'Κρήτης', 'Χαvίωv', 'Βάμoυ','Ρεθύμvης','Ανατολικής Κρήτης', 'Ηρακλείου', 'Καστελίoυ - Πεδιάδoς', 'Μoιρώv', 'Πύργoυ Κρήτης', 'Λασιθίου', 'Iεράπετρας', 'Σητείας']




def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x


if __name__ == "__main__":

    # YOUR FILE HERE
    with open('corpus_YODD.txt', 'r') as myfile:
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
    print("CPC: ", len(cpc))

    # CPV code mainly found in YODD
    cpv = re.findall('[0-9]{8}-[0-9]', data)
    print("CPV: ", len(cpv))

    # POEPLE

    military_personel = re.findall('ΣΑ [0-9]{3}/[0-9]{3}/[0-9]{2}', data)
    print("Military personnel: ", military_personel)
    #id_numbers = re.findall(
    #    'Α.Δ.Τ. [Α-Ωα-ω]{0,2} [0-9]{6}|Α.Δ.Τ.: [Α-Ωα-ω]{0,2}-[0-9]{6}|Α.Δ.Τ. [Α-Ωα-ω]{0,2}[0-9]{6}|ΑΔΤ Α[Α-Ωα-ω]{0,2}[0-9]{6}', data)
    id_numbers = re.findall('(Α.Δ.Τ.|Α.Δ.Τ.:|ΑΔΤ) ([Α-Ωα-ω]{0,2}[0-9]{6}|[Α-Ωα-ω]{0,2}-[0-9]{6}|[Α-Ωα-ω]{0,2} [0-9]{6})',data)
    print("ID numbers: ",  len(id_numbers))

    # IBAN accounts
    ibans = re.findall(
        '^[A-Z]{2}(?:[ ]?[0-9]){18,20}$|[A-Z]{2} [0-9]{25}|[A-Z]{2}[0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}', data)
    print("IBAN numbers: ", len(ibans))

    # TVA tax
    TVA = re.findall('(Φ.Π.Α.|ΦΠΑ) [0-9]{1,2}%', data)
    print("TVA rates: ", len(TVA))
    e_mails = re.findall(r'[\w\.-]+@[\w\.-]+', data)

    # E-MAILS
    print("Emails :", len(e_mails))
    #phone_numbers = re.findall(
    #    'τηλ. .+[0-9]|τηλ: .+[0-9]|tel: .+[0-9]|τηλ.: .+[0-9]|Τηλέφωνο: .+[0-9]|Τηλ. .+[0-9]', data)
    phone_numbers = re.findall('(τηλ.|τηλ:|τηλ.:|Τηλ.|Τηλέφωνο:) .+[0-9]',data)
    # Phone numbers
    print("Phone numbers: ", len(phone_numbers))
    post_codes = re.findall('ΤΚ: [0-9]{3} [0-9]{2}', data)
    print("Post codes: ", len(post_codes))

    # exact times can be found in issues like YODD documenting mainly
    # when an assebly or meeting took place
    exact_times = re.findall(
        '[0-9]{2}:[0-9]{2} (π.μ.|μ.μ.)|[0-9]{2}:[0-9]{2}', data)
    print("Exact time: ", len(exact_times))

    # money YODD many variations
    money = re.findall(
        r'[$€£]{1}\d+\.?\d{0,2}|\d+\.\d+\,?\d{0,2} [$€£]{1}|\d+\.\d+\,?\d{0,2} EUR|\d+\.\d+\,?\d{0,2} ευρώ|([0-9]+) ευρώ', data)
    print("Monetary amounts: ", len(money))

    # Other issues (simple heurestic needs work finds around half)
    issues = re.findall(
        'ΦΕΚ [0-9]{1,4}[/.-]{0,1}[Α-Ωα-ω.΄\s][/.-]{0,1}.+[0-9]|\(ΦΕΚ [0-9]{1,4}[/.-]{0,1}[Α-Ωα-ω.΄\s][/.-]{0,1}.+[0-9]', data)
    #print("Issues mentioned: ",  issues)
    print(" Issues number: ", len(issues))
    # Public work using code http://epde.gr/liferay-portal/documents/10181/4692465/%CE%95%CE%93%CE%A7%CE%95%CE%99%CE%A1%CE%99%CE%94%CE%99%CE%9F+%CE%9B%CE%95%CE%99%CE%A4%CE%9F%CE%A5%CE%A1%CE%93%CE%99%CE%A9%CE%9D/d9ad1db6-bfb7-42ce-8fba-74666568a083
    publc_works = re.findall('[0-9]{4}[Α-Ωα-ω]{2}[0-9]{8}', data)
    print("Public works: ", len(publc_works))

    # find NUTS european regions https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:02003R1059-20180118&qid=1519136585935
    NUTS_reg = re.findall('NUTS: [A-Z]{2}[0-9]{1,3}', data)
    print("NUTS_reg: ", len(NUTS_reg))

    # find KAEK  code basic heurestic  http://www.ktimatologio.gr/aboutus/Documents/Pages/33/LqYyvusGBh2JgNdw/diad_entaksis_praxis_efarmogis_1.pdf
    kaek = re.findall('ΚΑΕΚ(- )[0-9/]{12}', data)
    #print("KAEK: ", kaek)
    print("KAEK: ", len(kaek))

    # get AFM
    afm = re.findall('(ΑΦΜ|Α.Φ.Μ.|ΑΦΜ:) [0-9]{9}', data)
    print('AFM codes: ', len(afm))

    # get HULL number of ship, mainly used in AAP issues uncomplete
    hull = re.findall(
        'HULL No ([A-Z0-9 -]{1,17}|[A-Z]{1,2} [0-9]{1,17})', data)
    print('HUll numbers: ', hull)

    # Ship flags (doesnt work)
    flags = re.findall('[Α-Ω][\u0370-\u03FF]+ σημαία', data)
    print('Flags: ', len(flags))
    # FIND METRICS -Distances
    # Scale
    scales = re.findall('1:[0-9]{1,10}', data)
    print("Scales: ", len(scales))
    # meters
    meters = re.findall('\-?\d+\,\d+ (m|μ)|\-?\d+\,\d+(m|μ)', data)
    print("Meters : ", len(meters))
    kilometers = re.findall('\-?\d+\,\d+ km', data)
    print("KiloMeters : ", kilometers)

    # Conditions
    cond = []
    for i in range(0, len(conditions)):
        cond.append(re.findall(conditions[i], data))

    print("Conditions found: ", len(list(flatten(cond))))

    # Temperatures
    temps = re.findall('^[-+]?\d*\.?\d*$°C', data)
    print("Temps: ", temps)

    # Weight
    weight = re.findall('[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d* (Kg|kg|kgr)|[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(Kg|kg|kgr)',data)
    print("Weights: ", len(weight))

    # Volume 
    volumes = re.findall('[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d\d)*(λίτρα|It|lt|ml)|[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)* (λίτρα|It|lt|ml)',data)
    print("Volumes: ", len(volumes))

    # Ship tonnage in register tons
    tonnage = re.findall('[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)* κόροι|[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)* κόρωv', data)
    print("Tonnage: ", tonnage)

    # Power
    power = re.findall('[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)* KW|[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)*KW',data)
    print("Power mesurements: ", power) 

    # Surface
    surface = re.findall('[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)* (μ2|τετραγωνικών μέτρων|τμ|τ.μ.|στρέμματα|στρ|στρ.)|[-+]?[.]?[\d]+[-+]?[.]?[\d]+(?:,\d\d)*(μ2|τετραγωνικών μέτρων|τμ|τ.μ.|στρέμματα|στρ|στρ.)',data)
    print("Surface measurements: ", len(surface)) 

    # Natura Territories
    natura_ter = re.findall("GR[0-9]{7}", data)
    print("Natura 2000 regions: ", len(natura_ter))

    # Wildlife sanctuaries
    wildlife_sanct = re.findall('Καταφύγιο Άγριας Ζωής [Α-ΩA-Z0-9]+',data)
    print("Wildlife sanctuaries: ", wildlife_sanct)

    # Act of deletion from the Public HR registry
    del_from_registry = re.findall(
        "(Αριθ. βεβ. διαγραφής από το Μητρώο Ανθρώπινου Δυναμικού Ελληνικού Δημοσίου: [0-9]{10}/[0-9]{2}.[0-9]{2}.[0-9]{4})", data)
    print("Deletion from registry: ", len(del_from_registry))

    # Act of inscription to the Public HR registry
    ins_to_registry = re.findall(
        "(Αριθμ. βεβ. εγγραφής στο Μητρώο Ανθρώπινου Δυναμικού Ελληνικού Δημοσίου: [0-9]{10}/[0-9]{2}.[0-9]{2}.[0-9]{4})", data)
    print("Insertion to registry: ", len(ins_to_registry))

    # Finfing Courts
    # print(re.findall(r"(?=("+'|'.join(high_courts)+r"))",data))
    # print(re.findall(r"(?=("+'|'.join(courts)+r"[Α-Ωα-ω]+"+r"))",data))
    

    # Directives EU 
    directives = re.findall('(Οδηγία|Οδηγίας) [0-9]+/[0-9]+/[Α-Ω]{2,4}',data)
    print("EU Directives: ", len(directives))

    # ADA -> Αριθμός Διαδικτυακής Ανάρτησης (Internet Publcation Numbers)
    adas = re.findall('(ΑΔΑ:|ΑΔΑ) [Α-Ω0-9]{4,10}-[Α-Ω0-9]{3}',data)
    print("ADAs found: ", len(adas))

    #OPS code -> code to th Ολοκληρωμένο Πληροφοριακό Σύστημα (ΟΠΣ) 
    ops = re.findall('ΟΠΣ [0-9]+|ΟΠΣ: [0-9]+',data)
    print("OPS codes found: ", ops)

    #Protocols ISO-ELOT
    protocols = re.findall('πρότυπο ([Α-ΩA-Z]{2,4} [Α-ΩA-Z]{2,4} [0-9:-]+|[Α-ΩA-Z]{2,4} [0-9:-]+)',data)
    print("Protocols: ", protocols)  

    #Academic year:
    ac_year = re.findall('ακαδημαϊκό έτος [0-9]{4}-[0-9]{4}',data)
    print("Academic year: " , ac_year)
   
    #
    


