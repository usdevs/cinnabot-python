# cinnabot-python
Cinnabot-python is the codebase for @cinnabot, a Telegram bot that assists NUSC students with their day-to-day needs. Please note that there is a previous codebase named "cinnabot", but that has been made redundant due to the rewriting of all the code into Python. Therefore, only this codebase is kept up to date.


**base.py**: Provides instructions and content for commands _/start_, _/about_ and _/help_ in Cinnabot. _/about_ provides a useful list of weblinks and residential living apps for NUSC students. _/help_ provides users more information on the various features of Cinnabot.

**claims.py**: Instructions for _/claims_, guiding users to follow a constrained list of steps to submit claims for reimbursements and fund requests at NUSC.

**feedback.py**: Instructions for _/feedback_, which provides users 2 key buttons to pick from: Office of Housing Services (OHS) and University Scholars Club. Users are directed to the OHS Feedback Form or asked about which stall they ate at respectively.

**resources.py**: Instructions for _/resources_, which provides users 4 key buttons to pick from: Channels, Interest Groups, Check Aircon Meter and Care Mental Health. Resources are provided for each of these areas through relevant links to NUSC channels, interest groups, aircon meter bot (@nusairconbot) and mental health bot (@asafespacebot).  

**spaces.py**: Instructions for _/spaces_, including drawing out data from an internal database of bookings so that users can view all bookings. Users are able to display bookings now, this week, a specific day or across a specific range of dates.

**travel.py**: Instructions for _/map_ which provides users with a map of the area of NUS that they are in.

**utils.py**: Contains Abstract Base Classes (ABCs) (code structures) that developers should follow and utilise for any coding through cinnabot-python.



**How to make edits to cinnabot-python?**
1. Do a git clone of the repository to your own text editor
2. Create a new branch under your name, and git checkout from the master branch to your own branch
3. Type _pip install python-telegram-bot_ and _pip install google-cloud-firestore_ in the Terminal to download the needed packages beforehand.
4. Change tab name of _config.json.example_ to _config.json_.
5. Go to @BotFather on Telegram and create a new bot by sending _/newbot_. You will be prompted to give a Telegram bot Name and username. Pick anything you like. After which, you will receive an HTTP API key from BotFather.
6. Replace _Enter telegram bot token_ in _config.json_ with this HTTP API key.
7. Type _python main.py_ in the Terminal to activate your new bot. If this does not work, make sure you have downloaded the latest version of Python in your laptop.
8. Use your new bot as a sandbox. Upon making any code changes, check that it works on your own bot before git pushing changes to the master branch.
