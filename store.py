import pyshark
import csv
import time

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
            print(f'Processing packet number {pktcount}')
            
            try:
                # Extract features from the packet
                bytecount = int(packet.length)
                timestamp = float(packet.sniff_time.timestamp())  # Timestamp in seconds
                dur = int(timestamp * 1e6)  # Current time in microseconds
                dur_nsec = int(time.time_ns() % 1e9)  # Nanoseconds
                tot_dur = dur + (dur_nsec / 1e3)  # Total duration in microseconds
                flows = pktcount  # Simplified for example
                packetins = 1  # Simplified for example
                pktperflow = pktcount / flows if flows else 0
                byteperflow = bytecount / flows if flows else 0
                pktrate = pktcount / (tot_dur / 1e6) if tot_dur else 0
                Pairflow = 1  # Simplified for example
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
                tx_kbps = (tx_bytes * 8) / 1e3 if tx_bytes else 0
                rx_kbps = (rx_bytes * 8) / 1e3 if rx_bytes else 0
                tot_kbps = tx_kbps + rx_kbps

                # Print the extracted features
                print(f'Packet Count: {pktcount}')
                print(f'Byte Count: {bytecount}')
                print(f'Timestamp: {timestamp}')
                print(f'Duration: {dur}')
                print(f'Duration Nanoseconds: {dur_nsec}')
                print(f'Total Duration: {tot_dur}')
                print(f'Flows: {flows}')
                print(f'Packet Ins: {packetins}')
                print(f'Packets per Flow: {pktperflow}')
                print(f'Bytes per Flow: {byteperflow}')
                print(f'Packet Rate: {pktrate}')
                print(f'Pair Flow: {Pairflow}')
                print(f'Protocol: {Protocol}')
                print(f'Source Port: {src_port}')
                print(f'Destination Port: {dst_port}')
                print(f'Transmit Bytes: {tx_bytes}')
                print(f'Receive Bytes: {rx_bytes}')
                print(f'Transmit Kbps: {tx_kbps}')
                print(f'Receive Kbps: {rx_kbps}')
                print(f'Total Kbps: {tot_kbps}')

                # Write the data to the CSV file
                writer.writerow([
                    pktcount, bytecount, dur, dur_nsec, tot_dur,
                    flows, packetins, pktperflow, byteperflow,
                    pktrate, Pairflow, Protocol, src_port, dst_port,
                    tx_bytes, rx_bytes, tx_kbps, rx_kbps, tot_kbps
                ])

            except AttributeError as e:
                print(f'Packet processing error: {e}')
            except Exception as e:
                print(f'General error: {e}')
    except KeyboardInterrupt:
        print('Packet capture stopped by user.')
    except Exception as e:
        print(f'Capture error: {e}')
    finally:
        print('Stopping packet capture.')
