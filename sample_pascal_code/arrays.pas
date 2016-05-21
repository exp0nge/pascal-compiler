program arrays;

var a : array[0..10] of integer;
var i, x, temp : integer;
var avg : integer;

begin
    x := 10;
    avg := 0;
    // Example from http://www.tutorialspoint.com/pascal/pascal_arrays.htm
    for i := 0 to 10 do
        begin
              a[i] := i;
              avg := avg + a[i];
              //writeln(a[i]);
              writeln(avg);
        end;
 {*   for i := 0 to 10 do
        begin
            temp := a[i];
            a[i] := a[x];
            a[x] := temp;
            x := x - 1;
        end;
        *}
end.
