program caseStatement;
var
    grade: char;
begin
    // Example from: http://www.tutorialspoint.com/pascal/pascal_case_statement.htm
    grade := 'A';

    case (grade) of
    'A' : writeln('Excellent!' );
    'B', 'C': writeln('Well done' );
    'D' : writeln('You passed' );
    'F' : writeln('Better try again' );
    end;

    writeln('Your grade is  ', grade );
end.