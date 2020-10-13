'''
Abaqus babysitting/kill code

Last updated: 9/9/2020 by Patrick Walgren 
Originally created by the honorable Pedro Leal

This script operates as a wrapper around any Abaqus process and monitors its status.
The script waits until Abaqus is complete (signified by the *.exe processes ceasing to 
exist) and then passes information back to the optimization/DOE, or will kill all associated
processes if Abaqus stalls somewhere (sometimes Abaqus will get hung up and not do anything for
hours). Note: This script is analysis- and VERSION-specific. There are process names that 
must be changed according to the specific Abaqus version you are running. 

Files needed:
    -The abaqus script that runs the job ('AssemblyModifyEdit.py' in this case)
    -The I/O files required to pass data from the optimizer to Abaqus (input.p, input.mat,output.p,
    and output.mat in this case) The output/input pickles (.p files) and matlab matrices (.mat files)
    are for passing information between python and matlab.

                   

Things to change for a different analysis: 
    -Any changes in I/O file names must be accounted for. These are all initialized on lines 
    149-155. 
    -If the design vector gets saved as something different than 'x', this must be accounted 
    for on line 178.
    -The master optimization record gets written to on line 200 if the job times out. Be sure to
    modify both the magnitudes of the penalized outputs for the specific design problem, as well as
    the file name associated with the optimization. 
    -Depending on the run time of your specific analysis, the variables time_terminate and 
    increment_time should be changed. These can be changed on lines 176 and 178, respectively. 
    The smaller the increment time, the less "slop" you'll have (where the kill code is waiting
    but abaqus has already completed), but with more print statements (which may contribute to 
    unneccesary overhead).
    
Things to change for a different VERSION:
    -All abaqus executables must be change. For Abaqus/2018, these are abq2018.exe. They are found
    on lines 57,58, and 202. All "pre.exe", "standard.exe", etc. calls should stay the same.
    
    
To-do:
    -Initialize the variable associated with the design vector earlier in the code, instead
    of being buried in the np.savetxt command.

'''

import os
import time
import math
import pickle
import json
import win32api
import subprocess as sp

import scipy.io
import numpy as np


# from DOE_FullFactorial import DOE
# from wing_model import model

def enhanced_waitForCompletion(processes_to_track = ['ABQcaeK.exe', 'abq2018.exe','pre.exe', 'standard.exe'],
                                processes_to_kill = ['ABQcaeK.exe', 'abq2018.exe','pre.exe', 'standard.exe'],
                                increment_time=30., max_time=3600., not_on_kill_list = []):
    flag = False
    # Need to wait to get into standard

    current_time = 0
    process_exists = True
    print('Start waiting')
    while max_time>current_time and process_exists == True:
        time.sleep(increment_time)
        current_time += increment_time
        tasklistrl = os.popen("tasklist").readlines()

        process_exists = False
        for process in processes_to_track :
            for examine in tasklistrl:
                if process == examine[0:len(process)]:
                    pid = int(examine[29:34])
                    if pid not in not_on_kill_list:
                        process_exists = True
        if process_exists:
            print('Current run time: ' + str(current_time))
        else:
            print('Current run time: ' + str(current_time) + '. DONE!')

        
    # If max running time was achieved and still not done, KILL!!
    if max_time>=current_time and process_exists == True:
        
        flag = True
        print('TIME TO KILL')
        for process in processes_to_kill:
            try:
                kill(str(process), tasklistrl, not_on_kill_list)
            except:
                pass
         
    # If done, why even complain?! Just get out of there
    
    return flag

def kill(process, tasklistrl=None, not_on_kill_list = []):
    """This function has a dependency of win32api (which abaqus already has).
       To install, just use pip install pypiwin32"""
    if tasklistrl == None:
        tasklistrl = os.popen("tasklist").readlines()
    process_exists_forsure = False
    gotpid = False
    for examine in tasklistrl:
        if process == examine[0:len(process)]:
            process_exists_forsure = True
    if process_exists_forsure:
        print("That process exists.")
    else:
        print("That process does not exist.")
        # sys.exit()
    for getpid in tasklistrl:
        if process == getpid[0:len(process)]:
            pid = int(getpid[29:34])
            if pid not in not_on_kill_list:
                gotpid = True
                try:
                    handle = win32api.OpenProcess(1, False, pid)
                    win32api.TerminateProcess(handle, 0)
                    win32api.CloseHandle(handle)
                    print("Successfully killed process %s on pid %d." % (getpid[0:len(process)], pid))
                except win32api.error as err:
                    print(err)
                    # sys.exit()
    if not gotpid:
        print("Could not get process pid.")

def get_good_pids(process, tasklistrl=None):
    """This function has a dependency of win32api (which abaqus already has).
       To install, just use pip install pypiwin32"""
    if tasklistrl == None:
        tasklistrl = os.popen("tasklist").readlines()

    process_exists_forsure = False
    gotpid = False
    for examine in tasklistrl:
        if process == examine[0:len(process)]:
            process_exists_forsure = True
    if process_exists_forsure:
        print("That process exists.")
    else:
        print("That process does not exist.")
        # sys.exit()
    good_guys = [] 
    for getpid in tasklistrl:
        if process == getpid[0:len(process)]:
            pid = int(getpid[29:34])
            gotpid = True
            good_guys.append(pid)
    if not gotpid:
        print("Could not get process pid.")
    return good_guys

def run_abaqus():
    # Define work directory (currently uses the command line one)
    current_dir = os.path.dirname(os.path.realpath('__file__'))
    # Command to execute
    abaqus_script = 'AssemblyModifyEdit.py'
    # Directory where the new command line runs
    popen_dir = current_dir
    # Input file for Abaqus
    input_file = os.path.join(current_dir, 'input.txt')
    # Input file from matlab 
    input_mat = os.path.join(current_dir,'input.mat')
    # Output file from Abaqus
    output_file = os.path.join(current_dir, 'output.p')
    # Output file to matlab 
    output_mat = os.path.join(current_dir, 'output.mat')
    # Command to execute
    command = 'abq2018 cae nogui=' + abaqus_script
    # Time to wait for termination
    time_terminate = 1200.
    # Time increment for checking (if too small, will not work)
    increment_time=5.
    # delete previous input/output files
    # try:
        # os.remove(input_file)
    # except OSError:
        # pass
    try:
        os.remove(output_file)
    except OSError:
        pass
        
    # Creating input file
    inputs = scipy.io.loadmat(input_mat)
    print(inputs['x'])

    np.savetxt(input_file, inputs['x'], fmt='%f')
    
    # Check for executables that were running before so that
    # you do not kill another one by accident
    not_on_kill_list = get_good_pids('python.exe')
    
    # Run abaqus script
    ps = sp.Popen(command, cwd = popen_dir, shell=True)
    
    # Wait for termination
    terminated = enhanced_waitForCompletion(processes_to_track = ['python.exe'],
                                            processes_to_kill = ['python.exe', 'ABQcaeK.exe', 'abq2018.exe','pre.exe', 'standard.exe'],
                                            max_time=time_terminate, not_on_kill_list = not_on_kill_list,
                                            increment_time = increment_time)
    # If job is killed or if it did not converge, dummy outputs are generated
    if terminated:
        outputs = [1.0E10,-1.0E10,-1.0E10]
        fData=open('AssemblyOutput.txt', "a")
        fData.write(str(outputs[0])+','+str(-1.0)+','+str(outputs[1])+','+str(-1.0)+','+str(outputs[2])+'\n') #mass is sent in as negative to minimize in optimizer
        fData.close()
    else:
        try:
            outputs = pickle.load( open( output_file, "rb" ),encoding='latin1' ) #latin1 encoding needed for translation between python 3.X and 2.X
        except:
            outputs = [1.0E10,-1.0E10,-1.0E10] 
            fData=open('AssemblyOutput.txt', "a")
            fData.write(str(outputs[0])+','+str(-1.0)+','+str(outputs[1])+','+str(-1.0)+','+str(outputs[2])+'\n') #mass is sent in as negative to minimize in optimizer
            fData.close()
            
    scipy.io.savemat(output_mat, mdict={'outputs': outputs})
    # write a matlab .mat file for the outputs 
    
    return outputs

if __name__ == "__main__":
    outputs = run_abaqus()
    print(outputs)