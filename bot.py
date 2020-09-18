from twitchio.ext import commands
from twitchio.ext.commands.core import Command

import config
import bot_tools
import bot_db
import utils


GAMEGRAMMAR_USER_ID = 427289393
tag_names = [t['name'] for t in bot_db.get_all_tags()]


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=config.bot_irc_token,
            client_id=config.bot_client_id,
            nick=config.bot_nick,
            prefix=config.bot_prefix,
            initial_channels=config.bot_initial_channels
        )

    async def event_ready(self):
        utils.log_kv('[Bot#event_ready] Ready with username', self.nick)
        utils.log_kv('Tags', bot_db.get_all_tags())
        utils.log_kv('Mods', bot_db.get_all_mods())
        utils.log_kv('Superadmins', config.superadmins)

    async def event_message(self, message):
        utils.log_kv('[Bot#event_message] New message', message.content)
        await self.handle_commands(message)


    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')


    # @commands.command(name='stats')
    # async def stats_command(self, ctx):
    #     n_followers = await self.get_followers(GAMEGRAMMAR_USER_ID, count=True)
    #     await ctx.send(f'GameGrammar has {n_followers} followers!')

    def get_jisho_results_message(self, keywords, result_index=None):
        results = bot_tools.jisho(keywords)

        if len(results) == 0:
            return f'Sorry, no results for {keywords}.'

        if result_index and result_index < len(results) and result_index > 0:
            result = results[result_index]
        else:
            result = results[0]

        n_senses_to_show = 3

        senses_parts = []

        for idx, sense in enumerate(result['senses']):
            if idx >= n_senses_to_show:
                break
            digit = utils.get_unicode_digit(idx + 1)
            definitions = ', '.join(sense['english_definitions'])

            # This code adds parts of speech after every sense.
            # pos = '/'.join([
            #     bot_tools.shorten_part_of_speech(pos)
            #     for pos in sense['parts_of_speech']
            # ])
            # if len(pos) > 0:
            #     senses_parts.append(f'{digit} {definitions} [{pos}]')
            # else:
            #     senses_parts.append(f'{digit} {definitions}')

            senses_parts.append(f'{digit} {definitions}')

        senses_string = ' '.join(senses_parts)

        # TODO: Only add parts of speech from senses we actually showed?
        pos_all = list(itertools.chain.from_iterable([
            s['parts_of_speech'] for s in result['senses']
        ]))
        pos_unique = list(set(pos_all))
        pos_short = [bot_tools.shorten_part_of_speech(pos) for pos in pos_unique]
        pos_string = '/'.join(pos_short)

        word = result["japanese"][0].get("word", None)
        reading = result["japanese"][0].get("reading", None)

        message = 'NaruhodoThink'
        if word is not None:
            message += f' {word}'
        if reading is not None:
            message += f' {reading}'
        message += f' {senses_string} [{pos_string}]'
        return message

    @commands.command(name='j')
    async def jisho_command(self, ctx):
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: !j <keywords> [<result_number>]')

        [_, keywords] = command
        [keywords, result_number] = bot_tools.get_trailing_numbers(keywords)
        if result_number is None:
            message = self.get_jisho_results_message(keywords)
        else:
            message = self.get_jisho_results_message(keywords, result_number - 1)
        await ctx.send(message)


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
