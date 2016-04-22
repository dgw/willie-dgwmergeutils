"""
Utility to go with my games, in case you want to merge duplicate users
created when people play with different nicks, accidentally or otherwise.
"""
from sopel.module import commands, example, require_owner
from sopel.tools import Identifier

STRINGS = {
    'OWNER_MERGE':   "Only the bot owner can merge users.",
    'MERGE_SYNTAX':  "I want to be sure there are no mistakes here. "
                     "Please specify nicks to merge as: <duplicate> into <primary>",
    'MERGE_DONE':    "Merged %s into %s.",
    'MERGE_GROUPED': "Nicks %s & %s are already grouped.",
    'MERGE_UNKNOWN': "Encountered unknown nick. Aborting merge.",
}

STATS = (
    'bomb_wrongs',
    'bomb_timeouts',
    'bomb_defuses',
    'bomb_alls',
    'bombs_planted',
    'duel_wins',
    'duel_losses',
    'rep_score',
    'roulette_games',
    'roulette_wins',
)

RATES = (
    'bomb_last_planted',
    'duel_last',
    'rep_used',
    'roulette_last',
)


@commands('nickmerge')
@example(".nickmerge newbie into old_friend")
@require_owner(STRINGS['OWNER_MERGE'])
def is_really(bot, trigger):
    """
    Merge the two nicks, keeping the stats for the second one.
    """
    duplicate = trigger.group(3) or None
    primary = trigger.group(5) or None
    if not primary or not duplicate or trigger.group(4).lower() != 'into':
        bot.reply(STRINGS['MERGE_SYNTAX'])
        return
    duplicate = Identifier(duplicate)
    primary = Identifier(primary)
    try:
        if bot.db.get_nick_id(duplicate, False) == bot.db.get_nick_id(primary, False):
            bot.reply(STRINGS['MERGE_GROUPED'] % (primary, duplicate))
            return
    except ValueError:
        bot.reply(STRINGS['MERGE_UNKNOWN'])
        return
    newstats = dict()
    for stat in STATS:
        dupval = bot.db.get_nick_value(duplicate, stat) or 0
        prival = bot.db.get_nick_value(primary, stat) or 0
        newstats[stat] = dupval + prival
    for rate in RATES:
        dupval = bot.db.get_nick_value(duplicate, rate) or 0
        prival = bot.db.get_nick_value(primary, rate) or 0
        newstats[rate] = prival if (prival > dupval) else dupval
    for stat in newstats:
        bot.db.set_nick_value(primary, stat, newstats[stat])
        bot.db.set_nick_value(duplicate, stat, 0)  # because willie < 5.4.1 doesn't merge properly
    bot.db.merge_nick_groups(primary, duplicate)
    bot.say(STRINGS['MERGE_DONE'] % (duplicate, primary))
