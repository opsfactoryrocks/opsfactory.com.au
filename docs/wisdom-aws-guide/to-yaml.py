import yaml
import json
import os

sections = {}
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".md"):
            sroot = root.split('/')
            if len(sroot) > 1:
                sroot = sroot[1]+" (DRAFT)"
                if not sroot in sections:
                    sections[sroot] = []

                fsplit = file.split('.')[0].capitalize().replace('-', ' ')
                # sections[sroot[1]][fsplit] = []
                sections[sroot].append({fsplit: sroot + "/" + file})

print yaml.dump(sections)