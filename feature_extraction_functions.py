def num_diff_serv_acces(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    acc[current_host].add(record['_source']['netflow']['l4_dst_port'])


def num_FIN_flags(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    is_fin = record['_source']['netflow']['tcp_flags'] & 1
    acc[current_host] += is_fin


def num_ICMP_packets(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    is_icmp = record['_source']['netflow']['protocol'] == 1
    acc[current_host] += is_icmp


def num_RST_flags(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    is_rst = (record['_source']['netflow']['tcp_flags'] & 4) == 4
    acc[current_host] += is_rst


def num_SYN_flags(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    is_syn = (record['_source']['netflow']['tcp_flags'] & 2) == 2
    acc[current_host] += is_syn


def num_to_certain_services(config):
    def _num_to_certain_services(acc, record):
        current_host = record['_source']['netflow']['ipv4_src_addr']
        which_port = config.get("which_port")
        is_same_port = record['_source']['netflow']['l4_dst_port']
        if which_port == is_same_port:
            acc[current_host] += 1

    return _num_to_certain_services


def num_to_privileged_services(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    port = record['_source']['netflow']['l4_dst_port']
    if port < 1024:
        acc[current_host] += 1


def num_to_the_same_host(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    host = record['_source']['netflow']['ipv4_dst_addr']
    # not sure if this does the job
    acc[host] += 1


def num_to_the_same_service(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    service = record['_source']['netflow']['l4_dst_port']
    acc[service] += 1


def num_to_unprivileged_services(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    port = record['_source']['netflow']['l4_dst_port']
    if port >= 1024:
        acc[current_host] += 1


def num_total_connections(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    connection = record['_source']['netflow']["flow_seq_num"]
    if current_host not in acc:
        acc[current_host] = set()

    acc[current_host].add(connection)


def num_urgent(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    is_syn = (record['_source']['netflow']['tcp_flags'] & 32) == 32
    acc[current_host] += is_syn


def percent_control_packets(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    in_pkts = record['_source']['netflow']['in_pkts']
    if 'all' not in acc[current_host]:
        acc[current_host]['all'] = 0
        acc[current_host]['special'] = 0

    acc[current_host]['all'] += in_pkts

    if record['_source']['netflow']['protocol'] == 1:
        acc[current_host]['special'] += in_pkts


def percent_data_packets(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    in_pkts = record['_source']['netflow']['in_pkts']
    if 'all' not in acc[current_host]:
        acc[current_host]['all'] = 0
        acc[current_host]['special'] = 0

    acc[current_host]['all'] += in_pkts

    if record['_source']['netflow']['protocol'] != 1:
        acc[current_host]['special'] += in_pkts


def percent_on_same_host_to_same_service(acc, record):
    pass


def percent_of_same_service_to_same_host(acc, record):
    pass


def bytes_transferred_over_all_services(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    acc[current_host] += record['_source']['netflow']['in_bytes']


def bytes_transferred_over_current_host(acc, record):
    current_host = record['_source']['netflow']['ipv4_src_addr']
    bytes = record['_source']['netflow']['in_bytes']
    acc[current_host] += bytes


def bytes_transferred_over_current_service(acc, record):
    current_service = record['_source']['netflow']['l4_dst_port']
    bytes = record['_source']['netflow']['in_bytes']
    acc[current_service] += bytes