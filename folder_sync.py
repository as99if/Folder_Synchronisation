import hashlib
import os
import sys
import logging
import time
import shutil


def compare_files(file1, file2) -> bool:
    """
    Compare two files with hash
    :param file1: str (Path to file1)
    :param file2: str (Path to file2)
    :return: True if file is the same, False if file is different
    """
    #
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            if hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest():
                return True
            else:
                return False


def compare_hash_folder(_folder, _replica) -> bool:
    """
    Compare hash folder
    :param _folder: str (Path to source folder)
    :param _replica: str (Path to replica folder)
    :return: True if all file is same, False if any file is different
    """

    _files = os.listdir(_folder)
    _files_replica = os.listdir(_replica)

    if len(_files) != len(_files_replica):
        return False
    for _file in _files:
        if _file in _files_replica:
            if os.path.isdir(_folder + "/" + _file):
                if not compare_hash_folder(_folder + "/" + _file, _replica + "/" + _file):
                    return False
            else:
                if not compare_files(_folder + "/" + _file, _replica + "/" + _file):
                    return False
        else:
            return False
    return True


def sync(source_folder, replica_folder, interval):
    """
    Continuous synchronize between two folders, with interval time.
    :param source_folder: str (Path to source folder)
    :param replica_folder: str (Path to replica folder)
    :param interval: int (Interval between synchronisation in ms)
    :return: None
    """
    if not os.path.isdir(source_folder):
        logging.infoging.info("source folder not found")
        exit()

    if not os.path.isdir(replica_folder):
        logging.infogin.info("replica folder not found")
        exit()

    # run loop every 5 minutes
    while True:
        # check folder
        if os.path.isdir(source_folder):
            logging.info("source folder exists")
        else:
            logging.info("source folder does not exist")
            break
        # check backup
        if os.path.isdir(replica_folder):
            logging.info("replica folder exists")
        else:
            logging.info("replica folder does not exist")
            break

        # check if folder is same with backup
        if compare_hash_folder(source_folder, replica_folder):
            logging.info("file is up to date")
            # time interval
            time.sleep(interval)
            continue

        # check file hash in folder and compare with backup
        count_sync = 0
        count_update = 0
        count_delete = 0
        # get all file in folder
        files_source = os.listdir(source_folder)
        # get all file in backup
        files_replica = os.listdir(replica_folder)
        # compare two folders
        for file in files_replica:
            if file in files_source:
                if os.path.isdir(replica_folder + '/' + file):
                    if compare_hash_folder(source_folder + "/" + file, replica_folder + '/' + file):
                        logging.info(f"{file} is up to date")
                        count_sync += 1
                    else:
                        # count_update file in replica_folder from source_folder
                        count_update += 1
                        shutil.rmtree(replica_folder + "/" + file)
                        shutil.copytree(source_folder + "/" + file, replica_folder + "/" + file)
                        logging.info(f"{file} is updated")
                else:
                    if compare_files(source_folder + "/" + file, replica_folder + '/' + file):
                        logging.info(f"{file} is up to date")
                        count_sync += 1
                    else:
                        # count_update file in replica_folder from source_folder
                        count_update += 1
                        os.remove(replica_folder + "/" + file)
                        shutil.copy2(source_folder + "/" + file, replica_folder)
                        logging.info(f"{file} is updated")

            elif file not in files_source:
                # count_delete file in backup
                if os.path.isdir(replica_folder + "/" + file):
                    shutil.rmtree(replica_folder + "/" + file)
                else:
                    os.remove(replica_folder + "/" + file)
                logging.info(f"{file} is deleted")
                count_delete += 1

        for file in files_source:
            if file not in files_replica:
                # copy file from source_folder to replica_folder
                if os.path.isdir(source_folder + "/" + file):
                    shutil.copytree(source_folder + "/" + file, replica_folder + "/" + file)
                else:
                    shutil.copy2(source_folder + "/" + file, replica_folder)

                count_update += 1
                logging.info(f"{file} is copied")

        logging.info(f"sync: {count_sync}; update: {count_update}; delete: {count_delete} ;")
        # time interval
        time.sleep(interval)


if __name__ == "__main__":
    _source_folder = sys.argv[1]
    _replica_folder = sys.argv[2]
    _interval = sys.argv[3]
    _log_file_path = sys.argv[4]
    logging.basicConfig(filename=_log_file_path, encoding='utf-8', level=logging.INFO,
                        datefmt='%d-%b-%y %H:%M:%S',
                        format='%(asctime)s - %(message)s')
    sync(_source_folder, _replica_folder, int(_interval))
