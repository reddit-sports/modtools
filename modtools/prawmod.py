import praw, config

if config.refresh_token != '':
    #With Refresh Token
    bot = praw.Reddit(user_agent=config.user_agent,
                      client_id=config.client_id,
                      client_secret=config.client_secret,
                      refresh_token=config.refresh_token
                      )
else:
    #Without Refresh Token
    bot = praw.Reddit(user_agent=config.redditusername,
                      client_id=config.client_id,
                      client_secret=config.client_secret,
                      username=config.redditusername,
                      password=config.redditpassword
                      )