import subprocess

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
                drive_count += 1
                print('\n     *\t\t {} {}      {}\t  '
                            '{}\t\t  *'.format(drive_count, drive.get_source(), 
                                drive.get_fs(), drive.is_mounted()), end='')
    
            if len(drive.get_fs()) > 6 and len(drive.get_source()) < 10:
                drive_count += 1
                print('\n     *\t\t {} {}\t      {}\t  '
                            '{}\t\t  *'.format(drive_count, drive.get_source(), 
                                drive.get_fs(), drive.is_mounted()), end='')
            elif len(drive.get_fs()) == 4:
                drive_count += 1
                print('\n     *  {}\t      {}\t  '
                            '{}\t\t  *'.format(drive.get_source(), 
                                drive.get_fs(), drive.is_mounted()), end='')
        print('\n     *******************************************************'
                    '***************     ',
                    end ='\n')
