package ca.jrvs.apps.grep;

import java.util.Arrays;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.DoubleStream;
import java.util.stream.IntStream;
import java.util.stream.Stream;

/**
 * Concrete implementation of LSE interface.
 */
public class LambdaStreamApi implements LambdaStreamExec {

  @Override
  public Stream<String> createStrStream(String... strings) {
    return Arrays.stream(strings);
  }

  @Override
  public Stream<String> toUpperCase(String... strings) {

    return createStrStream(strings)
        .map(String::toUpperCase);

  }

  @Override
  public Stream<String> filter(Stream<String> stringStream, String pattern) {
    return stringStream.filter(s -> !s.contains(pattern));
  }

  @Override
  public <E> List<E> toList(Stream<E> stream) {
    return stream.toList();
  }

  @Override
  public List<Integer> toList(IntStream intStream) {
    return intStream.boxed().toList();
  }

  @Override
  public IntStream createIntStream(int[] arr) {
    return Arrays.stream(arr);
  }

  @Override
  public IntStream createIntStream(int start, int end) {
    return IntStream.range(start, end);
  }

  @Override
  public DoubleStream squareRootIntStream(IntStream intStream) {
    return intStream
        .mapToDouble(x -> Math.sqrt(x));
  }

  @Override
  public IntStream getOdd(IntStream intStream) {
    return intStream
        .filter(x -> x % 2 != 0);
  }

  @Override
  public Consumer<String> getLambdaPrinter(String prefix, String suffix) {
    return message -> System.out.println(prefix + message + suffix);
  }

  @Override
  public void printMessages(String[] messages, Consumer<String> printer) {
    Arrays.stream(messages).forEach(printer);
  }

  @Override
  public void printOdd(IntStream intStream, Consumer<String> printer) {
    intStream
        .filter(i -> i % 2 != 0)
        .mapToObj(i -> String.valueOf(i))
        .forEach(printer);
  }

  @Override
  public Stream<Integer> flatNestedInt(Stream<List<Integer>> ints) {
    return ints.flatMap(list -> list.stream())
        .map(x -> x * x);
  }
}
