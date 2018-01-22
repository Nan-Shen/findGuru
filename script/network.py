#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 23:17:50 2018

@author: Nan
"""


__author__ = "Nan Shen"
__credits__ = ["Nan Shen"]
__version__ = "0.1-dev"
__maintainer__ = "Nan Shen"
__email__ = "nanshenbms@gmail.com"

import click
import sys
import tweepy

from findGuru.collect import get_follower_ids, api
from findGuru.knit import process_follower_list, SEED

"""
"""

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1')

@click.option('-d', '--depth', required=True,
              type=click.INT,
              help='How far to follow user network.')
@click.option('-s', '--screen_name', required=True,
              type=click.str,
              help='Screen name of twitter user')

def twitter_network(depth, screen_name):
    """
    """
    
    
def collect_followers(depth, screen_name):
    """Collect followers and friends of user with screen-name and trace down
    friends follwers and friends. 
    """
    if depth < 1 or depth > 3:
        print 'Depth value %d is not valid. Valid range is 1-3.' % depth
        sys.exit('Invalid depth argument.')
        
    print 'Max Depth: %d' % depth
    matches = api.lookup_users(screen_names=[screen_name])
    
    if len(matches) == 1:
        print get_follower_ids(matches[0].id, max_depth=depth)
    else:
        print 'Sorry, could not find twitter user with screen name: %s' % screen_name
        
def build_network(screen_name):
    """
    """
    edges = process_follower_list(screen_name, max_depth=3)

    with open('twitter_network.csv', 'w') as outf:
        edge_exists = {}
        for edge in edges:
            key = ','.join([str(x) for x in edge])
            if not(key in edge_exists):
                outf.write('%s\t%s\t%d\n' % (edge[0], edge[1], edge[2]))
                edge_exists[key] = True

if __name__ == '__main__':
    twitter_network()