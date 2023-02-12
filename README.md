# cinnabot-python
Cinnabot-python is the codebase for @cinnabot, a Telegram bot that assists NUSC students with their day-to-day needs. Please note that there is a previous codebase named "cinnabot", but that has been made redundant due to the rewriting of all the code into Python. Therefore, only this codebase is kept up to date.


**base.py**: Provides instructions and content for commands _/start_, _/about_ and _/help_ in Cinnabot. _/about_ provides a useful list of weblinks and residential living apps for NUSC students. _/help_ provides users more information on the various features of Cinnabot.

**claims.py**: Instructions for _/claims_, guiding users to follow a constrained list of steps to submit claims for reimbursements and fund requests at NUSC.

**feedback.py**: Instructions for _/feedback_, which provides users 2 key buttons to pick from: Office of Housing Services (OHS) and University Scholars Club. Users are directed to the OHS Feedback Form or asked about which stall they ate at respectively.

**resources.py**: Instructions for _/resources_, which provides users 4 key buttons to pick from: Channels, Interest Groups, Check Aircon Meter and Care Mental Health. Resources are provided for each of these areas through relevant links to NUSC channels, interest groups, aircon meter bot (@nusairconbot) and mental health bot (@asafespacebot).  

**spaces.py**: Instructions for _/spaces_, including drawing out data from an internal database of bookings so that users can view all bookings. Users are able to display bookings now, this week, a specific day or across a specific range of dates, as well as directly make bookings.

**travel.py**: Instructions for _/map_ which provides users with a map of the area of NUS that they are in.

**utils.py**: Contains Abstract Base Classes (ABCs) (code structures) that developers should follow and utilise for any coding through cinnabot-python.


## Linux server deployment
Temporary solution for deploying on `stu.comp.nus.edu.sg`
Note that **tmux sessions do not sync between stu1 and stu2**
_May need to log in and out to get back on the correct host_
```
# optional, depending on setup
# We used conda to install python and packages
conda activate cinnabot
# tmux is used for persistence
tmux
# In a new tmux window
ngrok http 5000
# In another tmux window / pane
python prepenv.py
source environments.var
python main.py
```

## Conda installation
```
ssh user@stu.comp.nus.edu.sg

# https://github.com/conda-forge/miniforge/releases
wget https://github.com/conda-forge/miniforge/releases/download/22.9.0-3/Mambaforge-22.9.0-3-Linux-x86_64.sh

chmod u+x Mambaforge-22.9.0.3-Linux-x86-64.sh

./Mambaforge-22.9.0.3-Linux-x86_64.sh


git clone https://github.com/usdevs/cinnabot-python.git
# Create the conda environment
conda env create -f cinnabot_environment.yml -n cinnabot

# Downloading ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvf ngrok-v3-stable-linux-amd64.tgz

# Suggestion: add ngrok executable file to your PATH so you can just call ngrok

# Add ngrok auth token
ngrok config add-authtoken []

```

