program arrays;

var a : array[0..10] of integer;
var i, x, temp : integer;
var avg : real;

begin
    x := 10;
    avg := 0.0;
    // Example from http://www.tutorialspoint.com/pascal/pascal_arrays.htm
    for i := 0 to 10 do
        begin
              a[i] := i;
              avg := avg + a[i];
              //writeln(a[i]);
              writeln(avg);
        end;
        avg := avg / 11.0;
        writeln(avg);
end.
