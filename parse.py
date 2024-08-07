import pyshark
import csv
import requests
import time

# Define the FastAPI endpoint URL
fastapi_url = 'http://127.0.0.1:8000/predict'

# Define the CSV file path
csv_file_path = 'packet_data.csv'

# Open the CSV file for writing
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow([
        'pktcount', 'bytecount', 'dur', 'dur_nsec', 'tot_dur',
        'flows', 'packetins', 'pktperflow', 'byteperflow',
        'pktrate', 'Pairflow', 'Protocol', 'src_port', 'dst_port',
        'tx_bytes', 'rx_bytes', 'tx_kbps', 'rx_kbps', 'tot_kbps'
    ])

    print('Starting packet capture... Press Ctrl+C to stop.')

    # Capture live packets
    capture = pyshark.LiveCapture(interface='wlo1')

    try:
        pktcount = 0  # Initialize packet count

        for packet in capture.sniff_continuously():
            pktcount += 1  # Increment packet count
            timestamp = float(packet.sniff_time.timestamp())  # Timestamp in seconds
            print(f'Timestamp: {timestamp}')

            try:
                # Extract features from the packet
                bytecount = int(packet.length)
                dur = int(timestamp * 1e6)  # Current time in microseconds
                dur_nsec = int(time.time_ns() % 1e9)  # Nanoseconds
                tot_dur = int(dur + (dur_nsec / 1e3))  # Total duration in microseconds
                flows = pktcount  # Simplified for example
                packetins = 1  # Simplified for example
                pktperflow = int(pktcount / flows) if flows else 0
                byteperflow = int(bytecount / flows) if flows else 0
                pktrate = int(pktcount / (tot_dur / 1e6)) if tot_dur else 0
                Pairflow = 1  # Simplified for example

                # Extract protocol information
                Protocol = packet.transport_layer if hasattr(packet, 'transport_layer') else 'unknown'

                # Extract source and destination ports
                src_port = 0
                dst_port = 0
                if hasattr(packet, 'tcp'):
                    src_port = int(packet.tcp.srcport) if hasattr(packet.tcp, 'srcport') else 0
                    dst_port = int(packet.tcp.dstport) if hasattr(packet.tcp, 'dstport') else 0
                elif hasattr(packet, 'udp'):
                    src_port = int(packet.udp.srcport) if hasattr(packet.udp, 'srcport') else 0
                    dst_port = int(packet.udp.dstport) if hasattr(packet.udp, 'dstport') else 0

                tx_bytes = int(packet.length)  # Simplified for example
                rx_bytes = int(packet.length)  # Simplified for example
                tx_kbps = int((tx_bytes * 8) / 1e3) if tx_bytes else 0
                rx_kbps = int((rx_bytes * 8) / 1e3) if rx_bytes else 0
                tot_kbps = tx_kbps + rx_kbps

                # Prepare the data payload for FastAPI
                data_payload = {
                    'pktcount': pktcount,
                    'bytecount': bytecount,
                    'dur': dur,
                    'dur_nsec': dur_nsec,
                    'tot_dur': tot_dur,
                    'flows': flows,
                    'packetins': packetins,
                    'pktperflow': pktperflow,
                    'byteperflow': byteperflow,
                    'pktrate': pktrate,
                    'Pairflow': Pairflow,
                    'Protocol': Protocol,
                    'port_no': src_port,  # Use src_port for port_no if it's the expected field
                    'tx_bytes': tx_bytes,
                    'rx_bytes': rx_bytes,
                    'tx_kbps': tx_kbps,
                    'rx_kbps': rx_kbps,
                    'tot_kbps': tot_kbps
                }

                # Write the data to the CSV file
                writer.writerow([
                    pktcount, bytecount, dur, dur_nsec, tot_dur,
                    flows, packetins, pktperflow, byteperflow,
                    pktrate, Pairflow, Protocol, src_port, dst_port,
                    tx_bytes, rx_bytes, tx_kbps, rx_kbps, tot_kbps
                ])

                # Send the data to the FastAPI endpoint
                response = requests.post(fastapi_url, json=data_payload)
                if response.status_code == 200:
                    prediction = response.json().get('prediction')
                    print(f'Prediction: {prediction}')
                else:
                    print(f'Failed to get prediction: {response.status_code}')
                    print(f'Response content: {response.text}')
            
            except AttributeError as e:
                print(f'Packet processing error: {e}')
            except requests.exceptions.RequestException as e:
                print(f'Request error: {e}')
            except Exception as e:
                print(f'General error: {e}')
    except KeyboardInterrupt:
        print('Packet capture stopped by user.')
    except Exception as e:
        print(f'Capture error: {e}')
    finally:
        print('Stopping packet capture.')
