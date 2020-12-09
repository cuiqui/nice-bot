# nice-bot
![dank_icon](images/dank_icon.png?raw=true "Dank icon")

Discord niceness dank bot tracker. It will keep track of every nice comment made within the case insensitive regex: `(?<!\S)n+i+c+e+(?!\S)`, in a context-free grammar. If it has any mentions or quotes, it will also keep track of them.

One service of the bot supports being included in multiple servers, metrics and quotes won't collide. Bare in mind that it is not meant to be used in 200 servers with 5000 members each; I mean, if `pandas` can support it then you're free to try, but whatever, man.

### Install

#### Debian route

It's a debian package, you should do it inside a virtual environment.

1. Install all dependencies inside `debian/control`
2. Run in project root `debuild -us -uc` and then `debuild clean`.
3. Finally in parent dir `sudo dpkg -i nice-bot_<version>_<architecture>.deb`

#### Poetry route (for development)

If you have [Poetry](https://python-poetry.org/docs/) installed:

1. Clone repository.
2. `poetry install` to generate venv with dependencies.
3. `bash scripts/install.sh` to create necessary directories.
4. `poetry run nicebot` to start the bot service.

### Usage
If went the debian route, there is a systemd service for the bot: `service nicebot start`.
If you are using poetry, go into the repository and run `poetry run nicebot` to start the bot.

Logs are in `/var/log/nice-bot/bot.log`, but you can manipulate it as you want in configuration file.

### Development

#### Without poetry:

1. Clone repo.
2. `virtualenv --python=python3.7 venv`
3. `. venv/bin/activate`
4. `pip install -e . -r requirements.txt`
5. `bash scripts/install.sh`
6. `python bot/service.py`

#### With poetry:

1. Clone repo
2. `poetry install`
3. `bash scripts/install.sh`
4. `poetry run nicebot`


### Configuration
This project uses [confight](https://github.com/Avature/confight), so configs are read in the following fashion:
1. `/etc/nice-bot/config.toml`
2. `/etc/nice-bot/conf.d/*`

Secrets and other overrides should be put inside `conf.d` folder in order to guarantee a clean debian installation.

    [bot]
        # Token to connect with discord API
        token = ''

        # Path to CSV database
        csv = '/var/lib/nice-bot/db.csv'

        # Spam probability
        spam = 0.1

    [logging]
        # logging.config.dictConfig configuration
        version = 1
        [logging.formatters]
            [logging.formatters.default]
                format = '[%(asctime)s] [%(levelname)s] %(message)s'
        [logging.handlers]
            [logging.handlers.file]
                class = 'logging.FileHandler'
                formatter = 'default'
                filename = '/var/log/nice-bot/bot.log'
        [logging.root]
            handlers = ['file']
            level = 'INFO'



### Interface
    Commands:
      bad-bot          <feedback: str> Help us improve!
      my-nice-messages Retrieve messages that made people go like 'nice'
      nice-elo         Returns elo niceness evolution
      nice-fact        Cheers you up with a nice wholesome beautiful sweet sugary...
      nice-messages    <user: @mention> Retrieve messages that made people go lik...
      nice-metrics     Retrieve nice leaderboard
      nice-team-elo    Returns team elo niceness evolution
      nice-wisdom      Retrieve random nice quote
    ​No Category:
      nice-help        Shows this message

    Type !nice-help command for more info on a command.
    You can also type !nice-help category for more info on a category.

### Metrics

You can ask the bot to retrieve the extremely nice leaderboard of nice people:

![nice_metrics](images/nice_metrics.png?raw=true "Nice metrics")

### Wisdom
You can ask the bot to retrieve nice ancient wisdom:

![nice_wisdom](images/nice_wisdom.png?raw=true "Nice wisdom")

### Feedback!
Encourage your users to give feedback on the bot, `bad-bot` takes a string as an argument and stores the user's feedback.
