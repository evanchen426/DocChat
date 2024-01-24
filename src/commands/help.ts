import { CommandInteraction,SlashCommandBuilder } from 'discord.js'

import { SlashCommand } from '../types/command'

export const HelpSlashCommand: SlashCommand = {
  data: new SlashCommandBuilder().setName('help').setDescription('Have some command descrptions.'),
  async execute(interaction: CommandInteraction) {
    const help_texts = `**Command -- Description**
\`/ask question\` -- Ask a question and the chatbot will reply an answer if \
it can find related documents regarding to your question.
\`/ask_dummy question\` -- Ask a question and the chatbot will reply with \
"As an AI asistant, I cannot answer this question."
\`/discuss question\` -- Ask a question in a channel-wide discussion. In the \
channel-wide discussion, the chatbot see any question sent by this command \
as the continuation of the ongoing conversation about the first question, \
no matter who send them.
\`/new_discuss\` -- As we may change topic in the channel-wide discussion, \
this command starts a new the conversation.
\`/new_channel\` -- Create a private channel where there's just you and the \
chatbot. So that you can have a private discussion with chatbot without \
anyone bothers you.
`;
    await interaction.reply(help_texts)
  }
}
