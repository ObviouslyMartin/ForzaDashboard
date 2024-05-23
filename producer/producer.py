'''
Procucer listens on local host at a specified port and creates/sends ForzaDataPackets
to the consumer.

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

from kafka import KafkaProducer
import json
import datetime as dt
from fdp import ForzaDataPacket
import logging
import yaml as yaml

class FDPProducer:
    def __init__(self, soc, stop_event) -> None:
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v.to_dict()).encode('utf-8')
        )
        self.socket = soc
        self.topic = 'forza-data'
        self.stop_event = stop_event
        self.n_packets = 0

    def start_producer(self, ):
        self.receive_packet(self.stop_event)
        self.producer.close()

    def send_packet(self, packet):
        self.producer.send('forza-data', packet)
        self.producer.flush()

    def receive_packet(self, stop_event):
        while not stop_event.is_set():
            message, address = self.socket.recvfrom(1024)
            self.n_packets += 1
            fdp = ForzaDataPacket(message)
            logging.info(f'INFO: Running packet count: {self.n_packets}')
            # logging.info(f'Received message from {address}: {message}')

            if fdp.is_race_on:
                logging.info('{}: in race, logging data'.format(dt.datetime.now()))
                
                ''' Packet Processing here '''
                # print(fdp.to_list(params))
                # print(int(fdp.race_pos), f'||||| LAP: {int(fdp.lap_no)}')
                # print((fdp.timestamp_ms/1000)/60/60)
                
                if self.n_packets % 60 == 0:
                    logging.info('{}: logged {} packets'.format(dt.datetime.now(), self.n_packets))
            else:
                if self.n_packets % 60 == 0:
                    logging.info('{}: out of race, stopped logging data'.format(dt.datetime.now()))
            self.send_packet(fdp) 