import praw, config
bot = praw.Reddit(user_agent="s4njeebot",
                  client_id=config.client_id,
                  client_secret=config.client_secret,
                  username=config.redditusername,
                  password=config.redditpassword
                  )