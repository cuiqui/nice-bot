# nice-bot
![dank_icon](images/dank_icon.png?raw=true "Dank icon")

Discord niceness dank bot tracker. It will keep track of every nice comment made within the case insensitive regex: `(?<!\S)n+i+c+e+(?!\S)`, in a context-free grammar. If it has any mentions or quotes, it will also keep track of them.

One service of the bot supports being included in multiple servers, metrics and quotes won't collide. Bare in mind that it is not meant to be used in 200 servers with 5000 members each; I mean, if `pandas` can support it then you're free to try, but whatever, man.

### Install
It's a debian package, you should do it inside a virtual environment.

1. Install all dependencies inside `debian/control`
2. Run in project root `debuild -us -uc` and then `debuild clean`.
3. Finally in parent dir `sudo dpkg -i nice-bot_<version>_<architecture>.deb`

### Usage
It's a linux daemon coupled with systemd: `service nicebot start`.

Logs are in `/var/log/nice-bot/bot.log`, but you can manipulate it as you want in configuration file.

### Development
1. Clone repo.
2. `virtualenv --python=python3.7 venv`
3. `. venv/bin/activate`
4. `pip install -e . -r requirements.txt`

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
      nice-messages    <user: @mention> Retrieve messages that made people go like 'nice' by user
      nice-metrics     Retrieve nice leaderboard
      nice-wisdom      Retrieve random nice quote
    No Category:
      nice-help         Shows this message

    Type !help command for more info on a command.
    You can also type !help category for more info on a category.

### Metrics

You can ask the bot to retrieve the extremely nice leaderboard of nice people:

![nice_metrics](images/nice_metrics.png?raw=true "Nice metrics")

### Wisdom
You can ask the bot to retrieve nice ancient wisdom:

![nice_wisdom](images/nice_wisdom.png?raw=true "Nice wisdom")

### Feedback!
Encourage your users to give feedback on the bot, `bad-bot` takes a string as an argument and stores the user's feedback.
