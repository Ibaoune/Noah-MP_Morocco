import sys, os
from datetime import datetime
sys.path.append('src')
import run_postproc
data_dict = {}
data_dict['start_date'] = datetime.strptime('2016-01-01', '%Y-%m-%d')
data_dict['end_date'] = datetime.strptime('2016-12-31', '%Y-%m-%d')
import glob
files = glob.glob('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016/DA_nocdf_noirr_2016/EnKF/*/*_innov.a01.d01.nc')
data_dict['files_da_nocdf'] = files
from assimilation_diagnostics.plot_innovation import plot_innovation_increment
print("Files:", len(files))
print("Running plot_innovation_increment...")
res = plot_innovation_increment(data_dict, 'figures/matrix_2016/assimilation_diagnostics/')
print("Result:", res)
