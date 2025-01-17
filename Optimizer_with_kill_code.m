global indNum


%status1 = system('abaqus cae script=Assembly.py');
indNum = 0;
writeFile = 'PlottingInfo.txt';
% if isfile(writeFile)%s.bytes == 0
optOutput = fopen(writeFile,'w');
fprintf(optOutput,"Ind#;Desired DVs;Actual DVs;Perf. Metrics\r\n");
fclose(optOutput);
% end
writeFile2 = 'AssemblyOutput.txt';
% if ~isfile(writeFile2)%s.bytes == 0
assemblyOutput = fopen(writeFile2,'w');
fprintf(assemblyOutput,"Assembly k_xy, Max mises 1, Assembly k_theta, Max mises 2, Mass\r\n");
fclose(assemblyOutput);

assemblyOutFile = dir(strcat(pwd,'/','AssemblyOutput.txt'));
assemblyOutSize = assemblyOutFile.bytes;
% end
formatSpec = "\r\n%i;";

% CHANGE VALUES BELOW ##############

numOfSubstructures = 64; %Manually input for number of iterations
numOfVars = 3;% same

plotfn = @(options,state,flag)gaplotpareto(options,state,flag,[1 2 3]);
plotfn2 = @(options,state,flag)gaplotpareto(options,state,flag,[1 2]);
plotfn3 = @(options,state,flag)gaplotpareto(options,state,flag,[1 3]);
plotfn4 = @(options,state,flag)gaplotpareto(options,state,flag,[2 3]);
% options2 = gaoptimset('MaxGenerations',2,'PopulationSize',2,'PlotFcns',plotfn);
options = optimoptions(@gamultiobj,'MaxGenerations',50,'PopulationSize',250,...
                    'PlotFcn',{plotfn,plotfn2,plotfn3,plotfn4,@gaplotscorediversity},...
                    'OutputFcn',@myoutput);%,'OutputFcn',@indNumPrint);
                
% Restart options below
%load('population.mat','restart_population');
%options = optimoptions(@gamultiobj,'MaxGenerations',10,'PopulationSize',100,...
%                     'PlotFcn',{plotfn,plotfn2,plotfn3,plotfn4,@gaplotscorediversity},...
%                     'OutputFcn',@myoutput,'InitialPopulation',restart_population);
% options2 = optimoptions(@gamultiobj,'InitialPop',final_pop,'MaxGenerations',100,'PopulationSize',100,'PlotFcn',{plotfn,plotfn2,plotfn3,plotfn4,@gaplotscorediversity});%,'OutputFcn',@indNumPrint);

n = numOfSubstructures*numOfVars;

[x,fval,exitflag,output,population]=gamultiobj(@evaluation_function,n,[],[],[],[],zeros(n,1),ones(n,1),options);



% [x,fval,exitflag,output,final_pop2]=gamultiobj(@objective,n,[],[],[],[],zeros(n,1),ones(n,1),options2);



function obj = evaluation_function(x)
%     disp(x)
    global indNum

    indNum = indNum + 1;
    formatSpec = "\r\n%i;";
    %write individual number to Plotting info text file
    writeFile = 'PlottingInfo.txt';
    plotInfo = fopen(writeFile,'a');
    fprintf(plotInfo,formatSpec,indNum);
    fclose(plotInfo);

    
    % write .mat file for python input 
    save('input.mat','x')
    %run assembly code which should write perf. metrics to "AssemblyOutput.txt"
    status2 = system('python kill_code.py')

    % read in performance metrics from python-generated .mat file
    load('output.mat');
    disp(outputs)
    obj = -outputs;
    
end


function [state,options,optchanged] = myoutput(options,state,flag) 
         restart_population = state.Population ; %get current population
         save('population.mat','restart_population')
         optchanged = false;
     end