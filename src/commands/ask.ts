import { CommandInteraction,SlashCommandBuilder } from 'discord.js'
import { spawn } from 'child_process'

import { SlashCommand } from '../types/command'

export const AskSlashCommand: SlashCommand = {
  data: new SlashCommandBuilder()
    .setName('ask')
    .setDescription('Ask me any question!')
    .addStringOption(option =>
      option.setName('question')
        .setDescription('The question you wanna ask')
        .setRequired(true)
    ),
  async execute(interaction: CommandInteraction) {
    let query = interaction.options.get('question')?.value?.toString();
    if (query === undefined) {
      await interaction.reply('Error parsing question.');
      return;
    }

    let respMsg = 'Response:\n';
    const pythonExec = await spawn(
      'python3',
      [
        '-u',
        './python_src/ask.py',
        `'${query}'` // BE WARE OF COMMAND INJECTION
      ]
    );

    pythonExec.stdout.on('data', (data) => {
      console.log(data.toString());
      respMsg += data.toString();
    });

    pythonExec.on('close', (code) => {
      if (code == 0) {
        interaction.reply(respMsg);
      }
      else {
        interaction.reply('Error getting response.');
      }
    })
  }
}
