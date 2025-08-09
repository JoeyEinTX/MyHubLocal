#!/usr/bin/env python3
"""
Simple CoIoT listener to debug multicast traffic
"""
import socket
import struct
import time

def listen_for_multicast():
    """Listen for any multicast traffic on the CoIoT port"""
    MULTICAST_GROUP = "224.0.1.187"
    PORT = 5683
    
    print(f"Listening for multicast traffic on {MULTICAST_GROUP}:{PORT}")
    print("Press Ctrl+C to stop")
    
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to the port
    sock.bind(('', PORT))
    
    # Join multicast group
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Set a timeout so we can check for interrupts
    sock.settimeout(1.0)
    
    try:
        packet_count = 0
        start_time = time.time()
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                packet_count += 1
                
                print(f"\n--- Packet {packet_count} from {addr[0]}:{addr[1]} ---")
                print(f"Length: {len(data)} bytes")
                
                # Try to decode as text
                try:
                    text = data.decode('utf-8', errors='ignore')
                    print(f"Text: {text[:200]}{'...' if len(text) > 200 else ''}")
                except:
                    pass
                
                # Show hex dump of first 100 bytes
                hex_data = data[:100].hex()
                print(f"Hex:  {' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))}")
                
                # Check if it looks like a Shelly packet
                if b'shelly' in data.lower() or b'coiot' in data.lower():
                    print("*** Potential Shelly CoIoT packet! ***")
                
            except socket.timeout:
                # Check if we should continue
                elapsed = time.time() - start_time
                if elapsed > 30:  # Stop after 30 seconds if no packets
                    print(f"\nNo packets received in 30 seconds. Stopping.")
                    break
                continue
            except KeyboardInterrupt:
                break
    
    finally:
        print(f"\nReceived {packet_count} total packets")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        sock.close()

if __name__ == "__main__":
    listen_for_multicast()
