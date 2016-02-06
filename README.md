Rinter is a utility to check for formatting heresy, as defined by the High
Priest of the Eighth Day of our Lord.

Among the items checked by rinter:

    * File contains header with name, section, assignment #, due date,
      and total points.
    * Comments are present before each function, and do not occur in the
      body of a function.
    * All lines are under 80 characters long.
    * Function prototypes occur only inside of functions, and not in global
      scope.
    * No function is more than 25 lines in length.
    * Two blank lines before each function.
    * Indentation level of 3 spaces
    * Alphabetic declaration of variables
    * No mixing of case in variables and constants
    * Constants defined all upper case.

Usage:
    rinter -f <filename>
