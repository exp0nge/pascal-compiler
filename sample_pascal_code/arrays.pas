program arrays;

var a : array[0..10] of integer;
var i : integer;

begin

    // Example from http://www.tutorialspoint.com/pascal/pascal_arrays.htm
    for i := 0 to 10 do
        begin
            writeln(a[i]);
        end;
end.
