# NiceStalker

_"Day walker, night stalker."_

NiceStalker is a simple Discord bot designed to notify users when people become online on Discord. The project name is a playful nod to "Night Stalker," a character from the popular game Dota 2.

<p align="center">
  <img width="400" src="images/nicestalker.png" alt="Picture of an example notification"/>
</p>

## Features

:white_check_mark: **Real-time notifications:** NiceStalker keeps track of users' statuses and sends notifications whenever someone comes online on Discord.

:negative_squared_cross_mark: **Customizable settings:** Users can customize their notification preferences, including which users to monitor.

:negative_squared_cross_mark: **Automatic startup:** If required, NiceStalker can automatically start up on system boot, ensuring that you never miss out on any important alerts.

## Installation

To install NiceStalker, follow these steps:

1. Clone the repository to your local machine.

```bash
git clone https://github.com/naghim/NiceStalker.git
```

2. Install the necessary dependencies.

```bash
python -m pip install -r requirements.txt
```

3. Ensure that you are logged into the Discord client.

4. Run the bot.

```bash
python -m nicestalker.notifier
```
