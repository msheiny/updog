# Updog #

A RANCID clone written in Python. For those not familiar with RANCID,
this tool is designed to SSH to network devices, backup configs, and detect changes. It is also capable of pushing out commands for a large number of devices. 

I developed this because I needed better logic to break-out the vendor specific commands (easy extensibility) and to eventually extend with new
features. 

Right now I've only tested this against IOS and Foundry  (FastIron) devices but it is easy to extend to other switches with an SSH interface. Obviously,
I take no responsibility if this program wrecks your network. I highly advise testing it first on a device that is not in production!

## Installation ##

### Requirements ###
* `git` - dependency outside of pip
* `shell`
* `pexpect`
* `nose` - for testing

Eventually there will be two ways to install:

### Via PyPI ###
I recommend to do this via root. Otherwise if you are 
in a virtualenv, files will get copied to your virtualenv
directory:

```bash
    sudo pip install updog
```

### Manually ###

First build the installer

```bash
    python setup.py sdist
```

then you can install with pip (check the dist directory first):

```bash
    sudo pip install dist/updog-*.tar.gz
```

## Files ##
Depending on your distribution, whether you install in
root, and if you are outside of a virtualenv - files should be 
placed as follows (some of them will be auto-created (like `git`) and
otheres like `devices.list` and `.credentials` you'll need to make:

```
/
└── usr
    ├── bin
    │   ├── bark
    │   └── woof
    └── local
        └── updog
            ├── .credentials
            ├── devices.list 
            ├── git
            └── vendors
                ├── cisco.ini
                ├── extreme.ini
                └── foundry.ini
```

Scripts:

* `bark` - cli utility to push commands. 
* `woof` - cli utility to pull data and store in git. 

The following are configurable from cli arguments:

* `vendors` - place your vendor.ini files here
* `.credentials` - put credentials here
* `device.list` - put a list of devices to poll in rancid format

## Running ##

* First step is to create a `.credentials` file with the following:

```
[Credentials]
username=myuser
password=MyPa$$w0rd
```

* Next you'll want to build out a `devices.list` file in the following 
RANCID format:

```
test-switch.domain.com:cisco:up
test-switch1.domain.com:foundry:up
failure.domain.com:foundry:up
```

### Collecting data ###

`woof` will poll all devices listed in your devices.list file, store that
 into a git repository, and email/output the differences. Here are
 the command-line options. 

```bash
[msheiny:~] $ woof -h
usage: woof [-h] [-debug] [-gdir GDIR] [-vdir VDIR] [-list LIST] [-cred CRED]
            [-noemail] [-to TO]

Command-line tool to iterate through a network device list, connect to them,
run commands, save that output in git and send email alerts. 

optional arguments:
  -h, --help  show this help message and exit
  -debug      DEBUG - Display full output
  -gdir GDIR  Location of Git repository folder
  -vdir VDIR  Location of Vendor ini files
  -list LIST  Alternative list of devices.
  -cred CRED  Folder location for credentials files
  -noemail    Disable email alerting
  -to TO      Set email to address
```
You need to set `-to` if you want email and `-debug` if you'd like to see full pexpect output. 

### Pushing commands ###

`bark` will push commands to the devices you specify. Designed for making mass configuration changes.  

```bash
[msheiny:~] $ bark -h
usage: bark [-h] -run RUN [-debug] [-cred CRED] [-ena ENA] [-vdir VDIR]
            [-list LIST]

Bark - CLI tool to shoot commands to a network device list, jump into
configuration mode, enter those commands, then save those changes.

optional arguments:
  -h, --help  show this help message and exit
  -run RUN    Run custom command list. Reference to a txt file with one
              command per line.
  -debug      DEBUG - Display full output
  -cred CRED  Folder location for credentials files
  -ena ENA    Enable password
  -vdir VDIR  Location of Vendor ini files
  -list LIST  List of devices.
```

The `-run` option is required and is the location of a text file that contains
commands (one command per line), assuming you are already in config mode. For example:

```
interface GigabitEthernet 1/0/24
switchport mode access
no shutdown
switchport access vlan 2
exit
no logging console
```

## Extending ##
Definitions for prompts, commands, and filter lines is in the vendor directory. Here is an example for `cisco.ini`:

```
[PROMPT]
default=(?<=\s)\S+[#>]+
enable=[pP]assword[:]*\s*
pageoff=terminal length 0
conf=(?<=\s)\S+\(\S+\)#

[CONFIG]
confterm=conf term
leave=end
enable=enable
save=write mem
show=show config
showrun=show running-config view full
filter=(?<=secret \d )\S+(?=\s+)
filter2=(?<=key )\S+(?=\s+)
filter3=(?<=community )\S+(?=\s+)

[VERSION]
cmd=show version
filter=\d+ weeks*[\d\w \,]+

[HW]
cmd=show flash
cmd2=show boot
cmd3=show switch

[VLAN]
cmd=show vlan

```

Note that the CONFIG and VERSION section have filter options. This is designed to filter out potentially sensitive information and data that constantly changes that you don't care about. In certain sections like HW you can also specify multiple commands as long as the parameter in the `ini` file starts with 'cmd'. 

## Testing ##
Tests are currently functional tests. Clone down this folder, 
make changes, and then run `nosetests` from here. I recommend, 
`nosetests -v -s`. If you want to add new vendors, you'll have to place
an appropriate $vendor.ini in the vendors folder and extend the tests.

## To-Do ##

* Configuration compliance checking  
* Improve output on bark and woof
* Improve error handling and ability to re-run problematic devices
* Better targeting for pushing commands
* Add more vendors (juniper and fortigate next)
* Add more unit tests and re-factor some logic
