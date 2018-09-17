# discord auth
discordtoken = ''
# reddit auth
redditusername = ''
redditpassword = ''
client_secret = ''
client_id = ''
user_agent = ''

#Leave Refresh_token as '' if not used.  Reddit Username and Password is then required above.
refresh_token = ''

#mod emojis - use reddit username and emoji or unicode string
#Format: {'redditusername':[flairconfig,flair]}
DEFAULT_FLAIR = 0
CUSTOM_FLAIR = 1
modemojis = {'user1':[DEFAULT_FLAIR,u"\U0001f575"],'user2':[CUSTOM_FLAIR,'flair:##################']
}

#for tagging when a user is mentioned in modmail, use reddit username.  Enable Discord Dev Mode to see user ids.
discordIDs = {'username1':'discordid', 'username2':'##################'}

#channel this feeds to.  Enable Discord Dev Mode to see channel ids.
channel = '##################'
#channel for modmails, can be same as above
modmailchannel = '##################'
#your subreddit
subreddit = 'subreddit'
