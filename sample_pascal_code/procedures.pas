program procedures;

var x : integer;

procedure minusOne;
    begin
    x := x - 1;
    end;

begin
    x := 99;
    minusOne;
    writeln(x);
end;