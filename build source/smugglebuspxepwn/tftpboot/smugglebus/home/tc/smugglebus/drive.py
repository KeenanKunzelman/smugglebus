import subprocess


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
    def  is_mounted(self):
        proc = subprocess.Popen('sudo mount',
                stdout=subprocess.PIPE, shell=True) 
        (mounted_drives, err) = proc.communicate()
        mounted_drives = mounted_drives.decode('utf-8')
        if self.get_source() in mounted_drives:
            return 'yes'
        else:
            return 'no'
    
    
