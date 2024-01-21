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
    let question = interaction.options.get('question')?.value?.toString();
    if (question === undefined) {
      await interaction.reply('Error parsing question.');
      return;
    }

    // logging
    console.log(
      `User ${interaction.user.username} `
      + `in channel ${interaction.channelId.toString()} `
      + `ask "${question}"`
    )

    let respMsg = '';
    const pythonExec = await spawn(
      'python3',
      [
        '-u',
        './python_src/ask.py',
        `${question}`
      ]
    );

    pythonExec.on('error', (err) => {
      interaction.reply('Error starting ask module.');
    })

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
