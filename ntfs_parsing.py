
# 파일 추출 프로그램

file = open('NTFS_image', 'rb')
def mftentry_start():
    file.seek(11)
    Bytes_per_sector = list(file.read(2))
    Bytes_per_sector.reverse()
    for i in range(len(Bytes_per_sector)):                
            Bytes_per_sector[i] = "{:02x}".format(Bytes_per_sector[i])
    Bytes_per_sector = ''.join(Bytes_per_sector) 
    Bytes_per_sector = int(Bytes_per_sector, 16)

    file.seek(13)
    Sectors_per_cluster = list(file.read(1))
    for i in range(len(Sectors_per_cluster)):                
            Sectors_per_cluster[i] = "{:02x}".format(Sectors_per_cluster[i])
    Sectors_per_cluster = ''.join(Sectors_per_cluster) 
    Sectors_per_cluster = int(Sectors_per_cluster, 16)

    file.seek(48)
    cluster_num_mft = list(file.read(4))
    cluster_num_mft.reverse()
    for i in range(len(cluster_num_mft)):                
            cluster_num_mft[i] = "{:02x}".format(cluster_num_mft[i])
    cluster_num_mft = ''.join(cluster_num_mft) 
    cluster_num_mft = int(cluster_num_mft, 16)

    mft_entry_start = Bytes_per_sector * Sectors_per_cluster * cluster_num_mft
    return mft_entry_start, Bytes_per_sector, Sectors_per_cluster

#=========================== mft entry 찾음

def file_find(real_file):
    data_sig_loc = 0
    while True:
        file.seek(real_file)
        data_sig = list(file.read(4))              
        for i in range(len(data_sig)):                
            data_sig[i] = "{:02x}".format(data_sig[i]) 
        data_sig = ''.join(data_sig)
        if data_sig == '80000000':
            file.seek(real_file - 4)
            data_sig_loc_check = list(file.read(4))
            for i in range(len(data_sig_loc_check)):
                data_sig_loc_check[i] = "{:02x}".format(data_sig_loc_check[i])
            data_sig_loc_check = ''.join(data_sig_loc_check)
            if data_sig_loc_check == '30000000':
                data_sig_loc += 4
                real_file += 4
            else : 
                break
        else :
            data_sig_loc += 4
            real_file += 4
    return data_sig_loc


def file_data_(data_sig_loc, real_file) :           #resident인지 non-resident인지
    data_sig_loc = file_find(real_file)             #real_file + data_sig_loc = 80000000
    file_data = real_file + data_sig_loc + 8
    file.seek(file_data)
    file_data_ = list(file.read(1))
    for i in range(len(file_data_)):                
            file_data_[i] = "{:02x}".format(file_data_[i])
    file_data_ = ''.join(file_data_) 
    file_data_ = int(file_data_, 16)
    return file_data_

def file_size_(real_file, data_sig_loc) : 
    file.seek(real_file + data_sig_loc + 56)
    file_size = list(file.read(8))
    file_size.reverse()
    for i in range(len(file_size)):
        file_size[i] = "{:02x}".format(file_size[i])
    file_size = ''.join(file_size)
    file_size = int(file_size, 16)
    return file_size

def run_list(file_data_, real_file, data_sig_loc) :
    if file_data_ == 1:
        runlist_loc = real_file + data_sig_loc + 64
        file.seek(runlist_loc)
        runlist = list(file.read(1))
        for i in range(len(runlist)):                
            runlist[i] = "{:02x}".format(runlist[i])
        runlist = ''.join(runlist) 
        onerunlist = (int(runlist) % 10)
        tenrunlist = int(int(runlist)/10)
        run_list = tenrunlist + onerunlist
        file.seek(runlist_loc + 1)
        runlist = list(file.read(run_list))
        for i in range(len(runlist)):                
            runlist[i] = "{:02x}".format(runlist[i])
        run_offset = []
        for i in range(onerunlist, tenrunlist + 1):
            run_offset.append(runlist[i]) 
        run_offset.reverse()
        run_offset = ''.join(run_offset)
        run_offset = int(run_offset, 16)
        return(run_offset)  

def file_loc(run_offset, Bytes_per_sector, Sectors_per_cluster) : 
    file_loc = run_offset * Bytes_per_sector * Sectors_per_cluster
    return file_loc

def file_name(real_file):
    file_name_loc = 0
    in_real_file = real_file
    while True:
        file.seek(in_real_file)
        file_name = list(file.read(4))              
        for i in range(len(file_name)):                
            file_name[i] = "{:02x}".format(file_name[i]) 
        file_name = ''.join(file_name)
        if file_name == '30000000':
            break
        else :
            file_name_loc += 4
            in_real_file += 4
    file_name_loc = file_name_loc + 16 + 64 + 8
    file.seek(real_file + file_name_loc)
    file_name_size = list(file.read(1))
    for i in range(len(file_name_size)):
        file_name_size[i] = "{:02x}".format(file_name_size[i])
    file_name_size = ''.join(file_name_size)
    file_name_size = int(file_name_size,16)
    file.seek(real_file + file_name_loc + 2)
    file_name = list(file.read(file_name_size * 2))
    for i in range(len(file_name)):
        file_name[i] = "{:02x}".format(file_name[i]) 
        file_name[i] = int(file_name[i], 16)
    file_real_name = []
    for j in range(len(file_name)):
        if  file_name[j] != 0:   
            file_real_name.append(chr(file_name[j]))    
    file_name = ''.join(file_real_name)
    file.seek(real_file + 22)
    folder = list(file.read(2))
    folder.reverse()
    for i in range(len(folder)):
        folder[i] = "{:02x}".format(folder[i])
    folder = ''.join(folder)
    if (folder == '0002') | (folder == '0003'):
        return 0
    else : return file_name

def file_save(file_location, file_real_size, file_save_name):
    file.seek(file_location)
    new_file = open(file_save_name, "wb")
    new_file_context = file.read(file_real_size)
    new_file.write(new_file_context)
    new_file.close

def file_data_resident(data_sig_loc, real_file):
    file_data_size = data_sig_loc + real_file + 16
    file.seek(file_data_size)
    file_size = list(file.read(4))
    file_size.reverse()
    for i in range(len(file_size)):
        file_size[i] = "{:02x}".format(file_size[i])
    file_size = ''.join(file_size)
    file_size = int(file_size, 16)
    file.seek(file_data_size + 4)
    file_data = list(file.read(2))
    file_data.reverse()
    for i in range(len(file_data)):
        file_data[i] = "{:02x}".format(file_data[i])
    file_data = ''.join(file_data)
    file_data = int(file_data, 16)
    file_data_loc = real_file + data_sig_loc + file_data
    return file_size, file_data_loc
    

def run() : 
    mft_entry_start, Bytes_per_sector, Sectors_per_cluster = mftentry_start()

    i = 39
    folder = 0
    file = 0
    while i <= 47 : 
        real_file = mft_entry_start + 1024 * i

        data_sig_loc = file_find(real_file)
        file_data__ = file_data_(data_sig_loc, real_file)
        if file_data__ == 1:
            file_real_size = file_size_(real_file, data_sig_loc)
            file_save_name = file_name(real_file)
            if file_save_name == 0 : 
                    folder += 1
            else : 
                run_offset = run_list(file_data__, real_file, data_sig_loc)
                file_location = file_loc(run_offset, Bytes_per_sector, Sectors_per_cluster)
                file_save(file_location, file_real_size, file_save_name)
                file += 1
        elif file_data__ != 1:
            file_save_name = file_name(real_file)
            if file_save_name == 0 : 
                folder += 1
            else : 
                file_size, file_data_loc = file_data_resident(data_sig_loc, real_file)
                file_save(file_data_loc, file_size, file_save_name)
                file += 1

        i = i + 1
    print("folder : %d, file : %d" %(folder,file))   

if __name__=="__main__":
    run()
    file.close()


