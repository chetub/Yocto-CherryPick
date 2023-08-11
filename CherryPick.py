#!/usr/bin/python3

from functions import *

if __name__ == "__main__":    
    args = json_arg_parser()
    gerrit_numbers = get_gerrits_numbers(args)
    cherry_pick_gerrits (gerrit_numbers,'nets-tcam-deps')

    