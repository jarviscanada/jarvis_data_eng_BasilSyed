package ca.jrvs.apps.grep;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

/**
 * StreamAPI implementation of the GREP app.
 */
public class JavaGrepLambdaImp extends JavaGrepImp {

  public static void main(String[] args) {

    if (args.length != 3) {
      throw new IllegalArgumentException("Usage: JavaGrepImp <regex> <rootPath> <outFile>");
    }

    JavaGrepLambdaImp javaGrepLambdaImp = new JavaGrepLambdaImp();
    javaGrepLambdaImp.setRegex(args[0]);
    javaGrepLambdaImp.setRootPath(args[1]);
    javaGrepLambdaImp.setOutFile(args[2]);

    try {
      javaGrepLambdaImp.process();
    } catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  @Override
  public List<String> readLines(File inputFile) {
    if (inputFile == null || !inputFile.isFile()) {
      throw new IllegalArgumentException("Invalid input file: " + inputFile);
    }

    try (BufferedReader reader =
        new BufferedReader(
            new InputStreamReader(new FileInputStream(inputFile), StandardCharsets.UTF_8))) {

      return reader.lines().toList();

    } catch (IOException e) {
      throw new RuntimeException("Failed to read file: " + inputFile.getAbsolutePath(), e);
    }
  }

  @Override
  public List<File> listFiles(String rootDir) {
    File rootFile = new File(rootDir);

    if (!rootFile.exists() || !rootFile.isDirectory()) {
      throw new IllegalArgumentException("Invalid root directory: " + rootDir);
    }

    try (Stream<Path> paths = Files.walk(rootFile.toPath())) {
      return paths
          .filter(Files::isRegularFile)
          .map(Path::toFile)
          .toList();
    } catch (IOException e) {
      throw new RuntimeException("Failed to list files under: " + rootDir, e);
    }
  }

}
