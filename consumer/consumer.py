'''
Handles consumption of ForzaDataPackets set by FDPProcuder by setting up a 
public data_queue

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


from kafka import KafkaConsumer
import json
import queue

class FDPConsumer:
    def __init__(self, stop_event) -> None:
        self.consumer = KafkaConsumer(
            'forza-data',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='forza-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.stop_event = stop_event
        self.data_queue = queue.Queue()
        self.n_packets = 0
    def start_consumer(self) -> None:
        self.consume_packets()
    def close(self) -> None:
        self.consumer.close()

    def consume_packets(self) -> None:
        while not self.stop_event.is_set():
            for message in self.consumer:
                if self.stop_event.is_set():
                    break
                packet = message.value
                self.data_queue.put(packet)
                n_packets += 1
                print(f"Consumed packet: {packet}")
        self.close()

