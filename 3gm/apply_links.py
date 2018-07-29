import codifier
import syntax
import helpers
from statistics import mean, stdev

def apply_links(identifier):

    law = codifier.codifier.laws[identifier]
    links = codifier.codifier.links[identifier]

    links.sort()

    initial = law.serialize()
    initial['_version'] = 0

    versions = [initial]

    total = 0
    detected = 0
    applied = 0
    tmp_index = links.actual_links[0]['from']
    version_index = 0
    increase_flag = False

    for i, l in enumerate(links):
        if l['from'] == tmp_index:
            # Non applied modifying links trigger amendments
            if l['status'] == 'μη εφαρμοσμένος' and l['link_type'] == 'τροποποιητικός':
                increase_flag = True
                total += 1

                # Detect amendment
                try:
                    d, a = law.apply_amendment(l['text'])

                    # Increase accuracy bits
                    detected += d
                    applied += a

                    # Update link status
                    links.actual_links[i]['status'] = 'εφαρμοσμένος'
                except:
                    pass

        else:
            if increase_flag:
                # If it indeed modifies law then increase version
                version_index += 1
                s = law.serialize()
                s['_version'] = version_index
                s['amendee'] = tmp_index
                versions.append(s)

            tmp_index = l['from']
            increase_flag = False

    # JSON holding all versions to be stored to GridFS
    final_serializable = {
        '_id': 'ν. 4009/2011',
        'versions': versions
    }

    for v in final_serializable['versions']:
        print(v['_version'])
        print(v['amendee'])

    try:
        detection_accurracy = 100 * detected / total
        query_accuracy = 100 * applied / detected
    except:
        detection_accurracy = 100
        query_accuracy = 100


    print('Detection accuracy: ' + str(detection_accurracy) + '%')
    print('Querying from Detection accuracy: ' + str(query_accuracy) + '%')

    return detection_accurracy, query_accuracy, final_serializable, links

def apply_all_links(identifiers=None):
    """Apply all links in the codifier object"""
    if identifiers == None:
        codifier_keys = list(codifier.codifier.laws.keys())
        sorted_keys = helpers.quicksort(codifier_keys, key=helpers.compare_year)
    else:
        sorted_keys = helpers.quicksort(identifiers, helpers.compare_statutes)


    detection_accurracy = []
    query_accuracy = []

    for identifier in sorted_keys:

        d, q, final_serializable, links = apply_links(identifier)

        # Update links
        codifier.codifier.links[identifier] = links
        codifier.codifier.db.links.save(links.serialize())

        # Store to fs
        codifier.codifier.db.save_json_to_fs(identifier, final_serializable)

        # Update accuracy metrics
        detection_accurracy.append(d)
        query_accuracy.append(q)


    print('Mean Detection accuracy: {}%. Std: {}%'.format(mean(detection_accurracy), stdev(detection_accurracy)))
    print('Mean Query accuracy: {}%. Std: {}%'.format(mean(query_accuracy), stdev(query_accuracy)))

if __name__ == '__main__':
    apply_links('ν. 4009/2011')
