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
        with open('storage_path_config.json', 'r') as f:
            storage_paths = json.load(f)
        context_record_dir = storage_paths['context_record_dir']
        if os.path.exists(context_record_dir):
            channel_context_record = os.path.join(
                context_record_dir,
                args.channel_id
            )
            if os.path.exists(channel_context_record):
                os.remove(channel_context_record)
                print('Success clear discussion history.')
            else:
                print('Discussion history already empty')
        else:
            print('Discussion history already empty')
    except Exception as e:
        print(format_exc())
        raise e