# What is Instabot

Instabot is a little program developped to automatically post comments on the last picture posted by specific users on Instagram using a headless browser. The bost is developped in Python3.7 and can be deployed easily on a RaspberryPi.

## Usage

The entry point in the program is the file `main.py`.
The script accept one optional parameter `-d` or `--display` that can be used to run the script with the browser visible (mainly used to understand what the bot is doing and debugging).
The script generate screenshot after each run that can be found in the `debug` folder.
You can redirect the bot logs in Slack for easy monitoring (especially if you deploy the bot on a RaspberryPi) by providing a slack token in the environnement variables (see #Installation below).

## Installation

**Instabot** is developped on `Python3.7`. You can find Python3.7 [here](https://www.python.org/downloads/release/python-371/).
To run the bot you also need google chrome installed on your computer and you need to find the installation path of the application (for example on mac it is ~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome)
You also need to download the Chromedriver used by python to remotely control chrome. You can find the latest version of Chromedriver [here](http://chromedriver.chromium.org/). You will also need the path to the chromedriver itself.

To install **Instabot**:

- Clone instabot repo

```bash
git clone
```

- [Optional] I encourage you to use a python virtual env (see [here](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) for details on virtual env and [here](http://mkelsey.com/2013/04/30/how-i-setup-virtualenv-and-virtualenvwrapper-on-my-mac/) for details on virtualenvwrapper to handle env variables more easily). Activate your virtualenv

- Install dependencies from requirements.txt

```bash
pip install -r requirements.txt
```

- Setup the following env variables necessary to run the code. You can also copy the file `.env.sample`, populate it and rename it `.env` (If using virtualenvwrapper a tuto is available [here](https://stackoverflow.com/questions/9554087/setting-an-environment-variable-in-virtualenv)):
  - IG_USERNAME --> Username of IG account
  - IG_PASSWORD --> Password of IG account
  - CHROME_BINARY_PATH --> Path retrieved after installing the chromium-browser
  - CHROMEDRIVER_PATH --> Path where the chromedriver was unpacked
  - [OPTIONAL] SLACK_TOKEN --> Slack auth token (you will need to create a new app and give it write access to a slack  - channel to get a token. See [here](https://api.slack.com/apps))

- You need to add two text files in the folder `source`:
  - profilelist.txt --> contain the profile handle of the people you want to comment on. (separate the handle with a new line. You can find the profile handle on the url of the IG web client. The profile names should look like that `[profile_name]/`)
  - insta_comment.txt --> contain the comments you want to post (you add more than one comment in new lines. The bot will randomly select a comment to post during each run
  
- Run the code

```bash
python main.py
```

### How to run Instabot on a RaspberryPi

#### Raspi setup

- Install rasbian stretch using [Etcher](https://www.raspberrypi.org/documentation/installation/installing-images/)
- [Optional] Add auto ssh connection if no keyboard and screen (on the sd card navigate to the `boot` partition. In the root add a file called `ssh` no extension. The RasPi will connect to the network and enable ssh at startup.)
- [Optional] Install Dataplicity to be able to remote access the raspberry pi from your personal computer over the web.

#### Instabot raspi setup

- [Optional] Install python 3.7 ([tuto](http://www.ramoonus.nl/2018/06/30/installing-python-3-7-on-raspberry-pi/)) The code was updated to work with Python 3.5 installed by defauklt on the latest version of rasbian stretch.
- Install chromium ([tuto](https://tutorials-raspberrypi.com/google-chrome-for-raspberry-pi/)).

```bash
sudo apt-get install chromium-browser
```

- Get chrome webdriver compiled for armh ([tuto1](https://www.raspberrypi.org/forums/viewtopic.php?t=194176) and [tuto2](https://www.reddit.com/r/selenium/comments/7341wt/success_how_to_run_selenium_chrome_webdriver_on/)).

```bash
sudo apt-get install chromium-chromedriver
```

- `dpkg --listfiles chromium-chromedriver` save the path as *CHROMEDRIVER_PATH*
- `which chromium-browser` save the path as *CHROME_BINARY_PATH*.
- Then follow the standard installation process descibed above
