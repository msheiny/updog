"""
    This module contains CustomVendorStrings class which acts as an 
    abstraction layer for multiple vendors commands.
"""

import re
import ConfigParser
import os

class CustomVendorStrings(object):
    """
        This is an abstract class for determining the correct commands to run according to vendor type. You'll need to make a separate $vendor.ini file to handle this.
    """

    def __init__(cls, vendor, vendorfolder="./"):
        """ Start-off indicating the string of the vendor you are looking up"""
        cls.vendor_strings = ConfigParser.RawConfigParser()
        try:
            cfg_file = os.path.join(vendorfolder,vendor+".ini")
            cls.vendor_strings.read(cfg_file)
        except:
            cls.vendor_strings.read('switch.ini')

    def prompt(cls):
        """ Return the regex for the switch standard prompt """
        return cls.vendor_strings.get('PROMPT', 'default')

    def conf_prompt(cls):
        """ Return the regex for the switch config prompt """
        try:
            return cls.vendor_strings.get('PROMPT', 'conf')
        except ConfigParser.NoOptionError, ConfigParser.NoOptionError: 
            return None

    def disable_pager(cls):
        """ Return command to disable paging in terminal """
        return cls.vendor_strings.get('PROMPT', 'pageoff')

    def show_version(cls):
        """ Return the command to display switch version information """
        return cls.vendor_strings.get('VERSION', 'cmd')

    def show_hw(cls):
        """ Returns list of commands to run on switch to show hardware"""
        return [cmd for tag,cmd in cls.vendor_strings.items('HW') if tag.startswith('cmd')]

    def show_vlan(cls):
        """ Returns command to run on switch to show vlan data"""
        return cls.vendor_strings.get('VLAN', 'cmd')

    def show_config(cls):
        """ Return the command to display switch config information """
        return cls.vendor_strings.get('CONFIG', 'show')    

    def show_runconfig(cls):
        """ Return the command to display running switch config information """
        return cls.vendor_strings.get('CONFIG', 'showrun')

    def filter_output(cls, config, removed_str="<REMOVED>", section='CONFIG'):
        """ Pipe through raw outputtext and use regex patterns in the 
            .ini to yank out text 
        """
        tag_start = 'filter'
        replacement_tag_end = '_replacement'
        filters = [regex for tag,regex in cls.vendor_strings.items(section) if tag.startswith(tag_start)]
        filters = {tag: regex for tag,regex in cls.vendor_strings.items(section) if tag.startswith(tag_start) and not tag.endswith(replacement_tag_end)}
        replacements = {tag: replacement for tag,replacement in cls.vendor_strings.items(section) if tag.startswith(tag_start) and tag.endswith(replacement_tag_end)}
        for tag in filters.keys():
            r = re.compile(filters[tag])
            if replacements.has_key(tag + replacement_tag_end):
                config = r.sub(replacements[tag + replacement_tag_end], config)
            else:
                config = r.sub(removed_str, config)
        return config

    def config_term(cls):
        """ Return configuration mode commands """
        try:
            return cls.vendor_strings.get('CONFIG', 'confterm')
        except ConfigParser.NoSectionError: return None

    def leave_config(cls):
        """ Return configuration leave command """
        try:
            return cls.vendor_strings.get('CONFIG', 'leave')
        except ConfigParser.NoSectionError: return None

    def save_config(cls):
        """ Return save configuration command """
        try:
            return cls.vendor_strings.get('CONFIG', 'save')
        except ConfigParser.NoSectionError: return None

    def enable_mode(cls):
        """ Jump into enable mode """
        try:
            return (cls.vendor_strings.get('CONFIG', 'enable'),
                    cls.vendor_strings.get('PROMPT', 'enable'))
        except ConfigParser.NoSectionError: return None
