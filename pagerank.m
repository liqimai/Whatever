load graph.txt;
[~,n] = size(graph);
add = ones(1,n);
mul = zeros(n,n);
Im = zeros(n,n);
outdegree = add*graph;
d = 0.5;
for i = 1:n
    o = outdegree(i);
    if(o>0)
        mul(i,i) = 1/outdegree(i);
    end
    Im(i,i) = 1;
end

A = Im-graph*mul.*0.85;
b = ones(n,1)*(1-d)/n;
[x,flag,relres,iter,resverc]=bicg(A,b,1e-11);
disp(x);