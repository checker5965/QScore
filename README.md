# QScore
A multi-threaded socket program for professors which allows students to query their marks automatically.

This is a socket program which instructors can use to let registered students query their grades for a class.

The program works with CSV files and requires that you have the
files "grades.csv" and "login.csv" in the same directory as the server.

grades.csv should have first row as column names. An example file is attached. Format is -

Email,Assignment1,Assignment2,Assignment3
firstname.lastname_ug[year]@ashoka.edu.in,[Grade],[Grade],[Grade]



login.csv will start out empty but as and when users register into the system, values will be automatically added.

It will eventually look like -

firstname.lastname_ug[year]@ashoka.edu.in,[randomSalt][hashedPassword]


Use python3 to run the programs.
