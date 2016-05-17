program controlIf;
    var x, y, z : integer;
begin
    x := 10;
    y := 20;
    z := 99;
    if x > y then
        writeln(x)
        // the code below can be uncommented
//    else if x = 10 then
//        writeln(1)
    else
        writeln(z);
end.
