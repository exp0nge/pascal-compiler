program controlFor;
var
    x, y, z : integer;
begin
    y := 1;
    // Example from http://www.tutorialspoint.com/pascal/pascal_for_do_loop.htm
    for x := 10 to 20 do
    begin
        writeln(y);
        y := y + 1;
    end;
end.
