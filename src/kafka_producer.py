import json
import os
import sys
import time
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.unified_schema import (
    normalize_indeed_row,
    normalize_linkedin_row,
    normalize_wellfound_row,
    normalize_naukri_row
)

# Attempt to import kafka-python
try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

TOPIC_NAME = "raw_job_postings"
BUFFER_FILE = "kafka_stream_buffer.jsonl"

def get_kafka_producer(bootstrap_servers='localhost:9092'):
    if not KAFKA_AVAILABLE:
        print("[Kafka Producer] kafka-python package not available. Using JSONL Stream Buffer fallback.")
        return None
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
            request_timeout_ms=5000
        )
        print(f"[Kafka Producer] Connected successfully to Kafka broker at {bootstrap_servers}")
        return producer
    except Exception as e:
        print(f"[Kafka Producer] Could not connect to Kafka broker at {bootstrap_servers}: {e}")
        print("[Kafka Producer] Streaming events to local Kafka JSONL Buffer file instead.")
        return None

def publish_job_event(producer, event, buffer_fp=None):
    """Publishes a single standardized job event to Kafka or buffer file."""
    if producer:
        try:
            producer.send(TOPIC_NAME, value=event)
            return True
        except Exception as e:
            print(f"[Kafka Error] Failed to publish event: {e}")
    
    # Fallback to streaming buffer file
    if buffer_fp:
        buffer_fp.write(json.dumps(event, ensure_ascii=False) + "\n")
    return True

def run_ingestion_pipeline(limit_per_file=None, progress_callback=None):
    print("==================================================")
    print("   BIG DATA INGESTION PIPELINE (KAFKA PRODUCER)   ")
    print("==================================================")

    producer = get_kafka_producer()
    buffer_fp = open(BUFFER_FILE, "w", encoding="utf-8") if not producer else None

    files_config = [
        ('indeed_jobs.csv', normalize_indeed_row),
        ('jobs.csv', normalize_linkedin_row),
        ('master.csv', normalize_wellfound_row),
        ('naukri_live_jobs (2).csv', normalize_naukri_row)
    ]

    total_produced = 0
    total_indian = 0
    estimated_total = 92762 if not limit_per_file else (limit_per_file * len(files_config))

    for fname, norm_func in files_config:
        if not os.path.exists(fname):
            print(f"[Warning] File {fname} not found. Skipping.")
            continue

        print(f"\n[Ingesting] Reading raw file: {fname}...")
        try:
            df = pd.read_csv(fname, on_bad_lines='skip')
            if limit_per_file:
                df = df.head(limit_per_file)

            file_count = 0
            for _, row in df.iterrows():
                event = norm_func(row.to_dict())
                publish_job_event(producer, event, buffer_fp)
                total_produced += 1
                file_count += 1
                if event.get('is_indian_location'):
                    total_indian += 1

                if progress_callback and (total_produced % 300 == 0 or file_count == len(df)):
                    progress_callback(total_produced, estimated_total, fname, total_indian)

            print(f"  --> Ingested {file_count} records from {fname}")
        except Exception as e:
            print(f"  [Error] Failed processing {fname}: {e}")

    if producer:
        producer.flush()
        producer.close()
        print("\n[Kafka Producer] All records published & flushed to Kafka topic 'raw_job_postings'!")
    else:
        buffer_fp.close()
        print(f"\n[Stream Buffer] All records written to local stream buffer '{BUFFER_FILE}' ({total_produced} total events, {total_indian} Indian locations)!")

    return total_produced, total_indian


if __name__ == "__main__":
    run_ingestion_pipeline(limit_per_file=50)
