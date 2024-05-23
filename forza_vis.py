# from fdp import ForzaDataPacket
from visualization.visualize import visualize_data
from producer.producer import FDPProducer 
from consumer.consumer import FDPConsumer
import logging
import socket
import threading
import yaml

def make_connection(ip_address='', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # print(ip_address)
    server_socket.bind((ip_address, port))

    logging.info('listening on port {}'.format(port))
    return server_socket

def parse_parameters(config_file=None, ip_address='', port=1234, params=[]):
    
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

        if 'parameter_list' in config:
            params = config['parameter_list']

    return {"ip_address":ip_address, "port":port, "params":params}

def main():
    import argparse
    ''' parse input '''
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
    

    ''' setup '''
    params = parse_parameters(config_file=args.config_file)
    sock = make_connection(ip_address=params['ip_address'], port=params['port'])
    fdpproducer = FDPProducer(sock, stop_event=stop_event)
    fdpconsumer = FDPConsumer(stop_event=stop_event)

    ''' prepare signal to exit / close'''
    stop_event = threading.Event()

    logging.info('{INFO: Creating Producer Thread for {}'.format(fdpproducer))
    producer_thread = threading.Thread(target=fdpproducer.start_producer)
    logging.info('{INFO: Creating Consumer Thread for {}'.format(fdpconsumer))
    consumer_thread = threading.Thread(target=fdpconsumer.start_consumer)
    
    producer_thread.start()
    logging.info('{INFO: Starting Producer Thread: {}'.format(producer_thread))
    consumer_thread.start()
    logging.info('{INFO: Starting Consumer Thread: {}'.format(consumer_thread))
    
    try:
        # Start the visualization
        visualize_data(stop_event, fdpconsumer.data_queue)
    except KeyboardInterrupt:
        logging.info('{INFO: Exiting due to keyboard interrupt')

    # Signal threads to stop and wait for them to finish
    stop_event.set()
    producer_thread.join()
    consumer_thread.join()


if __name__ == "__main__":
    main()