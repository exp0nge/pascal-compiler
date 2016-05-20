program controlWhile;
    var x, y : integer;
begin
    x := 0;
    writeln(x);
    while x < 10 do
        begin
            writeln(x);
            x := x + 3;
        end;
    writeln(x);
end.
