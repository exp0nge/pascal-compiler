program caseStatement;
var
    grade: char;
begin
    // Example from: http://www.tutorialspoint.com/pascal/pascal_case_statement.htm
    grade := 'A';

    case (grade) of
    'A': writeln(100);
    'B': writeln(85);
    'C': writeln(75);
    'D': writeln(60);
    'F': writeln(0);
    end;
end.