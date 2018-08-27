from b import Session, engine, Base
from sqlalchemy.sql import exists
from models import ModLog, ModQueueItem, DiscordAction, Report, ModMailConversation
from prawmod import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import praw, datetime, discord, pprint, config
import logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
# create tables with sqlalchemy based off models.py
Base.metadata.create_all(engine)

# create scheduler for separate jobs
sched = AsyncIOScheduler()

# create discord client
client = discord.Client()


# login message for discord client
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# adds moderation log to db every minute
@sched.scheduled_job('cron', second=10)
async def addModlogs():
    # Get subreddit moderation logs
    for log in bot.subreddit(config.subreddit).mod.log(limit=1000):
        session = Session()
        d = datetime.datetime.fromtimestamp(log.created_utc)
        # Create ModLog item to insert into modlogs table
        m = ModLog(id=log.id,
                   target_body=log.target_body,
                   mod_id36=log.mod_id36,
                   date=d,
                   created_utc=log.created_utc,
                   subreddit=log.subreddit,
                   target_title=log.target_title,
                   target_permalink=log.target_permalink,
                   details=log.details,
                   action=log.action,
                   target_author=log.target_author,
                   target_fullname=log.target_fullname,
                   sr_id36=log.sr_id36,
                   mod=log.mod.name)
        if log.action == 'approvelink' or log.action == 'approvecomment':
            message = session.query(DiscordAction).filter(DiscordAction.id == log.target_fullname.split("_")[1]).first()
            if message:
                messageID = message.messageID
                if log.target_body is None:
                    log.target_body = " "
                a = DiscordAction(id=log.id, action='approvereact', messageID=messageID, target_id=log.mod.name,
                                  date=d, link=log.target_permalink, text=log.target_body[:2611],target_type=log.action,
                                  target_channel=config.channel)
                session.merge(a)
        elif log.action == 'removelink' or log.action == 'removecomment':
            message = session.query(DiscordAction).filter(DiscordAction.id == log.target_fullname.split("_")[1]).first()
            if message:
                messageID = message.messageID
                if log.target_body is None:
                    log.target_body = " "
                a = DiscordAction(id=log.id, action='removereact', messageID=messageID, target_id=log.mod.name,
                                  date=d, link=log.target_permalink, text=log.target_body[:2611],target_type=log.action,
                                  target_channel=config.channel)
                session.merge(a)
        # Merge + commit item to db
        try:
            session.merge(m)
            session.commit()
            session.close()
        except Exception as e:
            print(e)


# adds modqueue items every minute
@sched.scheduled_job('cron', second=0)
def addModQueueItems():
    for item in bot.subreddit(config.subreddit).mod.modqueue(limit=None):
        print(vars(item))
        if item.removed == True:
            print(pprint.pprint(vars(item)))
        session = Session()
        if (item.edited == False):
            item.edited = 0
        if not session.query(exists().where(ModQueueItem.id == item.id)).scalar():
            d = datetime.datetime.fromtimestamp(item.created_utc)
            if type(item) != praw.models.reddit.submission.Submission:
                m = ModQueueItem(id=item.id, link_title=item.link_title, posttype='comment', link_id=item.link_id,
                                 author=item.author.name, date=d, edited=item.edited, body=item.body,
                                 permalink=item.permalink)
                a = DiscordAction(action='sendmessage', link=item.permalink, text=item.body, date=d,
                                  target_id=None, target_type="comment", id=item.id, completed=False,
                                  target_user=item.author.name, target_channel=config.channel)
            else:
                m = ModQueueItem(id=item.id, posttype='submission', link_title=item.title, link_id=None,
                                 author=item.author.name, date=d, edited=item.edited, body=None,
                                 permalink=item.permalink)
                a = DiscordAction(action='sendmessage', link=item.permalink, text=item.title, target_id=None, date=d,
                                  target_type="submission", id=item.id, completed=False, target_user=item.author.name,
                                  target_channel=config.channel)
            session.merge(m)
            if not session.query(exists().where(DiscordAction.id == item.id)).scalar():
                session.merge(a)
            session.commit()
            session.close()


# adds reports every minute
@sched.scheduled_job('cron', second=5)
def addReports():
    for item in bot.subreddit(config.subreddit).mod.reports(limit=None):
        d = datetime.datetime.fromtimestamp(item.created_utc)
        for report in item.user_reports:
            session = Session()
            if report[0] is not None:
                r = Report(id=item.id, reason=report[0], count=str(report[1]), date=d)
                session.merge(r)
                session.commit()
                session.close()
        for report in item.mod_reports:
            session = Session()
            if report[0] is not None:
                r = Report(id=item.id, reason=report[0], count=report[1], date=d)
                session.merge(r)
                session.commit()
                session.close()

@sched.scheduled_job('cron', second=30)
def addModMail():
    conversations = bot.subreddit(config.subreddit).modmail.conversations(state="all")
    session = Session()
    for c in conversations:
        if c.participant:
            mmc = ModMailConversation(id=c.id, participant=c.participant.name, subject=c.subject, lastupdated=c.last_updated)
            a = DiscordAction(id=c.id,target_user=c.participant.name, action='sendmodmailmessage', date=c.last_updated,
                              link='https://mod.reddit.com/mail/all/' + c.id, text=c.messages[-1].body_markdown,
                              target_type='modmail', target_id=c.subject)
            session.merge(mmc)
            session.merge(a)
            session.commit()
    session.close()

# processes actions placed in discordactions table
@sched.scheduled_job('cron', second=45)
async def processDiscordActions():
    session = Session()
    items = session.query(DiscordAction).filter(DiscordAction.completed == False).all()
    for item in items:
        if item.action == 'sendmessage':
            item.completed = True
            session.commit()
            channel = client.get_channel(int(config.channel))
            reports = session.query(Report).filter(Report.id == item.id)
            embed = discord.Embed(title=item.target_type+ " by /u/" + item.target_user, description=item.text[:2047], color=0x00ff00,
                                  url='http://reddit.com' + item.link)
            for r in reports:
                embed.add_field(name=r.reason, value=r.count)
            await channel.send(embed=embed)
            messages = await channel.history().flatten()
            item.messageID = messages[0].id
            session.commit()
        if item.action == 'sendmodmailmessage':
            channel = client.get_channel(int(config.channel))
            embed = discord.Embed(title="MODMAIL: "+item.target_id+ " by /u/" + item.target_user, color=0xff0000,
                                  url=item.link)
            item.completed = True
            session.commit()
            conversation = bot.subreddit(config.subreddit).modmail(item.id, mark_read=True)
            mentions = []
            for c in conversation.messages:
                try:
                    if c.author.name in config.discordIDs:
                        mentions.append("<@"+config.discordIDs[c.author.name]+">")
                    embed.add_field(name=c.author.name, value=c.body_markdown[:1023], inline=False)
                except Exception:
                    pass
            await channel.send(embed=embed)
            try:
                if conversation.messages[-1].author.name not in config.discordIDs:
                    await channel.send(" ".join(set(mentions)))
            except Exception:
                pass
            messages = await channel.history().flatten()
            item.messageID = messages[0].id
            session.commit()
        elif item.action == 'removereact':
            react = '\u274c'
        elif item.action == 'approvereact':
            react = '\u2705'

        if item.action == 'approvereact' or item.action == 'removereact':
            channel = client.get_channel(int(config.channel))
            if item.messageID:
                message = await channel.get_message(item.messageID)
                messageSQLobject = session.query(DiscordAction).filter(DiscordAction.messageID == str(message.id)).first()
                messageSQLobject.reactcompleted = True
                await message.add_reaction(react)
                if item.target_id and item.target_id in config.modemojis:
                    await message.add_reaction(config.modemojis[item.target_id])
                item.completed = True
                session.commit()
    session.close()

sched.start()
client.run(config.discordtoken)
