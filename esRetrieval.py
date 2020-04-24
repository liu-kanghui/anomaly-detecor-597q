import datetime
import csv
from collections import defaultdict
from elasticsearch import Elasticsearch


# start_date        is an array [y, m, d] of what date you want to start collecting records on
# number_of_days    is how many days you want to collect
# filter            is the city you want to look at and what kind of filters you want this will be a string
# size              is the number of records you want in the search
# scroll            idk what this does. it just is

# TODO: need to make return data

def retrieve(start_date, number_of_days, filter, size, scroll):
    # Establish date range
    date = datetime.datetime(start_date[0], start_date[1], start_date[2])

    # Establish ElasticSearch
    es = Elasticsearch()

    # Establish indices for the days
    indices = []
    for i in range(number_of_days):
        indices.append('logstash-' + date.strftime('%Y.%m.%d'))
        date += datetime.timedelta(days=1)

    output = []

    # Collect from days
    for index in indices:
        print('Collecting from ' + index)
        byteFlow = defaultdict(float)
        try:
            # replaced with our parameters from the yaml file
            # hope this does not break it :)
            res = es.search(index=index, q=filter, size=size, scroll=scroll)
            i = 0
            while len(res['hits']['hits']) > 0:
                print('part', i)
                i += 1
                output.extend(res['hits']['hits'])
                # for hit in res['hits']['hits']:
                #     netflow = hit['_source']['netflow']
                #
                #     # Establish src/dst
                #     if ('192.168' not in netflow['ipv4_src_addr']):
                #         src = 'superNode'
                #     else:
                #         src = netflow['ipv4_src_addr']
                #
                #     if ('192.168' not in netflow['ipv4_dst_addr']):
                #         dst = 'superNode'
                #     else:
                #         dst = netflow['ipv4_dst_addr']
                #
                #     byteFlow[(src, dst)] += (netflow['out_bytes'] / 2 ** 20)
                #     byteFlow[(dst, src)] += (netflow['in_bytes'] / 2 ** 20)

                scroll = res['_scroll_id']
                res = es.scroll(scroll_id=scroll, scroll='1m')
            # with open('../data/byte/byte_' + index + '.csv', 'w') as outfile:
            #     writer = csv.writer(outfile)
            #     writer.writerow(['src', 'dst', 'MB'])
            #     for key, value in byteFlow.items():
            #         writer.writerow([key[0], key[1], value])
            return output

        except Exception as e:
            print('Could not collect from ' + index)
            print(e)
