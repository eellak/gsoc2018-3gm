import argparse
import copy
import codifier
import syntax
import helpers
from statistics import mean, stdev
import logging
import pparser as parser
logger = logging.getLogger()
logger.disabled = True


def apply_links(identifier):
    """Apply all modifying links on a law
    :params identifier The identifier of the law
    """
    # rollback laws
    try:
        print('Rolling back...')
        init = codifier.codifier.db.rollback_laws(identifier)
        codifier.codifier.laws[identifier] = paraser.LawParser.from_serialized(
            init)
    except BaseException:
        print('No history on filesystem')

    # rollback links
    try:
        init = codifier.codifier.db.rollback_links(identifier=identifier)
        codifier.codifier.links[identifier] = codifier.Link.from_serialized(
            init)
    except BaseException:
        print('No links found')

    # Get information from codifier object
    law = codifier.codifier.laws[identifier]
    links = codifier.codifier.links[identifier].sort()

    # Initialize
    # pdb.set_trace()
    initial = law.serialize()
    initial['_version'] = 0

    versions = []
    versions.append(copy.deepcopy(initial))

    # Stats
    total = 0
    detected = 0
    applied = 0
    tmp_index = links.actual_links[0]['from']
    version_index = 0
    increase_flag = False

    # Apply amendments
    for i, l in enumerate(links):
        if l['from'] == tmp_index:
            # Non applied modifying links trigger amendments
            if l['status'] == 'μη εφαρμοσμένος' and l['link_type'] == 'τροποποιητικός':
                increase_flag = True
                total += 1

                # Detect amendment
                try:
                    d, a, law = law.apply_amendment(l['text'])

                    # Increase accuracy bits
                    detected += d
                    applied += a

                    # Update link status
                    if a == 1:
                        print('applied sucessfully')
                        links.actual_links[i]['status'] = 'εφαρμοσμένος'
                except BaseException as e:
                    pass

        else:
            if increase_flag:
                # If it indeed modifies law then increase version
                version_index += 1
                s = copy.deepcopy(law.serialize())
                s['_version'] = version_index
                s['amendee'] = tmp_index
                versions.append(s)

            tmp_index = l['from']
            increase_flag = False

    # JSON holding all versions to be stored to GridFS
    final_serializable = {
        '_id': identifier,
        'versions': versions
    }

    # Calculate accuracy
    try:
        detection_accurracy = 100 * detected / total
        query_accuracy = 100 * applied / detected
    except BaseException:
        print('No amendments')
        detection_accurracy = 100
        query_accuracy = 100

    print('Detection accuracy: ' + str(detection_accurracy) + '%')
    print('Querying from Detection accuracy: ' + str(query_accuracy) + '%')

    return detection_accurracy, query_accuracy, final_serializable, links


def apply_all_links(identifiers=None):
    """Apply all links in the codifier object"""
    if identifiers is None:
        identifiers = list(codifier.codifier.laws.keys())

    helpers.quicksort(identifiers, helpers.compare_statutes)

    # initialize stats
    detection_accurracy = []
    query_accuracy = []
    total = len(identifiers)

    # apply all links
    for i, identifier in enumerate(identifiers):

        try:
            d, q, final_serializable, links = apply_links(identifier)
            # Update links
            codifier.codifier.links[identifier] = links
            try:
                codifier.codifier.db.links.save(links.serialize())
            except BaseException:
                print('MongoDB Error in storing Links')

            # Update accuracy metrics
            detection_accurracy.append(d)
            query_accuracy.append(q)
        except KeyError:
            # Law is never amended
            initial = codifier.codifier.laws[identifier].serialize()
            initial['_version'] = 0
            final_serializable = {
                '_id': identifier,
                'versions': [initial]
            }
        finally:
            # Store current version to mongo
            latest = {
                '_id': identifier,
                'versions': [final_serializable['versions'][-1]]
            }
            try:
                codifier.codifier.db.laws.save(latest)
            except BaseException:
                print('MongoDB Error in storing current version')

            # Store versioning history to fs
            try:
                codifier.codifier.db.save_json_to_fs(
                    identifier, final_serializable)
            except BaseException:
                print('GridFS Error in storing history')

            print('Complete {} Progress: {}/{} {}%'.format(
                identifier, i + 1,
                total, (i + 1) / total * 100))

    # Extract statisticsapply_am
    if len(detection_accurracy) >= 2:
        print('Mean Detection accuracy: {}%. Std: {}%'.format(
            mean(detection_accurracy), stdev(detection_accurracy)))
        print('Mean Query accuracy: {}%. Std: {}%'.format(
            mean(query_accuracy), stdev(query_accuracy)))


def apply_links_between(start, end):
    """Apply links between two years"""
    identifiers = list(codifier.codifier.laws.keys())
    identifiers = list(
        filter(lambda x: start <= int(x[-4:]) <= end, identifiers))
    print(len(identifiers))
    apply_all_links(list(identifiers))


if __name__ == '__main__':
    # parse cmd line arguments
    argparser = argparse.ArgumentParser()

    required = argparser.add_argument_group('required arguments')
    optional = argparser.add_argument_group('optional arguments')

    optional.add_argument(
        '--test',
        help='Run test on example',
        action='store_true')
    optional.add_argument('--start', help='Year from which to start', type=int)
    optional.add_argument('--end', help='Year to end', type=int)

    args = argparser.parse_args()

    if args.test:
        apply_all_links(['ν. 4009/2011'])
    elif args.start is not None and args.end is not None:
        apply_links_between(args.start, args.end)
    else:
        apply_all_links()
