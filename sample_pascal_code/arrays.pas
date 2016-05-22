program arrays;

var a : array[0..10] of integer;
var i, x, temp : integer;
var avg : real;

begin
    x := 10;
    avg := 0.0;
    // Example from http://www.tutorialspoint.com/pascal/pascal_arrays.htm
    writeln('The next loop will calculate the average of the array.');
    for i := 0 to 10 do
        begin
              a[i] := i;
              avg := avg + a[i];
              //writeln(a[i]);
              writeln(avg);
        end;

    avg := avg / 11.0;
    writeln(avg);
    writeln('The next prints will reverse the array.');
    for i := 0 to 5 do
        begin
            temp := a[i];
            a[i] := a[x];
            a[x] := temp;
            x := x - 1;
        end;

   for i := 0 to 10 do
        begin
            writeln(a[i]);
        end;
end.
