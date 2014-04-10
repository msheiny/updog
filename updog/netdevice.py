"""
    This module holds NetworkDevice class. Provides abstraction to calling switch functions.
"""
import sys
import re
import os
import ConfigParser
import pexpect
import pxssh
import netvendor

class NetworkDevice(object):
    """
        This class provides an abstraction layer for running commands on switches. Initialization includes setting up the SSH connection by default. Credentials should be placed into .cfg files named for the vendor.
    """

    def __init__(cls, switch, vendor, cred_dir, vendordir, database_link=None, 
                        connect=True, debug_stdout=False, enable_pass=None,
                        retry_times=5):
        cls.vendor = netvendor.CustomVendorStrings(vendor, vendordir)
        cls.switch = switch
        cls.enpass = enable_pass
        cls.debug = debug_stdout
        cls.cmderrors = []

        if connect:
            cfg_file = os.path.join(cred_dir,vendor+".credentials")
            if not os.path.exists(cfg_file): 
                cfg_file = os.path.join(cred_dir,".credentials")
            cls.ssh_credentials = ConfigParser.RawConfigParser()
            cls.ssh_credentials.read(cfg_file)
            
            # Enable password is optional parameter
            try:
                if not enable_pass: 
                    cls.enpass = cls.ssh_credentials.get(
                                    'Credentials', 'enable')
            except ConfigParser.Error: 
                pass

            # User / pass credentials are mandatory
            try:
                user = cls.ssh_credentials.get('Credentials', 'username')
                passwd = cls.ssh_credentials.get('Credentials', 'password')
            except ConfigParser.Error:
                raise ConfigParser.Error("No valid credentials file found at"+\
                        " %s" % cfg_file)
                
            for retry in range(1,retry_times):
                try:
                    cls.connect(user, passwd, debug_stdout)
                    break
                except pexpect.ExceptionPexpect:
                    if retry == retry_times: raise
                    continue
        
    def connect(cls, user, passwd, debug):
        """ Make the pexpect SSH connection """
        cls.ssh = pxssh.pxssh()
        if debug: cls.ssh.logfile = sys.stdout
        cls.ssh.PROMPT = cls.vendor.prompt()
        cls.ssh.login(cls.switch, user, passwd, auto_prompt_reset=False,original_prompt=cls.ssh.PROMPT)
        
    def disable_pager(cls):
        """ Send commands to disable output paging """
        cls._cmd_wrapper(cmd=cls.vendor.disable_pager(),showoutput=False)

    def disconnect(cls):
        """ Disconnect the pexpect SSH connection """
        cls.ssh.logout()

    def _mutiple_cmds(cls, cmd=None, showoutput=True, prompt=None):
        """ Wrapper for calling multiple commands """
        cmdoutput = ""
        for run in cmd: 
            cmdoutput += cls._cmd_wrapper(run, showoutput, prompt)
        return cmdoutput
        
    def _cmd_wrapper(cls, cmd=None, showoutput=True, prompt=None):
        """ Wrapper for show commands """
        cls.ssh.sendline(cmd)
        if prompt: 
            cls.ssh.expect(prompt)
        elif not cls.ssh.prompt():
            raise pexpect.TIMEOUT(cmd)
        if 'error' in cls.ssh.before.lower():
            cls.cmderrors.append(cmd)
        if showoutput: 
            return re.sub(r"^{0}\s+".format(cmd),
                          "", cls.ssh.before)

    def get_config(cls, startup=True):
        """ Pull the config text for running or startup """
        if startup: 
            config = cls._cmd_wrapper(cls.vendor.show_config())
        else:
            config = cls._cmd_wrapper(cls.vendor.show_runconfig())
        return cls.vendor.filter_output(config)

    def get_version(cls):
        """ Pull version information """
        ver_data = cls._cmd_wrapper(cls.vendor.show_version())
        return cls.vendor.filter_output(ver_data, removed_str = '<filtered>',
                section = 'VERSION')

    def get_vlan(cls):
        """ Pull VLAN port information """
        return cls._cmd_wrapper(cls.vendor.show_vlan())
        
    def get_hardware_info(cls):
        """ Pull hardware information. Typically encloses multiple commands """
        hw_data = cls._mutiple_cmds(cls.vendor.show_hw())
        return cls.vendor.filter_output(hw_data, removed_str = '<filtered>',
                section = 'HW')

    def get_disk_info(cls):
        """ Pull disk information """
        pass

    def save(cls):
        """ Save config changes """
        pass

    def enable_mode(cls):
        """ Jump into enable mode if password supplied """
        enable_cmd = cls.vendor.enable_mode()
        if enable_cmd and cls.enpass:
            cls.ssh.sendline(enable_cmd[0])
            cls.ssh.expect(enable_cmd[1])
            cls.ssh.sendline(cls.enpass)
            if not cls.ssh.prompt():
                raise pexpect.TIMEOUT()
            if cls.debug: return cls.ssh.before

    def set_config(cls, cmds, write_term=True):

        """ Enter batch of commands into the switch  """
        cls.enable_mode()

        if cls.vendor.config_term():
            cls._cmd_wrapper(cls.vendor.config_term())
        cls._mutiple_cmds(cmds, prompt=cls.vendor.conf_prompt())
        if cls.vendor.leave_config():
            cls._cmd_wrapper(cls.vendor.leave_config())
        cls._cmd_wrapper(cls.vendor.save_config())
        try:
            cls._cmd_wrapper('exit')
        except pexpect.EOF: pass