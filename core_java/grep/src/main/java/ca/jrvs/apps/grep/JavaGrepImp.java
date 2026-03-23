package ca.jrvs.apps.grep;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import org.apache.log4j.BasicConfigurator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JavaGrepImp implements JavaGrep {

  private static final Logger logger = LoggerFactory.getLogger(JavaGrepImp.class);

  private String regex;
  private String rootPath;
  private String outFile;

  public static void main(String[] args) {
    BasicConfigurator.configure();

    if (args.length != 3) {
      logger.error("Usage: JavaGrepImp <regex> <rootPath> <outFile>");
      return;
    }

    JavaGrepImp javaGrepImp = new JavaGrepImp();
    javaGrepImp.setRegex(args[0]);
    javaGrepImp.setRootPath(args[1]);
    javaGrepImp.setOutFile(args[2]);

    try {
      javaGrepImp.process();
    } catch (Exception e) {
      logger.error("Error: unable to process files", e);
    }
  }

  @Override
  public void process() throws IOException {
    Stream<String> matchedLines =
        listFiles(getRootPath())
            .flatMap(this::readLines)
            .filter(this::containsPattern);

    writeToFile(matchedLines);
    logger.info("Done.");
  }

  @Override
  public Stream<File> listFiles(String rootDir) {
    File rootFile = new File(rootDir);

    if (!rootFile.exists() || !rootFile.isDirectory()) {
      throw new IllegalArgumentException("Invalid root directory: " + rootDir);
    }

    List<File> files = new ArrayList<>();
    collectFiles(rootFile, files);
    return files.stream();
  }

  private void collectFiles(File file, List<File> files) {
    if (file.isFile()) {
      files.add(file);
      return;
    }

    File[] children = file.listFiles();
    if (children == null) {
      return;
    }

    for (File child : children) {
      collectFiles(child, files);
    }
  }

  @Override
  public Stream<String> readLines(File inputFile) {
    if (inputFile == null || !inputFile.isFile()) {
      throw new IllegalArgumentException("Invalid input file: " + inputFile);
    }

    List<String> lines = new ArrayList<>();

    try (BufferedReader reader =
        new BufferedReader(
            new InputStreamReader(new FileInputStream(inputFile), StandardCharsets.UTF_8))) {

      String line = reader.readLine();
      while (line != null) {
        lines.add(line);
        line = reader.readLine();
      }

    } catch (IOException e) {
      throw new RuntimeException("Failed to read file: " + inputFile.getAbsolutePath(), e);
    }

    return lines.stream();
  }

  @Override
  public boolean containsPattern(String line) {
    if (line == null) {
      return false;
    }
    return Pattern.compile(getRegex()).matcher(line).find();
  }

  @Override
  public void writeToFile(Stream<String> lines) throws IOException {
    File outputFile = new File(getOutFile());
    File parent = outputFile.getParentFile();

    if (parent != null && !parent.exists()) {
      parent.mkdirs();
    }

    try (BufferedWriter writer =
        new BufferedWriter(
            new OutputStreamWriter(new FileOutputStream(outputFile), StandardCharsets.UTF_8))) {

      lines.forEach(line -> {
        try {
          writer.write(line);
          writer.newLine();
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      });
    }
  }

  @Override
  public String getRootPath() {
    return rootPath;
  }

  @Override
  public void setRootPath(String rootPath) {
    this.rootPath = rootPath;
  }

  @Override
  public String getRegex() {
    return regex;
  }

  @Override
  public void setRegex(String regex) {
    this.regex = regex;
  }

  @Override
  public String getOutFile() {
    return outFile;
  }

  @Override
  public void setOutFile(String outFile) {
    this.outFile = outFile;
  }
}