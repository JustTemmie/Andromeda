import json
import os 

if __name__ == "__main__":
    import sys
    sys.path.append(".")
    
import modules.helpers as helpers

success = 1

for file in os.listdir("assets/language_data"):
    if file.endswith(".json5"):
        with open(f"assets/language_data/{file}", "r") as f:
            json5_str = f.read()
            json_str = helpers.json5_to_json(json5_str)
            
            try:
                json.loads(json_str)
                print(f"assets/language_data/{file} verified!")
                
            except:
                print(f"failed to parse assets/language_data/{file}")
                success = 0

try:
    import settings
    print("settings.py verified!")
except:
    print("failed to import settings.py")
    success = 0

if success:
    exit()

else:
    exit(1)
