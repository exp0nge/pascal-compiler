program assignments;
var x, y : integer;
var hello : integer;
var aChar : char;
var aBool : boolean;
var aReal : real;

begin
    x := 20 + 20;
    y := (5 + 5) * 2;
    aBool := true;
    aChar := 'a';
    aReal := 1.64;
    writeln(x, x);
    writeln('(5 + 5) * 2 =', y);
    hello := 5 + 2 * 10 / 2 * 2 + 1 - 6;
    writeln('5 + 2 * 10 / 2 * 2 + 1 - 6 =', hello);
    writeln('this is a char:', aChar);
    writeln('this is a bool:', aBool);
    writeln('this is a real:', aReal);
end.
