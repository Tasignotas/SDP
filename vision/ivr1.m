% This line is a comment - you can leave out any of these lines 
% when copying this code to save time 
[x,y] = size(A);
% finds the dimensions of a matrix called A
if x > y 
   shape = 'thin'
else 
   shape = 'fat'
end
