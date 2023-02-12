import os
import subprocess
import json
import pathlib
"""
Attempts to get the public url of the ngrok tunnel,
assumes the tunnel in use is the first one in the 
dictionary returned by the API
quick hack till we can get azure running...

"""
def get_ngrok_host():
    try:
        # Attempt to get the public api
        # ngrok api endpoints list
        result = subprocess.run(["~/bin/ngrok api endpoints list"], shell=True, capture_output=True)

        print(result.stdout.decode())
        # print(result.stderr)

        result_dict = json.loads(result.stdout)
        # print(result_dict)

        public_url = result_dict["endpoints"][0]["public_url"][8:]
        return public_url
    except Exception as e:
        print("Make sure ngrok is running")
        print("ngrok http 5000")
        raise e

def create_file(path, token, host):
    with open(path, 'w') as f:
        f.write(f'export TOKEN="{token}"\n')
        f.write(f'export HOST="{host}"\n')


env_file = pathlib.Path("environments.var")
if env_file.exists():
    print("Existing environment file found")
    with open(env_file, 'r') as f:
        token = f.readline().split('"')[1]
        token = token[1:len(token)-1]
    print(f"Token prefix {token[:8]}")
    create_file(env_file, token, get_ngrok_host())
    print(f"Environment file created: {env_file}")
else:
    print("File not found, creating")
    token = input("Enter token: ")
    create_file(env_file, token, get_ngrok_host())
    print(f"New environment file created: {env_file}")

print("""
Next steps to deploy:  
----------------------- 
conda activate cinnabot 
source environments.var 
python main.py\n""")

