import { CommandInteraction, SlashCommandBuilder, PermissionsBitField, ChannelType, Client } from 'discord.js'

import { SlashCommand } from '../types/command'
import { randomUUID } from 'crypto';

export const NewChannelSlashCommand: SlashCommand = {
  data: new SlashCommandBuilder()
    .setName('new_channel')
    .setDescription('Open new channel where there\'s just you and chatbot...'),
  async execute(interaction: CommandInteraction) {
    const new_channel_name = 'chatbot_'
                            + interaction.user.username
                            + '_'
                            + randomUUID();
    const new_channel = await interaction.guild?.channels.create({
      name: new_channel_name,
      type: ChannelType.GuildText,
      permissionOverwrites: [
        {
          id: interaction.guild.id,
          deny: [PermissionsBitField.Flags.ViewChannel],
        },
        {
          id: interaction.user.id,
          allow: [PermissionsBitField.Flags.ViewChannel],
        },
        {
          id: interaction.applicationId,
          allow: [PermissionsBitField.Flags.ViewChannel],
        }
      ]
    });
    interaction.reply('Successfully made new channel: ' + new_channel_name);
  }
}
