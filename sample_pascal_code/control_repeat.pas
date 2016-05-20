program controlRepeat;
    var x, y : integer;
begin
    x := 0;
    y := 50;
    writeln(x);
    repeat
        x := x + 1;
        y := y + 100;
    until x >= 10;
    writeln(x);
    writeln(y);
end.
