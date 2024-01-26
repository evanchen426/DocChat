import os
import json
from traceback import format_exc
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'channel_id',
        type=str,
    )
    args = parser.parse_args()
    try:
        with open('storage_config.json', 'r') as f:
            storage_configs = json.load(f)
        context_record_dir = storage_configs['channel_records_dir']
        if os.path.exists(context_record_dir):
            channel_context_record = os.path.join(
                context_record_dir,
                args.channel_id
            )
            if os.path.exists(channel_context_record):
                os.remove(channel_context_record)
                print('Success clear conversation history.')
            else:
                print('Conversation history already empty.')
        else:
            print('Conversation history already empty.')
    except Exception as e:
        print(format_exc())
        raise e