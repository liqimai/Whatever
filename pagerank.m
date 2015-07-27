file = fopen('graph.txt','r');
n = textscan(file,'%d',1);
n = n{1};
graph = zeros(n,n);
while ~feof(file)
    i = textscan(file,'%d',1);
    i = i{1};
    j = textscan(file,'%d',1);
    j = j{1};
    graph(i+1,j+1) = 1;
end
fclose(file);
disp('Finish loading graph')
add = ones(1,n);
tmp = zeros(n,n);
outdegree = add*graph;
d = 0.85;
disp('Generating mul...');
for i = 1:n
    o = outdegree(i);
    if(o>0)
        tmp(i,i) = 1/outdegree(i);
    end
end

graph = graph*tmp.*(-d);
disp('Generating A...');
for i = 1:n
    graph(i,i)=graph(i,i) + 1;
end
b = ones(n,1).*((1-d)/double(n));
disp('Start calculating');
[x,flag,relres,iter,resverc]=bicg(graph,b,1e-11);
disp('Finish');

file = fopen('pagerank','w');
for i = 1:n
    fprintf(file,'%.4e\n',x(i,1));
end
fclose(file);
