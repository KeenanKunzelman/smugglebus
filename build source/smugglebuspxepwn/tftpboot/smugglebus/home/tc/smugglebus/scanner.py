import sys, subprocess, argparse, time, shutil, os, datetime

from drive import Drive

# this is for implanter, but wouldnt it be cool if we checked to see if we passed
# the drive obj to every implanter attack, and checked to make sure it was mounted


# Rename pretty_print(target_fs) to scan(target_fs) 
# implement an instance of scanner class in the implanter class to show 
# vulnerable drives when carrying out attacks.
# Maybe new scan(target_fs) method should return a list of the targeted drives.

class Scanner:

    # Run the command sudo blkid and then recieve its output as a bytes
    # Decode using utf-8 and then split on \n
    # Returns a list of drive paths and their file systems

    # this is like grab_drives()
    # Process output from blkid, store in self.drives on the scanner object
    # self.drives is a list of objects created from Drive class

    def __init__(self):
        proc = subprocess.Popen('sudo blkid', stdout=subprocess.PIPE, 
                shell=True)
        (drives, err) = proc.communicate()
        drives = drives.decode('utf-8').split('\n')

        connected_drives = []
        for i in range(len(drives)):
            temp_drive = Drive()
            temp_source = ''
            temp_fs = ''
            temp_raw_drive = drives[i].split()
            for attribute in temp_raw_drive:
                if '/dev' in attribute:
                    attribute = list(attribute)
                    attribute.pop()
                    attribute = ''.join(attribute) 
                    temp_drive.set_source(attribute)
                elif 'TYPE' in attribute:
                    temp_drive.set_fs(attribute)
            connected_drives.append(temp_drive)
        self.drives = connected_drives 
    # extracts the drives with ntfs types
    # returns a list of windows drives
    
    def target_drive(self, target_drive):
        return self.drives[int(target_drive)]
    
    
    def pretty_print(self, target):
        # takes as input an instance of the Drive class and prints
        # out useful data about the given drive.

        # subprocess.call('cat assets/ascii_art', shell=True)

        if target == 'ntfs':
            win_drives = []
            for drive in self.drives:
                if 'ntfs' in drive.get_fs():
                    win_drives.append(drive)
                    self.drives = win_drives

        print('\n\n     *******************************************************'
                    '***************     ',
                    end ='')
        print('\n     *******************A TABLE OF ALL CONNECTED'
                    ' DRIVES********************', 
                    end ='')
        print('\n     *******************************************************'
                    '***************     ',
                    end ='') 
        print('\n     *\t\t Drive Location\t      File System\t'
                    'Mounted\t\t  *',end ='')
        drive_count = 0
        for drive in self.drives:
            if len(drive.get_source()) > 10:
                print('\n     *\t\t {} {}      {}\t  '
                            '{}\t\t  *'.format(drive_count, drive.get_source(), 
                                drive.get_fs(), drive.is_mounted()), end='')
                drive_count += 1
            if len(drive.get_fs()) > 6 and len(drive.get_source()) < 10:
                print('\n     *\t\t {} {}\t      {}\t  '
                            '{}\t\t  *'.format(drive_count, drive.get_source(), 
                                drive.get_fs(), drive.is_mounted()), end='')
                drive_count += 1
            elif len(drive.get_fs()) == 4:
                print('\n     *  {}\t      {}\t  '
                            '{}\t\t  *'.format(drive.get_source(), 
                                drive.get_fs(), drive.is_mounted()), end='')
                drive_count += 1
        print('\n     *******************************************************'
                    '***************     ',
                    end ='\n')
    @staticmethod
    def grab_drives():
        proc = subprocess.Popen('sudo blkid', stdout=subprocess.PIPE, 
                shell=True)
        (drives, err) = proc.communicate()
        drives = drives.decode('utf-8').split('\n')
        return drives
    @staticmethod
    def locate_winfs(drives):
        win_drives = []
        for drive in drives:
            if 'ntfs' in drive:
                win_drives.append(drive)
        return win_drives

    @staticmethod
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

    @staticmethod
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
        
    @staticmethod
    def check_for_windrives(raw_drives):
        #looking back this code is actually so trash. Gotta refactor.
        drive_count = 0
        raw_win_drives = Scanner.locate_winfs(raw_drives)
        win_drives = Scanner.store_drives(raw_win_drives)
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
            Scanner.mount_drive(win_drives[int(target)])
            return True
