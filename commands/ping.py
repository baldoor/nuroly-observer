import subprocess
import platform

# Optional: Define shortcuts for this command
aliases = ["p"]

def execute(args):
    """
    Executes a real ICMP ping to a given host.
    Default host is 8.8.8.8 if no argument is provided.
    """
    host = args[0] if args else "8.8.8.8"
    
    # Platform specific parameters (-n for Windows, -c for Unix)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]

    try:
        # Use run() with proper encoding for Windows German output
        result = subprocess.run(
            command, 
            capture_output=True, 
            encoding='cp1252',  # Windows German encoding
            errors='replace',    # Replace encoding errors instead of failing
            timeout=5
        )
        
        # Safely combine stdout and stderr
        output = (result.stdout or "") + (result.stderr or "")
        
        # Support both English "time=" and German "Zeit=" in ping output
        if "time=" in output.lower() or "zeit=" in output.lower():
            # Minimalistic parsing of the latency - find the line with time/zeit
            for line in output.splitlines():
                if "time=" in line.lower() or "zeit=" in line.lower():
                    return f"✅ Ping to {host} successful.\n`{line.strip()}`"
            return f"✅ {host} is up."
        
        # Check for common failure messages in German and English
        if "host" in output.lower() or "ziel" in output.lower() or result.returncode != 0:
            return f"❌ Failed to reach {host}."
            
        return f"✅ {host} responded."
    except subprocess.TimeoutExpired:
        return f"❌ Timeout: {host} did not respond."
    except Exception as e:
        return f"❌ Error pinging {host}: {str(e)}"