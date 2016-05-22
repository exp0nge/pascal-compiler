program caseStatement;
var
    grade: char;
begin
    // Example from: http://www.tutorialspoint.com/pascal/pascal_case_statement.htm
    grade := 'A';

    case (grade) of
    'A': writeln('your grade is', 100);
    'B': writeln('your grade is', 85);
    'C': writeln('your grade is', 75);
    'D': writeln('your grade is', 60);
    'F': writeln('your grade is', 0);
    end;
end.