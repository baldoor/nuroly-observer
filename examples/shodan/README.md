# Shodan API Integration Example

This example shows how to integrate Shodan API queries into your nuroly-observer project.

## What is Shodan?

Shodan is a search engine for internet-connected devices (IoT, servers, routers, etc.). With the API you can:
- Query information about IP addresses
- Search for specific services/devices
- Find open ports and vulnerabilities
- Perform network reconnaissance

## Setup

### 1. Install Python Library

```bash
pip install shodan
```

### 2. Get a Shodan API Key

1. Register at [https://account.shodan.io/register](https://account.shodan.io/register)
2. Go to your Account Dashboard
3. Copy your API Key

### 3. Add API Key to `.env`

Add the following line to your existing `.env` file in the project root:

```
SHODAN_API_KEY=your_api_key_here
```

## Integration

Copy the `shodan.py` file from this example folder to `commands/shodan.py`:

```powershell
# Windows
Copy-Item .\examples\shodan\shodan.py .\commands\shodan.py

# Linux/Mac
cp ./examples/shodan/shodan.py ./commands/shodan.py
```

Restart the bot and the command will be available!

## Usage

### Basic Commands

**Get help:**
```
!shodan help
!sh help
```

**Query host information:**
```
!shodan host 8.8.8.8
!shodan host 1.1.1.1
```

**Domain/URL information:**
```
!shodan domain google.com
!shodan domain https://github.com
!shodan domain example.org
```

**DNS queries:**
```
!shodan dns google.com
!shodan dns microsoft.com
```

**Search for devices:**
```
!shodan search apache country:DE
!shodan search port:22 country:US
!shodan search nginx city:Berlin
!shodan search hostname:example.com
```

**Count results:**
```
!shodan count nginx
!shodan count port:3389 country:DE
```

**Get your IP address:**
```
!shodan myip
```

### Aliases

You can also use shortcuts:
```
!sh host 8.8.8.8
!sho search nginx
```

## Shodan Search Filters

### Commonly Used Filters

| Filter | Description | Example |
|--------|-------------|----------|
| `country` | Country (ISO code) | `country:DE` |
| `city` | City | `city:Berlin` |
| `port` | Port number | `port:22` |
| `os` | Operating system | `os:Windows` |
| `hostname` | Hostname | `hostname:google` |
| `org` | Organization | `org:Amazon` |
| `product` | Software product | `product:Apache` |
| `version` | Software version | `version:2.4` |
| `net` | IP range (CIDR) | `net:192.168.0.0/16` |
| `hostname` | Hostname/Domain | `hostname:example.com` |

### Example Queries

**Domain information:**
```
!shodan domain github.com
!shodan domain https://www.google.com
!shodan dns cloudflare.com
```

**Hosts of a specific domain:**
```
!shodan search hostname:example.com
!shodan search hostname:.gov country:US
```

**Find insecure webcams:**
```
!shodan search webcam country:DE
```

**RDP servers in Germany:**
```
!shodan search port:3389 country:DE
```

**SSH servers with weak encryption:**
```
!shodan search ssh country:DE
```

**Apache servers in a city:**
```
!shodan search apache city:Berlin
```

**Open databases:**
```
!shodan search mongodb port:27017
!shodan search mysql port:3306
```

## API Limits

The free Shodan API has the following limits:
- **100 results** per month
- **1 scan** per month
- Basic search queries only

For more features, you need a paid API plan.

## Troubleshooting

### "Shodan library not installed"
```bash
pip install shodan
```

### "SHODAN_API_KEY environment variable not set"
- Make sure the API key is added to your `.env` file
- Restart the bot after adding it

### "API Error: Invalid API key"
- Check if your API key is correct
- Log in to Shodan.io and copy the key again

### "API Error: Access denied"
- You have reached your monthly limit
- Wait until next month or upgrade your plan

## Security Notes

⚠️ **Important:**
- Use Shodan only for legal purposes
- Do not scan systems without permission
- Comply with data protection laws in your country
- Never share your API key publicly

## Additional Resources

- [Shodan Documentation](https://developer.shodan.io/)
- [Shodan Python Library](https://shodan.readthedocs.io/)
- [Shodan Search Guide](https://help.shodan.io/the-basics/search-query-fundamentals)
