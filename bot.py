import praw
import re
import json
import time
import warnings
warnings.filterwarnings("ignore")

id = "2kfEtgtbk2ayruNPrYs9mw"
secret = "Ejvrwm52ptm6vOE7SN52G7yElOpMtg"
beat = "https://soundcloud.com/mhhofficialbeats/dark-beat-124bpm-tag"

with open("var.json") as f:
    var = f.read()
var = json.loads(var)

reddit = praw.Reddit(
    client_id = var["id"],
    client_secret = var["secret"],
    user_agent = "test a agent",
    username = var["username"],
    password = var["password"],
    rate_limit_seconds = 40,
)

class Bot:
    def __init__(self, reddit, beat, subreddit, nonce, theme, winner, vote_count):
        self.reddit = reddit
        self.beat = beat
        self.subreddit = subreddit
        self.nonce = nonce
        self.submission_id = None
        self.votes_id = None
        self.theme = theme
        self.winner = winner
        self.vote_count = vote_count
    
    def get_submissions(self):
        data = {}
        sub = self.reddit.submission(id=self.submission_id).comments
        for top_comments in sub:
            body = top_comments.body
            author = top_comments.author
            match = re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", body)
            if match:
                for i in match:
                    if "https://soundcloud.com" in i:
                        data[str(author)] = i
        print(data)
        return data
    
    def count_winner(self):
        all_votes = {}
        voters = self.get_submissions()
        time.sleep(1)
        sub = self.reddit.submission(id=str(self.votes_id)).comments
        for top_comments in sub:
            vote = set()
            for votes in top_comments.replies:
                if "vote" in votes.body.lower() and str(votes.author) in voters:
                    vote.add(str(votes.author))
    
            index = top_comments.body.find("[")
            index2 = top_comments.body.find("]")  
            all_votes[str(top_comments.body)[index+1:index2]] = vote
        print(all_votes)

        max = [0,0]
        for i in all_votes:
            length = len(all_votes[i])
            if length > max[1]:
                max = [i, all_votes[i]]
                self.winner = i
                self.vote_count = length
        return max[0]

    def create_voting_thread(self):
        id = self.submission_id
        with open("voting.txt", "r") as f:
            text = f.read()
            text = text.replace("Beat", "[Beat]({})".format(self.beat)).format(self.theme)
        with open("voting_title.txt", "r") as f:
            title = f.read().format(self.nonce)
        test = self.reddit.subreddit("test_bruks_bot")
        test.submit(title=title, selftext=text)
        print("voting thread created")
    
    def create_submission_thread(self):
        here = "[here]({})".format(self.beat)

        with open("sub_thrd_title.txt", "rb") as f:
            title = f.read().decode('utf-8').format(self.nonce)
        with open("sub_thrd_body.txt", "rb") as f:
            text = f.read().decode('utf-8').format(here, self.winner, self.vote_count, self.theme)
        test = self.reddit.subreddit(self.subreddit)
        test.submit(title=title, selftext= text)
        print("submission thread created")
    
    def dm_winner(self):
        winner = self.count_winner()
        self.reddit.redditor(winner).message("Request for next week's beat", "Send your favourite choice from soundcloud")
        print("dm sent to winner")
    
    def check_on_winner(self):
        print("getting unread messages")
        winner = self.count_winner()
        mes = self.reddit.inbox.unread()
        for i in mes:
            if str(i.author) == str(winner):
                if re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", i.body) and "https://soundcloud.com/mhhofficialbeats" in i.body:
                    self.beat = re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", i.body)[0]
                    print("new beat saved")
                    i.mark_read()
                index = i.body.lower().find("theme:")
                last = i.body.find("\n", index)
                if index != -1:
                    if last == -1:
                        theme = i.body[index+6:]
                        self.theme = theme
                        i.mark_read()
                        print("new theme saved" , theme)
                    else:
                        theme = i.body[index+6:last]
                        self.theme = theme
                        i.mark_read()
                        print("new theme saved", theme)
            i.mark_read()
    

    def get_id_of_new_thread(self):
        sub = self.reddit.subreddit(self.subreddit)
        posts = sub.new()
        for i in posts:
            self.submission_id = i
            print("id of submission thread recovered as {}".format(self.submission_id))
            return i
    
    def get_id_of_vot_thread(self):
        sub = self.reddit.subreddit(self.subreddit)
        posts = sub.new()
        for i in posts:
            self.votes_id = i
            print("id of voting thread recovered as {}".format(self.votes_id))
            return i
    
    def comment_in_vot_thread(self):
        id = self.votes_id
        contesters = self.get_submissions()
        print(self.submission_id)
        vot_sub = self.reddit.submission(str(self.votes_id))
        for i in contesters:
            reply = "[{}]({})".format(i, contesters[i])
            print(reply)
            vot_sub.reply(reply)
            print("commented on voting thread")

    def run(self):
        while True:
            self.create_submission_thread()
            time.sleep(1)
            self.get_id_of_new_thread()
            time.sleep(60)
            self.create_voting_thread()
            time.sleep(1)
            self.get_id_of_vot_thread()
            time.sleep(1)
            self.comment_in_vot_thread()
            time.sleep(60)
            self.count_winner()
            time.sleep(2)
            self.dm_winner()
            time.sleep(60)
            self.check_on_winner()
            self.nonce += 1

test_bot = Bot(reddit, beat, "test_bruks_bot", 12, "FAKE FRIENDS", "GD Ambidextrous", 4)
print(test_bot.run())