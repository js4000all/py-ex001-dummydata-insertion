import itertools as it
import typing as ty

T=ty.TypeVar('T')

def chunked(iterable: ty.Iterable[T], n: int) -> ty.Iterator[ty.Sequence[T]]:
    """
    Splits an iterable into chunks of a specified size.
    :param iterable: The iterable to be split into chunks.
    :type iterable: Iterable[T]
    :param n: The size of each chunk.
    :type n: int
    :return: An iterator of iterators, where each inner iterator represents a chunk of the original iterable.
    :rtype: Iterator[Iterator[T]]
    """
    iterator = iter(iterable)
    return iter(lambda: list(it.islice(iterator, n)), [])


def merged_sequences(sequences: ty.Dict[T, ty.Iterator[ty.Any]], max_reads: int) -> ty.Iterator[ty.Tuple[T, ty.Any]]:
    """
    Merges multiple sequences into a single iterator, yielding elements from each sequence in a round-robin fashion.
    :param sequences: A dictionary where keys are identifiers for the sequences and values are iterators of the sequences.
    :type sequences: Dict[T, Iterator[Any]]
    :param max_reads: The maximum number of elements to read from all sequences combined.
    :type max_reads: int
    :return: An iterator that yields tuples containing the key of the sequence and the next element from that sequence.
    :rtype: Iterator[Tuple[T, Any]]
    This function iterates over the provided sequences in a round-robin manner, yielding elements from each sequence
    until all sequences are exhausted or the maximum number of reads is reached. If a sequence is exhausted before
    reaching the maximum number of reads, it is removed from the active sequences.
    """
    
    active_sequences = {k: iter(sequences[k]) for k in sequences}  # アクティブな数列

    for _ in range(max_reads):  # 全数列の最大読み込み回数
        for key in list(active_sequences.keys()):  # 動的に数列管理
            try:
                yield (key, next(active_sequences[key]))
            except StopIteration:
                del active_sequences[key]  # 数列が尽きたら削除

        if not active_sequences:  # すべての数列が尽きたら終了
            break
