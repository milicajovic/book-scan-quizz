from typing import Generator


def filter_feedback_stream(stream: Generator[str, None, None]) -> Generator[str, None, None]:
    """
    Filters the feedback stream, removing '###' and everything after it,
    even when '###' is split across multiple chunks.

    Args:
    stream (Generator[str, None, None]): The original stream of feedback chunks.

    Yields:
    str: Filtered chunks of feedback.
    """
    buffer = ""
    for chunk in stream:
        buffer += chunk
        while buffer:
            if '###' in buffer:
                separator_index = buffer.index('###')
                yield buffer[:separator_index]
                # Consume the rest of the stream without yielding
                for _ in stream:
                    pass
                return
            elif buffer.endswith('#') or buffer.endswith('##'):
                # Potential start of separator, keep in buffer
                break
            else:
                # No potential separator, yield entire buffer
                yield buffer
                buffer = ""

    # If we've reached here, '###' was never found
    if buffer:
        yield buffer