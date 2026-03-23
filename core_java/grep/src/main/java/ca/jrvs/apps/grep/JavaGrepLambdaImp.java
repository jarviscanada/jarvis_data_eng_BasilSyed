package ca.jrvs.apps.grep;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import org.apache.log4j.BasicConfigurator;

/**
 * StreamAPI implementation of the GREP app.
 */
public class JavaGrepLambdaImp extends JavaGrepImp {

  public static void main(String[] args) {

    BasicConfigurator.configure();

    if (args.length != 3) {
      throw new IllegalArgumentException("Usage: JavaGrepLambdaImp <regex> <rootPath> <outFile>");
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
  public Stream<String> readLines(File inputFile) {
    if (inputFile == null || !inputFile.isFile()) {
      throw new IllegalArgumentException("Invalid input file: " + inputFile);
    }

    try {
      BufferedReader reader =
          new BufferedReader(
              new InputStreamReader(new FileInputStream(inputFile), StandardCharsets.UTF_8));

      return reader.lines().onClose(() -> {
        try {
          reader.close();
        } catch (IOException e) {
          throw new UncheckedIOException(e);
        }
      });

    } catch (IOException e) {
      throw new RuntimeException("Failed to read file: " + inputFile.getAbsolutePath(), e);
    }
  }

  @Override
  public Stream<File> listFiles(String rootDir) {
    File rootFile = new File(rootDir);

    if (!rootFile.exists() || !rootFile.isDirectory()) {
      throw new IllegalArgumentException("Invalid root directory: " + rootDir);
    }

    try {
      return Files.walk(rootFile.toPath())
          .filter(Files::isRegularFile)
          .map(Path::toFile);
    } catch (IOException e) {
      throw new RuntimeException("Failed to list files under: " + rootDir, e);
    }
  }

}
