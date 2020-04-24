import yaml
import json
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from feature_extraction_functions import *
from sklearn import preprocessing


# read the yaml file and return a dictionary
def parse(config_filename):
    cfg = None
    try:
        with open(config_filename, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)

    except yaml.YAMLError as e:
        print(e)
        print("Yaml config file not found.")
        exit()

    return cfg


# if necessary get the data from elasticsearch
def get_data(cfg):
    d = None
    try:
        if cfg.get("input_file") is not None:
            with open(cfg.get('input_file'), 'r') as datafile:
                print('Reading from input file: ' + cfg.get("input_file"))
                d = json.load(datafile)['hits']['hits']

    except IOError:
        print("Could not read file: ", cfg.get('input_file'))
        exit()

    if d is None:
        import esRetrieval
        filter = "clientID:" + cfg.get("client_id") + " AND " + " AND ".join(cfg.get("filter"))
        print('querying elasticsearch using filter: ' + filter)
        d = esRetrieval.retrieve(cfg.get("date_range")["start_date"],
                                 cfg.get("date_range")["range"],
                                 filter,
                                 cfg.get("result_size"),
                                 cfg.get("scroll"))

    return d


def get_features(data, config):
    """
    Here is a list of the features which the paper used to classify traffic:

    - % of same service to same host
    - % on same host to same service
    - average duration / all services
    - average duration / current host
    - average duration / current service
    - bytes transferred / all services
    - bytes transferred / current host
    - bytes transferred / current service
    - destination bytes
    - destination IP
    - destination port
    - duplicate ACK rate
    - duration
    - hole rate
    - land [large?] packet rate
    - protocol
    - resent rate
    - source bytes
    - source IP
    - source port
    - TCP flags
    - timestamp
    - # different services accessed [by the same source IP?]
    - # establishment errors
    - # FIN flags
    - # ICMP packets
    - # keys with outside hosts [?]
    - # new keys [?]
    - # other errors
    - # packets to all services
    - # RST flags
    - # SYN flags
    - # to certain services
    - # to privileged services
    - # to the same host
    - # to the same service
    - # to unprivileged services
    - # total connections
    - # unique keys [?]
    - # urgent
    - % control packets
    - % data packets
    - wrong data packet size rate
    - variance of packet count to keys

    while there's some speculation about what these actually mean (especially mentioning "keys"),
    of these, netflow data seems to lend itself to the following features:

    - % of same service to same host
    - % on same host to same service
    - bytes transferred / all services
    - bytes transferred / current host
    - bytes transferred / current service
    - protocol
    - source bytes
    - source IP
    - source port
    - TCP flags
    - timestamp
    - # different services accessed
    - # FIN flags
    - # ICMP packets
    - # RST flags
    - # SYN flags
    - # to certain services
    - # to privileged services
    - # to the same host
    - # to the same service
    - # to unprivileged services
    - # total connections
    - # urgent
    - % control packets
    - % data packets

    Some of these are "line-by-line" features and some depend on statistics across the whole dataset.
    """

    single_valued_functions = {
        'protocol': lambda record: record['_source']['netflow']['protocol'],
        'source_bytes': lambda record: record['_source']['netflow']['in_bytes'],
        'source_IP': lambda record: record['_source']['netflow']['ipv4_src_addr'],
        'source_port': lambda record: record['_source']['netflow']['l4_src_port'],
        'TCP_flags': lambda record: record['_source']['netflow']['tcp_flags'],
        'timestamp': lambda record: record['_source']['@timestamp'],
    }

    aggregate_functions = {
        'num_different_services_accessed':        num_diff_serv_acces,
        'num_FIN_flags':                          num_FIN_flags,
        'num_ICMP_packets':                       num_ICMP_packets,
        'num_RST_flags':                          num_RST_flags,
        'num_SYN_flags':                          num_SYN_flags,
        'num_to_certain_services':                num_to_certain_services(config),
        'num_to_privileged_services':             num_to_privileged_services,
        'num_to_the_same_host':                   num_to_the_same_host,
        'num_to_the_same_service':                num_to_the_same_service,
        'num_to_unprivileged_services':           num_to_unprivileged_services,
        'num_total_connections':                  num_total_connections,
        'num_urgent':                             num_urgent,
        'percent_control_packets':                percent_control_packets,
        'percent_data_packets':                   percent_data_packets,
        # 'percent_of_same_service_to_same_host':   percent_of_same_service_to_same_host,
        # 'percent_on_same_host_to_same_service':   percent_on_same_host_to_same_service,
        'bytes_transferred_over_all_services':    bytes_transferred_over_all_services,
        'bytes_transferred_over_current_host':    bytes_transferred_over_current_host,
        'bytes_transferred_over_current_service': bytes_transferred_over_current_service,
    }

    features = []

    aggregations = {
        'num_different_services_accessed': defaultdict(set),
        'num_FIN_flags': defaultdict(int),
        'num_ICMP_packets': defaultdict(int),
        'num_RST_flags': defaultdict(int),
        'num_SYN_flags': defaultdict(int),
        'num_to_certain_services': defaultdict(int),
        'num_to_privileged_services': defaultdict(int),
        'num_to_the_same_host': defaultdict(int),
        'num_to_the_same_service': defaultdict(int),
        'num_to_unprivileged_services': defaultdict(int),
        'num_total_connections': defaultdict(int),
        'num_urgent': defaultdict(int),
        'percent_control_packets': defaultdict(dict),
        'percent_data_packets': defaultdict(dict),
        # 'percent_of_same_service_to_same_host': defaultdict(float),
        # 'percent_on_same_host_to_same_service': defaultdict(float),
        'bytes_transferred_over_all_services': defaultdict(int),
        'bytes_transferred_over_current_host': defaultdict(int),
        'bytes_transferred_over_current_service': defaultdict(int),
    }

    print("Acquiring features from file")
    #feature selection data from yaml file
    f_to_use = config['feature_selection']['features']

    #the names of each data type in 'features'
    colum_names = []
    has_set_names = False

    row = len(data)
    print("Aquireing features from", row, "rows")
    for d in data:

        f = [d['_id']]
        for name, function in single_valued_functions.items():
            if has_set_names == False:
                colum_names.append(name)
            f.append(function(d))

        for name, function in aggregate_functions.items():
            if has_set_names == False:
                colum_names.append(name)
            function(aggregations[name], d)

        has_set_names = True

        features.append(f)
        
    print("Processing aggregate features")
    for f in features:
        for name, hash in aggregations.items():
            if f_to_use[name] == True:

                val = hash[f[3]]

                # Number of unique things
                if isinstance(val, set):
                    val = len(val)

                # Percentages
                if isinstance(val, dict):
                    if 'special' in val:
                        val = val['special'] / val['all'] * 100
                    else:
                        val = 0

                f.append(val)

    return remove_features(features, colum_names, config)



# remove the strings from the data for the ML
# also remove the features not set in yaml file
def remove_features(features, colum_names, config):

    options = config.get("feature_selection")["features"]

    # keep the features with strings
    np.savetxt('data_raw.csv', features, delimiter=',', fmt='%s')   # X is an array

    new = []
    for i in features:
        colum = 0
        line = []
        del i[0]

        for x in i:

            current_col = colum_names[colum]
            if options[current_col] == True:

                if isinstance(x, str):
                    #check if its an ip, convert to int
                    if x.count('.') == 3:
                        x = ip_to_num(x)
                    else:
                        colum += 1
                        continue

                line.append(x)

            colum = colum + 1
        new.append(line)

    return normilized(new)


def normilized(features):
    return preprocessing.MinMaxScaler().fit_transform(np.array(features))

# call the ML
def classify(feature_array):
    import train
    print("Applying ML to features")
    classified_data = train.train(feature_array)
    references = extract_references(classified_data[0], feature_array)
    return references

def extract_references(classified_data, feature_array):
    ref = []
    print(len(classified_data), " records were found to be anomalies")
    for i in classified_data:
        record = feature_array[i]
        ref.append(record)
    return ref



def display(plot, records):
    print(1)
    boxplot(records)
    print(2)
    boxplot(plot)
    # pass


def boxplot(feature_array):

    df = pd.DataFrame(feature_array)

    plt.figure(figsize=(6, 5), dpi=150)
    plt.yscale('log')

    sns.boxplot(data=df)
    sns.swarmplot(data=df, color='.3', size=2)

    plt.show()


ips = []
def ip_to_num(ip):
    global ips
    if ip not in ips:
        ips.append(ip)

    return ips.index(ip)


if __name__ == '__main__':

    # open the yamal file and get a dictionary out
    config = parse('config.yaml')

    # the yaml file can take a jason file in the "input_file" field if this is specified
    # then the data returned is the suff in the given jason.
    # If not file is given then we run the esRetrival prgram to get data
    data = get_data(config)

    # take the data and get the features needed for the algorithm
    feature_array = get_features(data, config)

    # take fetrues and apply the model
    records = classify(feature_array)

    # show the graph and any other data we want
    display(feature_array, records)

    print("Done")

