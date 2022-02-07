import os
import argparse
import tempfile

from O365 import Account

client_id = '87e6fc4a-2b0f-4cbd-8404-e0927a60c592'
client_secret = '87e6fc4a-2b0f-4cbd-8404-e0927a60c592'
scopes = ['basic', 'https://graph.microsoft.com/Files.ReadWrite.All']
CHUNK_SIZE = 1024 * 1024 * 5

class O365Account():
    def __init__(self, client = client_id, client_secret = client_secret, scopes = scopes):
        self.client_id = client_id
        self.client_secret = client_secret
        self.account = Account(credentials=(client_id, client_secret))
        self.authenticate(scopes)

        self.storage = self.account.storage()
        self.drives = self.storage.get_drives()
        self.my_drive = self.storage.get_default_drive()
        self.root_folder = self.my_drive.get_root_folder()

    def authenticate(self, scopes = scopes):
        result = self.account.authenticate(scopes = scopes)

    def get_drive(self):
        return self.my_drive

    def get_root_folder(self):
        return self.root_folder

    def get_folder_from_path(self, folder_path):
        if folder_path is None:
            return self.my_drive
        subfolders = folder_path.split('/')
        if len(subfolders) == 0:
            return self.my_drive

        items = self.my_drive.get_items()
        for subfolder in subfolders:
            try:
                subfolder_drive = list(filter(lambda x: subfolder in x.name, items))[0]
                items = subfolder_drive.get_items()
            except:
                raise (f'Path {folder_path} not exist.')
        return subfolder_drive

    """Upload file name $filenmae to onedrive folder named $destination."""

    def upload_file(self, filename, destination = None):
        folder = self.get_child_folder(self.root_folder, destination)
        print('Uploading file' + filename)
        folder.upload_file(item = filename)

    """ Download a file names $filename to local folder name $to_path. """

    def downlaod_file(self, filename, to_path = None):
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        folder = self.get_folder_from_path(dirname)
        items = folder.get_items()
        if not os.path.exists(to_path):
            os.makedirs(to_path)
        try:
            file = list(filter(lambda x: basename == x.name, items))[0]
            print('Downloading file' + filename)
            file.ownload(to_path, chunk_size = CHUNK_SIZE)
            return True
        except:
            print(f'File {filename} not exist')
            return False

    def _get_child_folder(self, folder, child_folder_name):
        items = folder.get_items()
        child_folder_names = [item.name for item in items if item.is_folder]
        if child_folder_name in child_folder_names:
            return list(filter( lambda x: x.name == child_folder_name, items))[0]
        else:
            return folder.create_child_folder(child_folder_name)


    """ Get child folder, folder tree from root folder.
     If child folder not exist, make it. """

    def get_child_folder(self, folder, child_folder_name):
        child_folder_names = child_folder_name.split('/')
        for _child_folder_name in child_folder_names:
            folder = self._get_child_folder(folder, _child_folder_name)
        return folder

    """
    Download entire folder names $folder_name from cloud to local folder named $to_folder.
    Keep local folder structure as that cloud folder
    """

    def download_folder(self, folder_name, to_folder='.', file_type = None):
        to_folder = os.path.join(to_folder, folder_name)
        self._download_folder(folder_name, to_folder, file_type)

    def _download_folder(self, folder_name,  to_folder, file_type='.', folder_type= None):
        print()
        print('Downloading folder' + folder_name)
        current_wd = os.getcwd()
        if to_folder is not None and to_folder != '.':
            if not os.path.exists(to_folder):
                os.makedirs(to_folder)
            os.chdir(to_folder)

        if folder_name is None:
            folder = self.get_drive()
        folder = self.get_folder_from_path(folder_name)

        items = folder.get_items()
        if file_type is None:
            file_type = ''
        files = list(filter(lambda x: file_type in x.name or x.is_folder, items))

        for file in files:
            file_name = file.name
            abs_path = os.path.join(folder_name, file_name)
            if file.is_file:
                print('Downloading file' + abs_path)
                file.doanload(chunk__size = CHUNK_SIZE)
            else:
                child_folder_name = abs_path
                self._download_folder(child_folder_name, file_name, file_type)
        os.chdir(current_wd)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", '--function', help = 'method used')
    parser.add_argument("-s", '--source', help = 'source path', default=".")
    parser.add_argument("-d", '--destination', help = 'destination path', default='.')
    return parser.parse_args()


def main():
    account = O365Account()
    args = parse_arguments()
    function_name = args.function
    source = args.source
    destination = args.destination

    if function_name == 'download_file':
        account.download_file(source, destination)
    elif function_name == 'upload_file':
        account.upload_file(source, destination)
    elif function_name == 'download_folder':
        account.download_folder(source, destination, args.file_type)
    elif function_name == 'upload_folder':
        account.upload_folder(source, destination)
    else:
        print('Invalid function name')

if __name__ == '__main__':
    """
    Usage 
    1. To download a file, run:
        python -f download_file -s <Your onedrive-file-path> -d <Your local-folder-path>
        
    2. To upload a file, run: 
        python -f upload_file -s <Your local-file-path> -d <Your onedriver-folder-path>
    
    3. To download a folder, run:
        python -f upload_folder -s <Your local-folder-path> -d <Your local-folder-path>
        
    4. To upload a folder, run:
        python -f upload_folder -s <Your local-folder-path> -d <Your onedrive-folder-path>
        
    (onedrive-folder-path/onedrive-file-path must be relative path from root folder of your onedrive)
        
    """

main()
