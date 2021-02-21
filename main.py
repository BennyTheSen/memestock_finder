import csv
import re
import sys
import time
import praw


class Scrapper():
    def __init__(self):
        self.SUBREDDITS = ["wallstreetbets", "mauerstrassenwetten", "stocks", "pennystocks", "pennystocksdd"]
        USER_AGENT = "myredditapp:v0.0.1 (by u/bennythesen)"
        self.REDDIT = praw.Reddit(client_id="", client_secret="", user_agent=USER_AGENT)
        self.POST_LIMIT = 200
    

    def main(self):
        #TODO: write more classes and functions instead of a big main

        sub_content_list = []
        # get reddit content
        for subreddit in self.SUBREDDITS:
            submissions = self.REDDIT.subreddit(subreddit).hot(limit=self.POST_LIMIT)
            sub_content_dict = {"subreddit": subreddit, "submission_text_content": []}
            print(f"Scraping r\{subreddit}!")

            # setup toolbar
            sys.stdout.write("[%s]" % (" " * self.POST_LIMIT))
            sys.stdout.flush()
            sys.stdout.write("\b" * (self.POST_LIMIT+1)) # return to start of line, after '['

            for i in range(self.POST_LIMIT):
                for submission in submissions:
                    author = submission.author
                    submission_text_content = submission.title + submission.selftext
                    sub_content_dict["submission_text_content"].append(submission_text_content)
                    num_comments = submission.num_comments
                    comments = submission.comments
                    upvotes = submission.ups
                    
                    sys.stdout.write("-")   # update progress bar
                    sys.stdout.flush()
            
            sys.stdout.write("]\n") # this ends the progress bar

            sub_content_list.append(sub_content_dict)

        symbol_list = self.get_stock_symbols()

        # compare content with symbols
        for sub_content_dict in sub_content_list:
            stock_count_dict = {"subreddit": sub_content_dict["subreddit"], "stocks": {}}

            for content in sub_content_dict["submission_text_content"]:
                stock_content = self.whole_word_in_string(content, symbol_list)
                #stock_content = {symbol for symbol in symbol_list if(symbol in content)}
                for stock in stock_content:
                    if stock in stock_count_dict["stocks"].keys():
                        stock_count_dict["stocks"][stock] += 1
                    else:
                        stock_count_dict["stocks"][stock] = 1

            self.write_to_csv(stock_count_dict)

    def get_stock_symbols(self):
        #TODO add more stocks than US and cryptos
        symbol_list = []
        with open("US_STOCKS.txt", "r") as textfile:
            for line in textfile:
                symbol_list.append(line.rstrip())
        return symbol_list

    def write_to_csv(self, stock_dict):
        filename = time.strftime("%Y%m%d") + "_" + stock_dict["subreddit"] + ".csv"
        with open(filename, "w+", newline='') as outfile:
            writer = csv.writer(outfile)
            for item in stock_dict["stocks"].items():
                writer.writerow(item)

    def whole_word_in_string(self, string, word_list):
        #TODO replace with NLP or similiar for better detection
        found_list = []
        
        for word in word_list:
            match = re.search(r"\b%s\b" % word, string, re.MULTILINE)
            if match:
                found_list.append(word)
        
        return found_list


if __name__ == "__main__":
    # execute only if run as a script
    scrapper = Scrapper()
    scrapper.main()  
