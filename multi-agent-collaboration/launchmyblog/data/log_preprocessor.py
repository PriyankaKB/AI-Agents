import re
import json

# Regex tuned for Scrapy log format
log_pattern = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+'   # timestamp
    r'\[(?P<module>[^\]]+)\]\s+'                                # module in brackets
    r'(?P<level>[A-Z]+):\s+'                                    # log level
    r'(?P<message>.*)$'                                         # message
)

input_file = "django.log"
output_file = "django_logs.jl"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        line = line.strip()
        if not line:
            continue
        match = log_pattern.match(line)
        if match:
            record = {
                "timestamp": match.group("timestamp"),
                "module": match.group("module"),
                "level": match.group("level"),
                "message": match.group("message")
            }
            outfile.write(json.dumps(record) + "\n")
        else:
            # fallback: write unmatched lines as raw message
            record = {
                "timestamp": None,
                "module": None,
                "level": None,
                "message": line
            }
            outfile.write(json.dumps(record) + "\n")
