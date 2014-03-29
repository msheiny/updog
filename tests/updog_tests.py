
import unittest
import shell
import os
import shutil
from updog import netvendor

class FakeSSHEnvSetup(object):

    def setup(cls):
        # override system path to add in fake ssh executable
        cls.orig_path = os.environ.get('PATH')
        fakessh_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        os.environ['PATH'] = fakessh_dir + \
                    ((os.pathsep + cls.orig_path) if cls.orig_path else '')

    def teardown(cls):
        # Restore original path
        if cls.orig_path:
            os.environ['PATH'] = cls.orig_path
        else:
            del os.environ['PATH']

class VendorIniTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.dirname(__file__)
        cls.vendor = netvendor.CustomVendorStrings("cisco",vendorfolder="./vendors")
        config_file = open(os.path.join(
                    cls.test_dir,'cisco-test-config.txt'),'r')
        cls.config = ''.join(config_file.readlines())
        config_file.close()

    def test_filter(cls):
        """ Make sure the config filter functionality is working  """
        filtered_conf = cls.vendor.filter_output(cls.config, 
                removed_str="<FILTERED>", section="CONFIG")
        filtered_file = open(os.path.join(cls.test_dir,
                        'cisco-test-filteredconfig.txt')).readlines()
        filtered_file_read = ''.join(filtered_file)
        cls.assertEquals(filtered_conf, filtered_file_read)

class WoofFunctionalTest(unittest.TestCase):   
    """ Woof functional run with fake SSH sessions """
    @classmethod
    def setUpClass(cls):
        cls.ssh = FakeSSHEnvSetup()
        cls.ssh.setup()

        # determine paths for setting up woof script test
        root_test = '/tmp/testupdog'
        cls.git = os.path.join(root_test,'git')
        thisdir = os.path.dirname(os.path.realpath(__file__)) 
        cls.list_file = os.path.join(thisdir,'test.list')
        vendor = os.path.join(thisdir,'../vendors')
        os.environ['PYTHONPATH'] = os.path.join(thisdir,'../')
        cli = "./bin/woof -cred {c} -vdir {v} -gdir {g} -list {l} -noemail".format(v=vendor, g=cls.git,
                             c=thisdir, l=cls.list_file)
        cls.sh = shell.shell(cli)

        device_list = open(cls.list_file).readlines()
        cls.hosts = [host.split(':')[0] for host in device_list]        
        cls.out_files = ['config','hw','runconfig','version','vlan']
        cls.shell_output = '\n'.join(cls.sh.output())
        
    @classmethod
    def tearDownClass(cls):
        cls.ssh.teardown()
        shutil.rmtree(cls.git)

    def test_simple(cls):
        """ Woof - Make sure the path is working with tests.  """
        sh = shell.shell('./bin/woof -h')
        cls.assertEqual(sh.code, 0)

    def _check_git_paths(cls, success):
        for h in cls.hosts:
            for check_file in cls.out_files:
                file_path = os.path.exists(os.path.join(cls.git,
                               h,check_file))
                if 'fail' in h and not success: cls.assertFalse(file_path)
                elif not 'fail' in h and success: cls.assertTrue(file_path)

    def test_woof_successes(cls):
        """ Woof - Confirm successful config pulls """
        cls._check_git_paths(success=True)
        for host in [h for h in cls.hosts if not 'fail' in h]:
            cls.assertIn("+ {}".format(host), cls.shell_output) 

    def test_woof_failures(cls):
        """ Woof - Confirm failed config pulls """
        cls._check_git_paths(success=False)
        cls.assertIn('failure.domain.com: Error contacting', cls.shell_output)
        
    def test_basic_woof_check(cls):
        """ Woof - Make sure woof is running without failures"""
        # Check to make sure no errors and exit code 0
        cls.assertEquals(cls.sh.errors(),[])
        cls.assertEquals(cls.sh.code,0)

class BarkFunctionalTest(unittest.TestCase):   
    """ Bark functional run with fake SSH sessions """
    @classmethod
    def setUpClass(cls):
        cls.ssh = FakeSSHEnvSetup()
        cls.ssh.setup()

        # determine paths for setting up woof script test
        root_test = '/tmp/testupdog'
        cls.git = os.path.join(root_test,'git')
        thisdir = os.path.dirname(os.path.realpath(__file__)) 
        cls.list_file = os.path.join(thisdir,'test.list')
        run_file = os.path.join(thisdir,'run-interface.txt')
        vendor = os.path.join(thisdir,'../vendors')
        os.environ['PYTHONPATH'] = os.path.join(thisdir,'../')
        cls.cli = "./bin/bark -ena {e} -r {r} -cred {c} -vdir {v} -list {l}".format(v=vendor, c=thisdir, 
                    e='EnABlEm3',
                    r= run_file,
                    l=cls.list_file)
        cls.sh = shell.shell(cls.cli)
        device_list = open(cls.list_file).readlines()
        cls.hosts = [host.split(':')[0] for host in device_list]        
        cls.out_files = ['config','hw','runconfig','version','vlan']
        cls.shell_output = '\n'.join(cls.sh.output())
        
    @classmethod
    def tearDownClass(cls):
        cls.ssh.teardown()
        
    def test_simple(cls):
        """ Bark - simple test  """
        cls.assertIsNotNone(cls.shell_output)
        cls.assertEquals(cls.sh.code, 0)
        cls.assertEquals(cls.sh.errors(),[])      

    def test_check_error_output(cls):
        """ Bark - confirm failure output  """
        cls.assertIn('failure.domain.com: Error contacting', cls.shell_output)

    def test_check_good_output(cls):
        """ Bark - confirm success output  """
        for host in [h for h in cls.hosts 
                        if 'fail' not in h]:
            cls.assertIn('+ {0}'.format(host), cls.shell_output)

    def test_cmd_issue(cls):
        """ Bark - confirm command error output  """
        for host in [h for h in cls.hosts 
                        if 'fail' not in h]:
            cls.assertIn("~ {0}, cmd 'interfce Gi 1/1".format(
                         host), cls.shell_output)
        
if __name__ == '__main__':
        unittest.main()
