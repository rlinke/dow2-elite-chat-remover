# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 21:37:31 2020

@author: Richard
"""
import unittest

import sys
sys.path.append("..")

import dow2_replay_module
from print_functions import print_players

class TestStringMethods(unittest.TestCase):

    
    def test_issue1(self):
        fname = "issue1/2p_calderisrefinery.2020-08-13.16-11-49.rec"
        message_data, gamedata = dow2_replay_module.remove_chat_messages(fname)
        
        # the correctly reduced size should be this ...
        # unsafe test but w/e
        self.assertEqual(len(gamedata),1291112)
        """
        with open('issue1/resolve.rec', 'wb') as f:
            f.write(bytearray(gamedata))
            
        """
        ## test printing of player info
        print_players(message_data)

if __name__ == '__main__':
    unittest.main()