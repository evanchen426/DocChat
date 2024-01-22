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
    ).addBooleanOption(option =>
      option.setName('bindchannel')
        .setDescription('Remembered this conversation. All Q&As in \
this channel will share the same context. FOREVER.')
    ),
  async execute(interaction: CommandInteraction) {
    let question = interaction.options.get('question')?.value?.toString();
    if (question === undefined) {
      await interaction.reply('Error parsing question.');
      return;
    }

    const is_bind_channel = interaction.options.get('bindchannel', false)?.value;
    let channel_id = interaction.channelId;
    let python_args = [
      '-u',
      './python_src/ask.py',
      `${question}`,
      '--channel-id', channel_id,
    ];
    if (is_bind_channel == true) {
      python_args = python_args.concat(['--bind-channel'], );
    }

    console.log(
      `User ${interaction.user.username} `
      + `in channel ${channel_id} `
      + `ask "${question}" `
      + `is_bind_channel=${is_bind_channel}`
    )

    let respMsg = '';
  
    const pythonExec = await spawn('python3', python_args);

    pythonExec.on('error', (err) => {
      interaction.reply('Error starting ask module.');
    })

    pythonExec.stdout.on('data', (data) => {
      console.log(data.toString());
      respMsg += data.toString();
    });

    // discord's request body length limit is 2000
    const discordContentLengthLimit = 1600;
    pythonExec.on('close', (code) => {
      if (code != 0) {
        respMsg = 'Error getting response';
      }
      if (respMsg.length > discordContentLengthLimit) {
        respMsg = respMsg.substring(0, discordContentLengthLimit)
          + '[truncated for reply length limit]';
      }
      interaction.reply(respMsg);
    });
  }
}
