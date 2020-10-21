import subprocess


class Drive:
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
    
    
