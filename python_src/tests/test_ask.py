import unittest
import subprocess

class TestAskCommand(unittest.TestCase):

    def test_ask(self):
        result = subprocess.run([
            'python3', './python_src/ask.py',
            '--ai-backend', 'dummy',
            '--is-debug',
            'kiss'
        ], stdout=subprocess.PIPE)
        expected_stdout = (
b"""Relevant Docs:
- How to French Kiss.txt : 3.6657202728332234
kiss
As an AI assistant, I cannot answer this question.
"""
        )
        # print(result.stdout)
        self.assertEqual(result.stdout, expected_stdout)
    
    def test_discuss(self):
        # clear
        result = subprocess.run([
            'python3', './python_src/clear_channel_context.py', '123'
        ], stdout=subprocess.PIPE)
        possible_expect_stdouts = {
            b'Discussion history already empty.\n',
            b'Success clear discussion history.\n',
        }
        self.assertEqual(result.returncode, 0)
        self.assertIn(result.stdout, possible_expect_stdouts)

        # discuss 3 times
        discuss_args = [
            'python3', './python_src/ask.py',
            '--ai-backend', 'dummy',
            '--channel-id', '123',
            '--is-debug',
            'screenshot'
        ]
        expected_stdout = (
b"""Relevant Docs:
- How to Take a Screenshot on a Windows PC: 8 Simple Tricks.txt : 3.672123491438766
screenshot
As an AI assistant, I cannot answer this question.
screenshot
This is the 2 times I said this. As an AI assistant, I cannot answer this question.
screenshot
This is the 3 times I said this. As an AI assistant, I cannot answer this question.
"""
        )
        returncode = subprocess.call(discuss_args, stdout=subprocess.PIPE)
        self.assertEqual(returncode, 0)
        returncode = subprocess.call(discuss_args, stdout=subprocess.PIPE)
        self.assertEqual(returncode, 0)

        result = subprocess.run(discuss_args, stdout=subprocess.PIPE)
        # print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, expected_stdout)
