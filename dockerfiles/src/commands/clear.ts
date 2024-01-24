import { CommandInteraction,SlashCommandBuilder } from 'discord.js'
import { spawn } from 'child_process'

import { SlashCommand } from '../types/command'

export const ClearSlashCommand: SlashCommand = {
  data: new SlashCommandBuilder()
    .setName('new_discuss')
    .setDescription('Start a new empty discussion in this channel.'),
  async execute(interaction: CommandInteraction) {
    let channel_id = interaction.channelId;
    let python_args = [
      '-u',
      './python_src/clear_channel_context.py',
      `${channel_id}`
    ];
    console.log(
      `User ${interaction.user.username} `
      + `clears the context reocrd of channel ${channel_id}`
    )

    let respMsg = '';
  
    const pythonExec = await spawn('python3', python_args);
    pythonExec.stdout.on('data', (data) => {
      console.log(data.toString());
      respMsg += data.toString();
    });
    pythonExec.on('close', (code) => {
      if (code != 0) {
        respMsg = 'Error getting response';
      }
      interaction.reply(respMsg);
    });
  }
}
