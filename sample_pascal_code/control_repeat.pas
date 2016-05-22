program controlRepeat;
    var x, y : integer;
begin
    x := 0;
    y := 50;
    writeln('value of x before repeat-statement:', x);
    writeln('value of y before repeat-statement:', y);
    repeat
        x := x + 1;
        y := y + 100;
    until x >= 10;
    writeln('value of x after repeat-statement:', x);
    writeln('value of y after repeat-statement:', y);
end.
