# Introduction

This project is a Java application that mimics the basic behavior of the Linux `grep` command. It recursively searches through files in a given root directory, reads each line, checks whether the line matches a user-provided regular expression, and writes all matched lines to an output file. The project was built using Core Java, regular expressions with `Pattern`, file I/O classes such as `BufferedReader` and `BufferedWriter`, SLF4J with Log4j for logging, Maven for dependency management, and IntelliJ IDEA for development and debugging.

# Quick Start

## Prerequisites
- Java 8 or higher
- Maven
- IntelliJ IDEA or terminal

## Compile the project
```bash
mvn clean compile
````

## Run the app in IntelliJ

Set these program arguments in the run configuration:

```bash
<regex> <rootPath> <outFile>
```

Example:

```bash
.*IllegalArgumentException.* ./src /tmp/grep.out
```

## Run from terminal

If using Maven and a proper exec plugin configuration:

```bash
mvn exec:java -Dexec.mainClass="ca.jrvs.apps.grep.JavaGrepImp" -Dexec.args=".*IllegalArgumentException.* ./src /tmp/grep.out"
```

## Expected behavior

* The app scans all files under the root directory
* It reads each file line by line
* It finds lines matching the regex
* It writes matched lines into the output file

# Implementation

## Pseudocode

`process()` method pseudocode:

```text
create an empty list called matchedLines
get all files recursively from rootPath

for each file in files
    read all lines from the file
    for each line in lines
        if line contains the regex pattern
            add line to matchedLines

write matchedLines to outFile
log total number of matched lines
```

## Performance Issue

The current implementation stores all matched lines in memory before writing them to the output file. This can become a problem when processing very large files or many files. A better solution would be to write matching lines directly to the output file as they are found, which would reduce memory usage significantly.

# Test

The application was tested manually by preparing sample input files inside a test directory and running the app with different regex patterns. After execution, the output file was checked to confirm that only matching lines were written. Different cases were tested, including valid matches, no matches, invalid directories, and invalid file paths. The results were compared with expected output to verify correctness.

# Deployment

This application can be dockerized for easier distribution by creating a Dockerfile that copies the compiled JAR file into a lightweight Java runtime image. The container can then run the app with command-line arguments for regex, root path, and output file. Docker makes it easier to run the application in a consistent environment without requiring users to manually install dependencies on their local machine.

# Improvement

1. Improve memory efficiency by writing matched lines directly to the output file instead of storing all matches in a list.
2. Compile the regex pattern once and reuse it, instead of recompiling it for every line.
3. Add automated unit tests and integration tests to improve reliability and make future changes easier to verify.


