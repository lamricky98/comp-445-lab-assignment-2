# Comp 445 Lab Assignment 2
### By Ricky Lam 40089502

GitHub repo URL: https://github.com/lamricky98/comp-445-lab-assignment-2

# Description

This project is an HTTP server library that supports the following features:
1. GET operation: prints all files in directory if no directory is specified, otherwise reads file requested and returns in the response's body
2. POST operation: creates a file in the specified directory with the specified file name with the specified data in the request
3 Body of the response

A cURL-like command line program with basic functionalities is built on top of the HTTP library mentioned above.
See usage below for examples.

# Requirements
1. Python 3+

# Usage

- Download all files in the repository
- Open a terminal (shell, command prompt, etc...) in the directory of the .py files
- In the terminal, enter the following command and its options:

python httpfs.py [-v] [-p PORT] [-d PATH-TO-DIR]

- To get more detailed information on each argument, run "python httpfs.py --help"
- This program is best utilized with an HTTP client such as cURL or the one found here https://github.com/lamricky98/comp-445-lab-assignment-1
- If using the latter, there is a bash shell file with a list of commands that can be used to test this server application. It is called test_cases_for_a2.sh ; Have the server up and running and then execute the bash shell file. The results will be displayed inside the shell console.


