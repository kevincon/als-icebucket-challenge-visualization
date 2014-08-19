import twitter
import json
import os
import random
from time import sleep
from networkx import Graph
from thread import allocate_lock

CONSUMER_KEY = os.getenv('CONSUMER_KEY', None)
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', None)
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY', None)
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', None)

graph = Graph()
node_dict = {}
lock = allocate_lock()

TWITTER_URL = 'https://twitter.com/'
STATUS_URL = TWITTER_URL + '#!/twitter/status/'

class Participant(object):

    def __init__(self, user, status=None):
        self.user = user
        self.status = status

        self.update_embed()

    def update_embed(self):
        if self.status:
            status_url = STATUS_URL + str(self.status.id)
            try:
                self.embed = api.GetStatusOembed(url=status_url).get('html')
            except Exception:
                self.embed = '<blockquote class="twitter-tweet" lang="en">%s&mdash; %s (@%s) <a href="%s"></a></blockquote><script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>' % (self.status.text, self.user.screen_name, self.user.screen_name, status_url)
        else:
            self.embed = '<a href=%s>%s</a>' % (TWITTER_URL + self.user.screen_name,
                                                self.user.screen_name)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(self.user)

    def __hash__(self):
        return hash(str(self.user.screen_name))

    def __eq__(self, other):
        if not isinstance(other, Participant):
            return False
        else:
            return hash(self) == hash(other)

def is_original_tweet(status):
    return not status.retweeted_status

def is_completed_challenge(status):
    return is_original_tweet(status) and \
           'nominate' in status.text and \
           status.urls and \
           status.user_mentions

def update_data(status):
    lock.acquire()
    participant = Participant(status.user, status)
    screen_name = participant.user.screen_name
    if participant in node_dict.values():
        # user had already been mentioned, let's set status
        node = node_dict[screen_name]
        node.status = status
        node.update_embed()
    else:
        graph.add_node(participant)
        node_dict[screen_name] = participant
        # create nodes for everyone mentioned in status, if necessary
        for mentioned_user in status.user_mentions:
            mentioned_participant = Participant(mentioned_user)
            mentioned_screen_name = mentioned_user.screen_name
            if mentioned_participant not in node_dict.values():
                graph.add_node(mentioned_participant)
                node_dict[mentioned_screen_name] = mentioned_participant
            else:
                mentioned_participant = node_dict[mentioned_screen_name]
            graph.add_edge(participant, mentioned_participant)
    lock.release()

api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

def get_updates():
    result_json = {}

    if graph.nodes():
        lock.acquire()
        result_nodes = [{'id': p.user.screen_name,
                         'label': p.user.screen_name,
                         'x': random.random(),
                         'y': random.random(),
                         'size': 1.0,
                         'embed': p.embed} for p in graph.nodes()]
        result_links = [{'id': '%s->%s' % (p1.user.screen_name, p2.user.screen_name),
                         'source': p1.user.screen_name,
                         'target': p2.user.screen_name}
                        for (p1, p2) in graph.edges_iter()]
        lock.release()

        result_json['nodes'] = result_nodes
        result_json['edges'] = result_links

    return json.dumps(result_json)


def process_stream():
    stream = api.GetStreamFilter(track=['ALS', 'ice bucket', 'Ice Bucket'])

    for t in stream:
        status = twitter.status.Status.NewFromJsonDict(t)
        if is_completed_challenge(status):
            print 'COMPLETED: %s' % status.text.encode('utf-8')
            update_data(status)
            sleep(0.5)

if __name__ == '__main__':
    process_stream()
