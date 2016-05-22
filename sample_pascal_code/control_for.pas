program controlFor;
var
    x, y, z : integer;
begin
    y := 1;
    writeln('y is', y, 'before for-loop');
    // Example from http://www.tutorialspoint.com/pascal/pascal_for_do_loop.htm
    for x := 10 to 20 do
    begin
        y := y + 1;
        writeln('y + 1 =', y);
    end;
end.
