'''
Script to listen on a given port for UDP packets sent by a Forza Motorsport (2023)
"data out" stream and write the data to a CSV file.

Copyright (c) 2024 Martin Plut

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import logging
import socket

import yaml as yaml
import datetime as dt

from fdp import ForzaDataPacket

def to_str(value):
    '''
    Returns a string representation of the given value, if it's a floating
    number, format it.

    :param value: the value to format
    '''
    if isinstance(value, float):
        return('{:f}'.format(value))

    return('{}'.format(value))

def dump_stream(port=5000, packet_format='dash', config_file=None):
    '''
    Listens to UDP packets on the given port
    and writes data to the file.

    int: port=listening port number
    str: packet_format=the packet format sent by the game, one of either 'sled' or 'dash'
    str: config_file=path to the YAML configuration file
    '''

    if config_file:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        ## The configuration can override everything        
        if 'address' in config:
            ip_address = config['address']
        else:
            ip_address = ''

        if 'port' in config:
            port = config['port']

        if 'packet_format' in config:
            packet_format = config['packet_format']

    params = ForzaDataPacket.get_props(packet_format = packet_format)
    if config_file and 'parameter_list' in config:
        params = config['parameter_list']

    log_wall_clock = False
    if 'wall_clock' in params:
        log_wall_clock = True

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(ip_address)
    server_socket.bind((ip_address, port))

    logging.info('listening on port {}'.format(port))

    n_packets = 0
    while True:
        message, address = server_socket.recvfrom(1024)
        # print(f"Received message from {address}: {message}")
        fdp = ForzaDataPacket(message, packet_format = packet_format)
        if log_wall_clock:
            fdp.wall_clock = dt.datetime.now()

        if fdp.is_race_on:
            if n_packets == 0:
                logging.info('{}: in race, logging data'.format(dt.datetime.now()))
            
            # print(fdp.to_list(params))
            # print(int(fdp.race_pos), f'||||| LAP: {int(fdp.lap_no)}')
            # print((fdp.timestamp_ms/1000)/60/60)

            n_packets += 1
            if n_packets % 60 == 0:
                logging.info('{}: logged {} packets'.format(dt.datetime.now(), n_packets))
        else:
            if n_packets > 0:
                logging.info('{}: out of race, stopped logging data'.format(dt.datetime.now()))
            n_packets = 0

def main():
    import argparse

    cli_parser = argparse.ArgumentParser(
        description="script that grabs data from a Forza Motorsport stream and dumps it to a TSV file"
    )

    cli_parser.add_argument('-v', '--verbose', action='store_true',
                            help='write informational output')

    cli_parser.add_argument('-c', '--config_file', type=str,
                            help='path to the YAML configuration file')


    args = cli_parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    dump_stream(config_file=args.config_file)

    return()

if __name__ == "__main__":
    main()
    
