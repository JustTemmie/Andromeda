import json
import os 

if __name__ == "__main__":
    import sys
    sys.path.append(".")
    
import modules.generic_helpers as generic_helpers

success = 1

for file in os.listdir("assets/language_data"):
    if file.endswith(".json5"):
        with open(f"assets/language_data/{file}", "r") as f:
            json5_str = f.read()
            json_str = generic_helpers.json5_to_json(json5_str)
            
            try:
                json.loads(json_str)
                print(f"successfully parsed assets/language_data/{file}!")
                
            except:
                print(f"failed to parse assets/language_data/{file}")
                success = 0

try:
    import settings
    print("successfully imported settings.py!")
except:
    print("failed to import settings.py")
    success = 0

if success:
    exit()

else:
    exit(1)
