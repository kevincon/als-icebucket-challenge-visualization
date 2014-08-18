import twitter
import json
import os
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

class Participant(object):

    def __init__(self, user, status=None):
        self.user = user
        self.status = status

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
        node_dict[screen_name].status = status
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

TWITTER_URL = 'https://twitter.com/'
STATUS_URL = TWITTER_URL + '#!/twitter/status/'


def get_updates():
    result_json = {}

    if graph.nodes():
        lock.acquire()
        result_nodes = [{'name': p.user.screen_name,
                         'url': STATUS_URL + str(p.status.id) if p.status else TWITTER_URL + p.user.screen_name} for p in graph.nodes()]
        result_links = [{'source': p1.user.screen_name,
                         'target': p2.user.screen_name}
                        for (p1, p2) in graph.edges_iter()]
        lock.release()

        result_json['nodes'] = result_nodes
        result_json['links'] = result_links

    return json.dumps(result_json)


def process_stream():
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

    stream = api.GetStreamFilter(track=['ALS', 'ice bucket', 'Ice Bucket'])

    for t in stream:
        status = twitter.status.Status.NewFromJsonDict(t)
        if is_completed_challenge(status):
            print 'COMPLETED: %s' % status.text.encode('utf-8')
            update_data(status)
            print status.id
            sleep(0.5)

if __name__ == '__main__':
    process_stream()
