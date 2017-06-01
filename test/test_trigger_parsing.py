#!/usr/bin/env python3
import os
import unittest
import json



class ParseMessageTest(unittest.TestCase):
    pass

def test_generator(stub):
    def test(self):

    return test


if __name__ == '__main__':
    stub_dir = os.environ['STUB_DIR']
    for filename in os.listdir(stub_dir):
        test_name = 'test_parsing_{}'.format(filename)
        stub = test_generator(json.load(open(os.path.join(stub_dir, filename))))
        setattr(ParseMessageTest, test_name, stub)
    unittest.main()
