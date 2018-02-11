# Titan

![Alt Text](https://i.imgur.com/uebAKT4.png)



Titan is a totally free cryptocurrency automated trading framework for traders of all skill levels. Built on top of the ccxt API library, it works out of the box with any exchange and trading pair. We believe in decentralizing trading strategies and providing everyone access to building advanced crypto portfolios. The future of algorithmic trading is here!

The base framework comes with a set of methods that allow you to program trading logic and write data to your own database with ease. A sample strategy based on moving average crossovers is provided out of the box to experiment as well as a full simulation suite where one can trade fake BTC against real market prices. The original objective of the project was to write a cryptocurrency trading bot in a framework that allows for the implementation of various machine learning algorithms to determine trade behavior.

## FAQ

#### Spare me the mumbo-jumbo! What's this all about?
IT PRINTS MONEY

#### But wait, why would you ever release this for free??? hurr-durr profits
Ah yes, I see you've taken a basic microeconomics course before. Truth is, this is mainly a project to encourage people to write their own strategies and have a way to test them out. We want to lower the bar to algorithmic cryptocurrency trading to those who are interested but don't know where to start. 

#### This sounds cool, I want to get involved!
Great, there's tons of cool stuff you can work on. Beginners welcome. Check out our discord [here!](https://discord.gg/4r9Qxuf)

#### What's with the name Titan anyway?
Sounds cool as heck, think about it. "Yeah made 5 BTC using that Titan trading system" - it has a certain ring to it. Plus it makes us feel important, ok?


## Getting Started
![Alt Text](https://media.giphy.com/media/v5Ewl8EnO4KFW/giphy.gif)

*Is this your face right now? Don't worry!*

First thing is make sure you have a recent version of Python on your computer, as well as Git (I recommend GitHub Desktop if you're a new user). You can download Python from the website [here](https://www.python.org/downloads/) and go for the 3.6+ version for your OS. From there, make a new virtual environment as follows:

    python -m venv /path/to/new/virtual/titanenv
    (Mac) $ source titanenv/bin/activate 
    (Windows) C:\> titanenv\Scripts\activate.bat 

Once you're squared away with a squeaky clean new virtual environment you should proceed to install all the dependencies required for the program to run. You should have <titanenv> on the side of your console window now. 
    
    mkdir Titan
    cd Titan
    git clone https://github.com/Denton24646/Titan.git
    python pip install -r requirements.txt 
  
Now you're all set to go - what to do next? Well, Titan is currently a Flask application that runs in your web browser. So the UI that you will interact with will be inside your Chrome or Firefox browser running on your local machine. Make sure you're in the main Titan directory and run the following:

    python titan_app.py
    
You should get an indication that the app is running on port 5555 on your local machine. If you see that message, open up your browser and navigate to http://127.0.0.1:5555 to start using the app!

## Using Titan
At first it's recommended to trade only simulation currency and familiarize yourself with the behavior of the program. 
A [detailed wiki](https://github.com/Denton24646/Titan/wiki) explains the core components underlying Titan. 

### Live Trading

*You better know what you're getting yourself into!*
