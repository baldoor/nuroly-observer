"""
Shodan API Command - Search for internet-connected devices
"""
import os

# Import shodan library (install with: pip install shodan)
try:
    import shodan as shodan_lib
    SHODAN_AVAILABLE = True
except ImportError:
    SHODAN_AVAILABLE = False

aliases = ["sh", "sho"]
description = "Query Shodan API for device information"

# Get API key from environment variable
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")


def execute(args):
    """
    Query Shodan API for device/service information.
    
    Usage:
        !shodan help                - Show this help message
        !shodan host <IP>           - Get info about a specific host
        !shodan domain <domain>     - Get info about a domain/URL
        !shodan search <query>      - Search for devices (limit 10)
        !shodan myip                - Get info about your IP
        !shodan count <query>       - Count results for a query
        !shodan dns <domain>        - Get DNS records for a domain
    
    Examples:
        !shodan help
        !shodan host 8.8.8.8
        !shodan domain google.com
        !shodan search apache country:DE
        !shodan count nginx
        !shodan dns github.com
        !shodan myip
    """
    
    # Check if shodan library is installed
    if not SHODAN_AVAILABLE:
        return "❌ Shodan library not installed. Run: `pip install shodan`"
    
    # Check if API key is configured
    if not SHODAN_API_KEY:
        return "❌ SHODAN_API_KEY environment variable not set!"
    
    # Check if arguments were provided
    if not args:
        return _get_usage()
    
    # Initialize API
    try:
        api = shodan_lib.Shodan(SHODAN_API_KEY)
    except Exception as e:
        return f"❌ Failed to initialize Shodan API: {str(e)}"
    
    # Parse command
    command = args[0].lower()
    
    try:
        if command == "help":
            return _get_usage()
        
        elif command == "host" and len(args) >= 2:
            return _query_host(api, args[1])
        
        elif command == "domain" and len(args) >= 2:
            domain = args[1].replace('http://', '').replace('https://', '').split('/')[0]
            return _query_domain(api, domain)
        
        elif command == "dns" and len(args) >= 2:
            domain = args[1].replace('http://', '').replace('https://', '').split('/')[0]
            return _query_dns(api, domain)
        
        elif command == "search" and len(args) >= 2:
            query = " ".join(args[1:])
            return _search_devices(api, query)
        
        elif command == "count" and len(args) >= 2:
            query = " ".join(args[1:])
            return _count_results(api, query)
        
        elif command == "myip":
            return _get_my_ip(api)
        
        else:
            return _get_usage()
            
    except shodan_lib.APIError as e:
        return f"❌ Shodan API Error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def _query_host(api, ip):
    """Query information about a specific host"""
    try:
        host = api.host(ip)
        
        # Format response
        response = f"🌐 **Shodan Host Information: {ip}**\n\n"
        response += f"**Organization:** {host.get('org', 'N/A')}\n"
        response += f"**ISP:** {host.get('isp', 'N/A')}\n"
        response += f"**Country:** {host.get('country_name', 'N/A')} ({host.get('country_code', 'N/A')})\n"
        response += f"**City:** {host.get('city', 'N/A')}\n"
        response += f"**Hostnames:** {', '.join(host.get('hostnames', ['None']))}\n"
        response += f"**Domains:** {', '.join(host.get('domains', ['None']))}\n"
        response += f"**Open Ports:** {len(host.get('ports', []))} port(s)\n\n"
        
        # List open ports and services
        if host.get('data'):
            response += "**Services:**\n"
            for item in host['data'][:5]:  # Limit to first 5 services
                port = item.get('port', 'N/A')
                product = item.get('product', 'Unknown')
                version = item.get('version', '')
                transport = item.get('transport', 'tcp')
                
                response += f"  • Port {port}/{transport}: {product}"
                if version:
                    response += f" {version}"
                response += "\n"
            
            if len(host['data']) > 5:
                response += f"  ... and {len(host['data']) - 5} more services\n"
        
        return response
        
    except shodan_lib.APIError as e:
        return f"❌ Host not found or API error: {str(e)}"


def _search_devices(api, query, limit=10):
    """Search for devices matching a query"""
    try:
        results = api.search(query, limit=limit)
        
        total = results['total']
        matches = results['matches']
        
        response = f"🔍 **Shodan Search Results**\n\n"
        response += f"**Query:** {query}\n"
        response += f"**Total Results:** {total:,}\n"
        response += f"**Showing:** {len(matches)} result(s)\n\n"
        
        for i, result in enumerate(matches, 1):
            ip = result.get('ip_str', 'N/A')
            port = result.get('port', 'N/A')
            org = result.get('org', 'Unknown')
            location = f"{result.get('location', {}).get('country_name', 'Unknown')}"
            
            response += f"**{i}. {ip}:{port}**\n"
            response += f"   Org: {org} | Location: {location}\n"
            
            # Add product/service info if available
            product = result.get('product', '')
            if product:
                response += f"   Service: {product}\n"
            
            response += "\n"
        
        return response
        
    except shodan_lib.APIError as e:
        return f"❌ Search error: {str(e)}"


def _count_results(api, query):
    """Count results for a query without retrieving data"""
    try:
        result = api.count(query)
        total = result['total']
        
        response = f"📊 **Shodan Query Count**\n\n"
        response += f"**Query:** {query}\n"
        response += f"**Total Results:** {total:,}\n"
        
        return response
        
    except shodan_lib.APIError as e:
        return f"❌ Count error: {str(e)}"


def _get_my_ip(api):
    """Get information about your current IP"""
    try:
        my_ip = api.tools.myip()
        return f"🌐 **Your IP Address:** {my_ip}\n\nUse `!shodan host {my_ip}` for more details."
        
    except shodan_lib.APIError as e:
        return f"❌ Error: {str(e)}"


def _query_domain(api, domain):
    """Query information about a domain"""
    try:
        info = api.dns.domain_info(domain)
        
        response = f"🌍 **Shodan Domain Information: {domain}**\n\n"
        
        # Domain details
        if 'domain' in info:
            response += f"**Domain:** {info['domain']}\n"
        
        if 'tags' in info and info['tags']:
            response += f"**Tags:** {', '.join(info['tags'])}\n"
        
        # Subdomains
        if 'subdomains' in info and info['subdomains']:
            response += f"\n**Subdomains:** ({len(info['subdomains'])})\n"
            for subdomain in info['subdomains'][:10]:  # Limit to 10
                response += f"  • {subdomain}\n"
            if len(info['subdomains']) > 10:
                response += f"  ... and {len(info['subdomains']) - 10} more\n"
        
        # A records (IPs)
        if 'data' in info:
            ips = set()
            for record in info['data']:
                if 'value' in record and record.get('type') == 'A':
                    ips.add(record['value'])
            
            if ips:
                response += f"\n**IP Addresses:** ({len(ips)})\n"
                for ip in list(ips)[:5]:
                    response += f"  • {ip}\n"
                if len(ips) > 5:
                    response += f"  ... and {len(ips) - 5} more\n"
        
        return response
        
    except shodan_lib.APIError as e:
        # If domain info doesn't work, try a simple hostname search
        try:
            results = api.search(f"hostname:{domain}", limit=5)
            
            response = f"🌍 **Shodan Domain Search: {domain}**\n\n"
            response += f"**Total Results:** {results['total']:,}\n\n"
            
            if results['matches']:
                response += "**Associated IPs:**\n"
                for match in results['matches']:
                    ip = match.get('ip_str', 'N/A')
                    port = match.get('port', 'N/A')
                    product = match.get('product', 'Unknown')
                    response += f"  • {ip}:{port} - {product}\n"
            
            return response
        except:
            return f"❌ Domain not found or API error: {str(e)}"


def _query_dns(api, domain):
    """Query DNS records for a domain"""
    try:
        dns_info = api.dns.resolve(domain)
        
        response = f"📡 **DNS Records: {domain}**\n\n"
        
        if dns_info:
            response += "**IP Addresses:**\n"
            for ip in dns_info:
                response += f"  • {ip}\n"
            
            response += f"\nUse `!shodan host <IP>` to get details about an IP."
        else:
            response += "No DNS records found."
        
        return response
        
    except shodan_lib.APIError as e:
        return f"❌ DNS lookup error: {str(e)}"


def _get_usage():
    """Return usage information"""
    return """📖 **Shodan Command Usage**

**Available commands:**
  • `!shodan help` - Show this help message
  • `!shodan host <IP>` - Get info about a specific IP
  • `!shodan domain <domain>` - Get info about a domain/URL
  • `!shodan dns <domain>` - Get DNS records
  • `!shodan search <query>` - Search for devices
  • `!shodan count <query>` - Count results
  • `!shodan myip` - Get your current IP

**Examples:**
  • `!shodan host 8.8.8.8`
  • `!shodan domain google.com`
  • `!shodan domain https://github.com`
  • `!shodan dns microsoft.com`
  • `!shodan search apache country:DE`
  • `!shodan search hostname:example.com`
  • `!shodan count nginx`

**Common search filters:**
  • `hostname:example.com` - Specific hostname
  • `country:DE` - Germany
  • `city:Berlin` - Specific city
  • `port:22` - Specific port
  • `os:Windows` - Operating system
  • `product:Apache` - Specific product
"""
