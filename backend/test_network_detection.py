#!/usr/bin/env python3
"""
Test network detection without dependencies
"""
import socket
import ipaddress

def test_network_detection():
    """Test the network detection logic"""
    networks = []
    
    try:
        # Fallback method: try to connect to a remote address to find local IP
        try:
            # Connect to a public DNS server to find our actual IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                
            if not local_ip.startswith('127.'):
                network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
                networks.append(network)
                print(f"Found network via socket method: {network}")
                return networks
                
        except Exception as e:
            print(f"Socket method failed: {e}")
        
        # Last resort: hostname method (original logic)
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        if not local_ip.startswith('127.'):
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            networks.append(network)
            print(f"Found network via hostname: {network}")
            return networks
        
    except Exception as e:
        print(f"Error getting local network: {e}")
    
    # Final fallback to common private networks
    networks = [
        ipaddress.IPv4Network("10.0.0.0/24"),      # Common for home routers
        ipaddress.IPv4Network("192.168.1.0/24"),   # Very common for home routers  
        ipaddress.IPv4Network("192.168.0.0/24"),   # Common for home routers
        ipaddress.IPv4Network("192.168.2.0/24"),   # Some routers use this
    ]
    print("Using fallback networks")
    
    return networks

def test_ip_ranges():
    """Test IP range generation"""
    networks = test_network_detection()
    
    for network in networks:
        print(f"\nTesting network: {network}")
        hosts = list(network.hosts())
        
        # For 10.0.0.x network, scan more comprehensively around common device IPs
        if str(network.network_address).startswith("10.0.0"):
            print("  This is a 10.0.0.x network - generating targeted IP ranges")
            
            # Test specific ranges where devices are commonly found
            device_ranges = [
                range(80, 90),     # Focus on 80s where user's device is at 86
                range(1, 20),      # Router and infrastructure: 1-19
                range(50, 70),     # Common device range: 50-69
                range(70, 100),    # Extended device range: 70-99
                range(100, 120),   # Higher device range: 100-119
                range(200, 210)    # High range devices: 200-209
            ]
            
            test_ips = []
            for ip_range in device_ranges:
                for i in ip_range:
                    if i <= 254:  # Valid IP range
                        test_ips.append(f"10.0.0.{i}")
            
            # Remove duplicates while preserving order
            test_ips = list(dict.fromkeys(test_ips))
            print(f"  Generated {len(test_ips)} IPs to test")
            
            # Check if 10.0.0.86 is included
            if "10.0.0.86" in test_ips:
                print("  ✅ 10.0.0.86 is included in the scan range")
                print(f"  IPs around 86: {[ip for ip in test_ips if '10.0.0.8' in ip]}")
            else:
                print("  ❌ 10.0.0.86 is NOT included in the scan range")
        else:
            print(f"  Not a 10.0.0.x network, would use different logic")

if __name__ == "__main__":
    test_ip_ranges()
