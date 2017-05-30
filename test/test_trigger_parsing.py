#!/usr/bin/env python3
import os
import unittest
import json

os.sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from trigger_parsing import run

class ParseMessageTest(unittest.TestCase):
    pass

def test_generator(stub):
    def test(self):
        print(stub['recipient'])
        print(stub['params'])
        message = json.loads(stub['params'])
        run.parse(message)
        options = run.getEmailOptions(message)
        print(options)
        print(message['attachments'])
        files = list(run.getEmailAttachment(message))
        print(files)
        # self.assertEqual(a,b)
    return test


if __name__ == '__main__':
    stub_dir = os.environ['STUB_DIR']
    for filename in os.listdir(stub_dir):
        test_name = 'test_parsing_{}'.format(filename)
        stub = test_generator(json.load(open(os.path.join(stub_dir, filename))))
        setattr(ParseMessageTest, test_name, stub)
    unittest.main()
