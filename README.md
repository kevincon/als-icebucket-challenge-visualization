# ALS Ice Bucket Challenge Twitter Visualization

This is a web app written in Python (Flask) that uses the `python-twitter`
library, the `networkx` Python graph library, and the Sigma.js graph visualization library to visualize real-time
ALS Icebucket Challenge participants and their nominations.

## 10 steps to running the code
(tested on Mac OSX 10.8.5 using Python 2.7.7)


1. Install VirtualEnv:
http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation
2. Install Foreman: https://github.com/ddollar/foreman
3. Create a new Twitter application
(additionally create an access token under the "API Keys" tab of your new
application): https://apps.twitter.com/
4. Clone this repo:
`git clone git@github.com:kevincon/als-icebucket-challenge-visualization.git`
5. Copy the environment settings template `.env.template` to `.env` and fill in
the fields `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN_KEY`, and
`ACCESS_TOKEN_SECRET` with the values from your new Twitter application.
6. Create a virtualenv: `virtualenv venv`
7. Enter the virtualenv: `source venv/bin/activate`
8. Install the requirements: `pip install -r requirements.txt`
9. Start the website server using Foreman: `foreman start`
10. Visit the website: http://127.0.0.1:5000.

## Future work ideas
* Store the tweets in a database so the Twitter stream processing thread can
be removed
* Make the graph visualization collapsible
* Improve the CSS so it looks better on a wide range of screens/devices
* Provide stats about the number of tweets recorded, longest chain, etc.
