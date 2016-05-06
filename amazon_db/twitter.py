import tweepy

def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def main():
    #Fill in the values noted in previous step here
    cfg = { 
    "consumer_key"        : "0kFCrizKx4UFzFGfVKCZdJIFS",
    "consumer_secret"     : "d9eRNNVdDHy067VweYKbpEbei8gQicRQwMpGUSFFop0XimthCL",
    "access_token"        : "213512945-94181AvMplNNqoDXxO7z1uOqPDEIiAMehivblXdo",
    "access_token_secret" : "253adDmTAFS6WdwKUBzVnPoV0Iq9dPsOBiWGgAKdlaNid" 
    }
    api = get_api(cfg)
    tweet = "Testing"

    status = api.update_status(status=tweet) 
    print "status : ", status
    # Yes, tweet is called 'status' rather confusing

if __name__ == "__main__":
    main()