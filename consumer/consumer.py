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

