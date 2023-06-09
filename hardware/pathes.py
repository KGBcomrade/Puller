import os

ximc_lib_path = r'd:/TrustSoftware/XIMC_Software_package-2023.01.19-win32_win64/libximc-2.13.6-all.tar/ximc-2.13.6/ximc/win64'
os.add_dll_directory(ximc_lib_path)
key_path = os.path.join(ximc_lib_path, 'keyfile.sqlite')

save_path = 'D:\\TrustSoftware\\5 Oscill\\Waveforms'