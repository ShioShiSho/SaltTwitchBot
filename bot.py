from twitchio.ext import commands
from twitchio.ext.commands.core import Command

import unicodedata
import itertools
import random

import config
import bot_tools
import bot_db
import utils


GAMEGRAMMAR_USER_ID = 427289393

command_list_with_bruh = ['resetbruh', 'bruhcount']

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
        utils.log_kv('Admins: ', bot_db.get_all_admins())


    async def event_message(self, message):
        utils.log_kv('[Bot#event_message] New message', message.content)
        if 'bruh' in message.content.lower() and not message.author.name == config.bot_nick and not any (command in message.content for command in command_list_with_bruh):
            print('bruh found')
            if bot_db.exists_data('bruhs'):
                bot_db.increment_bruhs()
                bruhs = bot_db.get_data('bruhs')
                await message.channel.send(f'Bruh Counter: {bruhs[0]["bruhs"]}')
            else:
                print('No data')
        await self.handle_commands(message)


    @commands.command(name='resetbruh')
    async def res_bruh(self, ctx):
        if not bot_db.exists_admin(ctx.author.name):
            utils.log_body('[Bot#mod_command] Access denied to ' + ctx.author.name)
            return

        if bot_db.exists_data('bruhs'):
            bot_db.resetbruh()
            await ctx.send('Reset Bruh Coutner to 0')
        else:
            await ctx.send('No Bruh-coutner initialized')

    @commands.command(name='add_data')
    async def add_data(self, ctx):
        if not bot_db.exists_admin(ctx.author.name):
            utils.log_body('[Bot#mod_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 2)
        except ValueError:
            return await ctx.send('Usage: add_data <name> <entry>')

        [_, name, entry] = command
        if entry.isdigit():
            entry = int(entry)
        bot_db.add_data(name, entry)

    @commands.command(name='bc', aliases=['bruhcount'])
    async def bruhcount(self, ctx):
        if not bot_db.exists_data("bruhs"):
            bot_db.add_data("bruhs", 0)       
        bruhs = bot_db.get_data("bruhs")[0]["bruhs"]
        await ctx.send(f'Current bruh count: {bruhs}')

    @commands.command(name='mods')
    async def mods_command(self, ctx):
        mods = [mod['name'] for mod in bot_db.get_all_admins()]
        await ctx.send('Mods: {}'.format(', '.join(mods)))

    @commands.command(name='mod')
    async def mod_command(self, ctx):
        if not bot_tools.is_superadmin(ctx.author.name):
            utils.log_body('[Bot#mod_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: mod <name>')

        [_, mod_name] = command
        utils.log_kv('Modding', mod_name)

        if bot_db.exists_admin(mod_name):
            await ctx.send(f'{mod_name} is already a mod.')
        else:
            bot_db.add_admin(mod_name)
            await ctx.send(f'Modded {mod_name}.')

    @commands.command(name='demod')
    async def demod_command(self, ctx):
        if not bot_tools.is_superadmin(ctx.author.name):
            utils.log_body('[Bot#demod_command] Access denied to ' + ctx.author.name)
            return
        try:
            command = bot_tools.parse_command(ctx.message.content, 1)
        except ValueError:
            return await ctx.send('Usage: demod <name>')

        [_, user_name] = command
        utils.log_kv('Demodding', user_name)

        if bot_db.exists_admin(user_name):
            bot_db.remove_admin(user_name)
            await ctx.send(f'Demodded {user_name}.')
        else:
            await ctx.send(f'{user_name} is not a mod.')

    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')


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

        message = 'Kappa'
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
