from kafka import KafkaProducer
from utils import json_config_loader
import json
KAFKA_SERVERS = json_config_loader('config/kafka.json')["bootstrap_servers"]
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVERS,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
# service_ agent topic : service_127.0.0.1
producer.send("service_218.185.248.66",
              {
                  "command": "START",
                  "service": "ai_manager"
              })
